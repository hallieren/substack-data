#!/usr/bin/env python
"""accept -- pico-009 / django__django-15098.

Issue (the ONLY verdict source, policy P1): "Internationalisation didn't
support language locale containing both script and region.  The i18n_patterns
didn't work with locale contains both script and region, like en-latn-us."
With

    LANGUAGE_CODE = 'en-us'
    LANGUAGES = [('en-us', "English"),
                 ('en-latn-us', "Latin English"),
                 ('en-Latn-US', "BCP 47 case format")]
    MIDDLEWARE += ['django.middleware.locale.LocaleMiddleware']
    urlpatterns += i18n_patterns(path('', bangiah))

the reporter sees /en-us/ -> 200 "U!" but /en-latn-us/ -> 404, and asks for
200 "U!" on the script+region tag.  The issue also quotes RFC 5646 for the
general shape (language ["-" script] ["-" region] ...), so this script checks
a second, non-English language pair as well.

This rebuilds that project (settings + urlconf) and drives it with
django.test.Client.

Note on the mixed-case tag: Django canonicalises the *active* language tag to
lower case, and the issue itself notes "the language part is always in
lowercase", so /en-Latn-US/ is reported as context rather than gated on.

Exit codes (harness contract): 0 = accepted, 1 = not met, 2 = probe broken.
"""

import os
import sys
import traceback

URLCONF_NAME = "pico009_urls"
URLCONF_DIR = "/tmp"
URLCONF_SRC = r'''
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse
from django.urls import path


def bangiah(request):
    return HttpResponse("U!")


urlpatterns = []
urlpatterns += i18n_patterns(
    path("", bangiah),
)
'''


def main():
    urlconf_path = os.path.join(URLCONF_DIR, URLCONF_NAME + ".py")
    f = open(urlconf_path, "w")
    try:
        f.write(URLCONF_SRC)
    finally:
        f.close()
    if URLCONF_DIR not in sys.path:
        sys.path.insert(0, URLCONF_DIR)

    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=False,
            SECRET_KEY="pico009",
            ALLOWED_HOSTS=["*"],
            ROOT_URLCONF=URLCONF_NAME,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[],
            MIDDLEWARE=["django.middleware.locale.LocaleMiddleware"],
            TEMPLATES=[],
            USE_I18N=True,
            USE_TZ=False,
            LANGUAGE_CODE="en-us",
            LANGUAGES=[
                ("en-us", "English"),
                ("en-latn-us", "Latin English"),
                ("en-Latn-US", "BCP 47 case format"),
                # same shape, different language: guards against a fix that
                # only special-cases the tags spelled out in the issue
                ("de-de", "German"),
                ("de-latn-de", "Latin German"),
            ],
            DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        )
    django.setup()

    from django.test.client import Client

    client = Client()
    failures = []

    gated = [
        # (label, url) -- each must answer 200 b"U!"
        ("language-region", "/en-us/"),          # already works; must not break
        ("language-script-region", "/en-latn-us/"),
        ("language-script-region-other-language", "/de-latn-de/"),
    ]
    for label, url in gated:
        response = client.get(url)
        status = response.status_code
        try:
            body = response.content
        except Exception:
            body = b""
        ok = status == 200 and body == b"U!"
        print(
            "probe %s: GET %s -> %s %r (want 200 b'U!') :: %s"
            % (label, url, status, body[:40], "ok" if ok else "MISMATCH")
        )
        if not ok:
            failures.append("GET %s returned %s %r" % (url, status, body[:40]))

    # context only (not gated): the mixed-case spelling of the same tag, and
    # what the path-based language detection extracts.
    try:
        response = client.get("/en-Latn-US/")
        print(
            "context: GET /en-Latn-US/ -> %s %r (mixed-case spelling of the same "
            "tag; Django lower-cases the active tag, so this is reported, not gated)"
            % (response.status_code, response.content[:40])
        )
    except Exception as exc:
        print("context: GET /en-Latn-US/ raised %s: %s" % (type(exc).__name__, exc))

    try:
        from django.utils.translation import get_language_from_path

        print(
            "context: get_language_from_path -> /en-us/=%r /en-latn-us/=%r "
            "/de-latn-de/=%r /en-Latn-US/=%r"
            % (
                get_language_from_path("/en-us/"),
                get_language_from_path("/en-latn-us/"),
                get_language_from_path("/de-latn-de/"),
                get_language_from_path("/en-Latn-US/"),
            )
        )
    except Exception as exc:
        print(
            "context: get_language_from_path unavailable (%s: %s)"
            % (type(exc).__name__, exc)
        )

    if failures:
        print("ACCEPT: not met -- " + "; ".join(failures))
        return 1
    print(
        "ACCEPT: met -- i18n_patterns serves language tags that carry both a "
        "script and a region subtag"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        print("ACCEPT: probe broken")
        sys.exit(2)

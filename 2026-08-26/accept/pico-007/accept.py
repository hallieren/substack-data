#!/usr/bin/env python
"""accept -- pico-007 / django__django-11477.

Issue (the ONLY verdict source, policy P1):

    translate_url() creates an incorrect URL when optional named groups are
    missing in the URL pattern
    There is a problem when translating urls with absent 'optional' arguments

So: build a url pattern that HAS an optional named group, request the variant
of the url where that group is ABSENT, and translate it to another language.
translate_url() must produce the same url under the new language prefix -- it
must not invent a value for the missing optional group.  The variant where the
group is PRESENT must keep working too.

Exit codes (harness contract): 0 = accepted, 1 = not met, 2 = probe broken.
"""

import os
import sys
import traceback

URLCONF_NAME = "pico007_urls"
URLCONF_DIR = "/tmp"
URLCONF_SRC = r'''
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse

try:
    from django.urls import re_path
except ImportError:  # Django < 2.0
    from django.conf.urls import url as re_path


def view(request, *args, **kwargs):
    return HttpResponse("ok")


urlpatterns = i18n_patterns(
    # one optional named group; "/<lang>/opt/" is the "absent" variant
    re_path(r"^opt/(?P<arg>[\w-]+)?$", view, name="pico007-opt"),
    # control: same shape, no optional group at all
    re_path(r"^plain/$", view, name="pico007-plain"),
)
'''


def main():
    path = os.path.join(URLCONF_DIR, URLCONF_NAME + ".py")
    f = open(path, "w")
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
            SECRET_KEY="pico007",
            ALLOWED_HOSTS=["*"],
            ROOT_URLCONF=URLCONF_NAME,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[],
            MIDDLEWARE=[],
            TEMPLATES=[],
            USE_I18N=True,
            USE_TZ=False,
            LANGUAGE_CODE="en",
            LANGUAGES=[("en", "English"), ("nl", "Dutch")],
            DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        )
    django.setup()

    from django.urls import resolve, translate_url
    from django.utils import translation

    translation.activate("en")

    failures = []

    # context only (not a gate): what the resolver hands translate_url() for
    # the url whose optional group is absent.
    try:
        match = resolve("/en/opt/")
        print(
            "context: resolve('/en/opt/') -> url_name=%r args=%r kwargs=%r"
            % (match.url_name, tuple(match.args), dict(match.kwargs))
        )
    except Exception as exc:  # resolving must at least work
        print("context: resolve('/en/opt/') raised %s: %s" % (type(exc).__name__, exc))
        failures.append("the optional-group url does not even resolve")

    checks = [
        # (label, input url, target language, expected output)
        ("optional-group-absent", "/en/opt/", "nl", "/nl/opt/"),
        ("optional-group-present", "/en/opt/foo", "nl", "/nl/opt/foo"),
        ("no-optional-group", "/en/plain/", "nl", "/nl/plain/"),
    ]
    for label, url, lang, expected in checks:
        got = translate_url(url, lang)
        ok = got == expected
        print(
            "probe %s: translate_url(%r, %r) -> %r (want %r) :: %s"
            % (label, url, lang, got, expected, "ok" if ok else "MISMATCH")
        )
        if not ok:
            failures.append(
                "translate_url(%r, %r) returned %r, expected %r" % (url, lang, got, expected)
            )

    # the reverse direction of the same absent-optional-group url.  resolve()
    # only strips the '/nl/' prefix while 'nl' is the active language, so
    # activate it for this probe and put 'en' back afterwards.
    translation.activate("nl")
    try:
        got_back = translate_url("/nl/opt/", "en")
    finally:
        translation.activate("en")
    ok_back = got_back == "/en/opt/"
    print(
        "probe optional-group-absent-reverse: translate_url('/nl/opt/', 'en') -> "
        "%r (want '/en/opt/') :: %s" % (got_back, "ok" if ok_back else "MISMATCH")
    )
    if not ok_back:
        failures.append(
            "translate_url('/nl/opt/', 'en') returned %r, expected '/en/opt/'" % (got_back,)
        )

    if failures:
        print("ACCEPT: not met -- " + "; ".join(failures))
        return 1
    print("ACCEPT: met -- translate_url() keeps urls whose optional named "
          "groups are absent intact across languages")
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

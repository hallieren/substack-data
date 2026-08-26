"""accept — pico-017 (django__django-10999)

Verdict source: issues/pico-017.md ONLY (policy P1). The issue states that
standard_duration_re "doesn't match to negative durations, because of the
<hours> definition final (lookahead) part does not have '-?' in it", and gives
the intended pattern `((?:(?P<hours>-?\\d+):)(?=-?\\d+:-?\\d+))?`. So a
duration string whose minutes/seconds carry a '-' must parse, with each
component keeping its own sign, and the durations that already parsed must
keep parsing. Nothing here comes from the maintainer's patch or from any
hidden test; the pinned test file is never read or touched.

Exit: 0 all probes pass · 1 some probe failed · 2 probe broken.
"""

import sys
import traceback
from datetime import timedelta

RESULTS = []


def report(label, ok, observed):
    RESULTS.append(bool(ok))
    print("[%s] %s | %s" % ("PASS" if ok else "FAIL", label, observed))


def main():
    from django.utils.dateparse import parse_duration

    def check(label, source, expected):
        try:
            got = parse_duration(source)
        except Exception as exc:
            report(label, False,
                   "parse_duration(%r) raised %s: %s" % (source, type(exc).__name__, exc))
            return
        report(label, got == expected,
               "parse_duration(%r) -> %r (expected %r)" % (source, got, expected))

    # 1-3. The negative durations the issue says must match. Under the pattern
    #      the issue prescribes, every component keeps its own sign.
    check("negative hours/minutes/seconds parse",
          "-1:-2:-3", timedelta(hours=-1, minutes=-2, seconds=-3))
    check("positive hours with negative minutes/seconds parse",
          "1:-2:-3", timedelta(hours=1, minutes=-2, seconds=-3))
    check("negative days with a negative time part parse",
          "-1 -1:-2:-3", timedelta(days=-1) + timedelta(hours=-1, minutes=-2, seconds=-3))

    # 4-6. Durations that already parsed must be unchanged by the fix.
    check("plain seconds still parse", "30", timedelta(seconds=30))
    check("minutes:seconds still parse", "15:30", timedelta(minutes=15, seconds=30))
    check("hours:minutes:seconds still parse", "10:15:30",
          timedelta(hours=10, minutes=15, seconds=30))
    check("days with a time part still parse", "4 15:30",
          timedelta(days=4, minutes=15, seconds=30))

    # 7. Garbage must still be rejected (the looser lookahead must not swallow it).
    try:
        got = parse_duration("not a duration")
        report("non-durations still return None", got is None,
               "parse_duration('not a duration') -> %r" % (got,))
    except Exception as exc:
        report("non-durations still return None", False,
               "parse_duration('not a duration') raised %s: %s" % (type(exc).__name__, exc))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print("[BROKEN] accept probe could not run to completion")
        sys.exit(2)
    ok = bool(RESULTS) and all(RESULTS)
    print("accept: %d/%d probes passed" % (sum(1 for r in RESULTS if r), len(RESULTS)))
    sys.exit(0 if ok else 1)

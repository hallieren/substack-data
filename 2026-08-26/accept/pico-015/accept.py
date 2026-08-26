#!/usr/bin/env python
"""accept probe -- pico-015 (world matplotlib__matplotlib-26208)

Verdict source (policy P1): issues/pico-015.md ONLY.

The issue: with a stackplot on ax1 and a twinx() second axes, ax1's dataLim is
replaced by [inf, -inf] as soon as something is plotted on ax2.  The issue's own
reproduction, its "Actual outcome" print-out and its "Expected outcome" ("To not
change ax1 dataLims, since I made no changes to it") are the whole spec:

    ax1.stackplot(...)                 -> ax1.dataLim.intervaly [-22.71770833 26.585]
    ax2 = ax1.twinx()                  -> ax1 still [-22.71770833 26.585]
    ax2.plot(...)                      -> ax1 becomes [inf -inf]   <-- the bug
                                          ax2 is [-2.983302 -0.085014]

The issue also records, under "Additional information", that the mirror-image
order (plot on ax1, stackplot on ax2) already behaves; that is probed as a guard
so a fix cannot buy ax1 back by breaking the direction that already worked.

Exit codes: 0 = acceptance met, 1 = not met, 2 = probe broken.
"""

import sys
import traceback

import numpy as np

# Verbatim from the issue's reproduction snippet.
DF1_INDEX = ["16 May", "17 May"]
DF1_VALUES = [-22.717708333333402, 26.584999999999937]
DF2_VALUES = [-0.08501399999999998, -2.9833019999999966]

# The issue's own "Actual outcome" print-out, first line: what ax1 must keep.
AX1_EXPECTED = (-22.717708333333402, 26.584999999999937)
# ... third line: what ax2 legitimately ends up with.
AX2_EXPECTED = (-2.9833019999999966, -0.08501399999999998)


def _intervaly(ax):
    return np.array(ax.dataLim.intervaly, dtype=float)


def _finite(arr):
    return bool(np.all(np.isfinite(np.asarray(arr, dtype=float))))


def _matches(got, expected, rtol=1e-6, atol=1e-9):
    got = np.asarray(got, dtype=float)
    if not _finite(got):
        return False
    return bool(np.allclose(np.sort(got),
                            np.sort(np.asarray(expected, dtype=float)),
                            rtol=rtol, atol=atol))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    results = []

    # --- the issue's reproduction, verbatim ---------------------------------
    repro_error = None
    after_stack = after_twinx = after_plot = ax2_after_plot = None
    try:
        fig, ax1 = plt.subplots()
        ax1.stackplot(DF1_INDEX, DF1_VALUES)
        after_stack = _intervaly(ax1)

        ax2 = ax1.twinx()
        after_twinx = _intervaly(ax1)

        ax2.plot(DF1_INDEX, DF2_VALUES)
        after_plot = _intervaly(ax1)
        ax2_after_plot = _intervaly(ax2)
        plt.close(fig)
    except Exception as exc:
        repro_error = "%s: %s" % (type(exc).__name__, exc)

    def report(n, name, got, expected, what):
        if repro_error is not None:
            print("[probe %s %s] the issue's reproduction raised %s before this "
                  "point; %s -> FAIL" % (n, name, repro_error, what))
            return False
        ok = _matches(got, expected)
        print("[probe %s %s] %s; observed %r -> %s"
              % (n, name, what, got.tolist(), "PASS" if ok else "FAIL"))
        return ok

    # ---- probe 1: the issue's stated starting point still holds ------------
    results.append(report(
        "1/5", "baseline",
        after_stack, AX1_EXPECTED,
        "after ax1.stackplot(df1_index, df1_values), the issue's own output "
        "records ax1.dataLim.intervaly == [-22.71770833 26.585]"))

    # ---- probe 2: twinx() alone must not touch ax1 -------------------------
    results.append(report(
        "2/5", "after twinx",
        after_twinx, AX1_EXPECTED,
        "after ax2 = ax1.twinx(), ax1.dataLim.intervaly must be unchanged and "
        "finite ([-22.71770833 26.585])"))

    # ---- probe 3: THE BUG -- plotting on ax2 must not destroy ax1 ----------
    results.append(report(
        "3/5", "after ax2.plot",
        after_plot, AX1_EXPECTED,
        "after ax2.plot(df1_index, df2_values), the bug report shows ax1 turned "
        "into [inf -inf] while the expected outcome is an unchanged, finite "
        "[-22.71770833 26.585]"))

    # ---- probe 4: ax2's own dataLim is still the one the issue reports -----
    results.append(report(
        "4/5", "ax2 intact",
        ax2_after_plot, AX2_EXPECTED,
        "after ax2.plot(...), the issue's output records ax2.dataLim.intervaly "
        "== [-2.983302 -0.085014] and that part is not being complained about"))

    # ---- probe 5: the order the issue says already works, still works ------
    try:
        fig, bx1 = plt.subplots()
        bx1.plot(DF1_INDEX, DF1_VALUES)
        bx2 = bx1.twinx()
        bx2.stackplot(DF1_INDEX, DF2_VALUES)
        swapped_ax1 = _intervaly(bx1)
        swapped_ax2 = _intervaly(bx2)
        plt.close(fig)
        ok = _matches(swapped_ax1, AX1_EXPECTED) and _finite(swapped_ax2)
        print("[probe 5/5 swapped order guard] plot on ax1 + stackplot on ax2: "
              "ax1.dataLim.intervaly=%r, ax2.dataLim.intervaly=%r; the issue "
              "states this order already keeps ax1 at [-22.71770833 26.585] "
              "with finite ax2 limits -> %s"
              % (swapped_ax1.tolist(), swapped_ax2.tolist(),
                 "PASS" if ok else "FAIL"))
    except Exception as exc:
        ok = False
        print("[probe 5/5 swapped order guard] plot on ax1 + stackplot on ax2 "
              "raised %s: %s; the issue states this order already works -> FAIL"
              % (type(exc).__name__, exc))
    results.append(ok)

    passed = sum(1 for r in results if r)
    print("RESULT: %d/%d probes passed -> %s"
          % (passed, len(results), "ACCEPT" if passed == len(results) else "REJECT"))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    try:
        code = main()
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        sys.stdout.flush()
        sys.exit(2)
    sys.stdout.flush()
    sys.exit(code)

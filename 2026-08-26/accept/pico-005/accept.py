#!/usr/bin/env python
"""accept probe -- pico-005 (world matplotlib__matplotlib-24870)

Verdict source (policy P1): issues/pico-005.md ONLY.

The issue asks: "Autodetect boolean inputs to contour, and default levels to
[0.5] in that case."  Rationale given in the issue: without it, a boolean 2-D
array gets the default 8 levels (0, .15, .3, .45, .6, .75, .9, 1.05) and every
contour line is drawn on top of the others; "for boolean inputs, the only
choice that makes sense is to have a single level at 0.5 (or rather, anywhere
between 0 and 1)".

The issue names contour(); the same auto-level machinery serves contourf(), and
the requirement -- one single boundary between the False and True regions -- is
the same one there.  A filled contour cannot render a single boundary from a
one-element level list, so for contourf the equivalent of "one level at 0.5" is
one level strictly inside (0, 1) with the list bracketing it so both the False
side and the True side are filled.  Both surfaces are probed.

Exit codes: 0 = acceptance met, 1 = not met, 2 = probe broken.
"""

import sys
import traceback


def _levels_of(cs):
    import numpy as np
    return [float(v) for v in np.asarray(cs.levels).ravel().tolist()]


def _interior(levels):
    """Levels strictly between 0 and 1 -- i.e. real False/True boundaries."""
    return [v for v in levels if 0.0 < v < 1.0]


def main():
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # The issue's own example array.
    ii, jj = np.ogrid[:60, :60]
    im = ((ii + jj) % 20) < 10
    im = np.broadcast_to(im, (60, 60)).copy()
    if im.dtype != np.dtype(bool):
        raise RuntimeError(
            "probe setup wrong: test array dtype is %r, expected bool" % im.dtype)

    zf = ((ii + jj) % 20).astype(float)
    zf = np.broadcast_to(zf, (60, 60)).copy()

    results = []

    # ---- probe 1: contour() on a boolean 2-D array, no levels= given -------
    try:
        fig, ax = plt.subplots()
        cs = ax.contour(im)
        levels = _levels_of(cs)
        plt.close(fig)
        inner = _interior(levels)
        ok = (len(levels) == 1 and len(inner) == 1)
        print("[probe 1/4 contour] bool 2-D array, no levels= given -> "
              "cs.levels=%r (levels strictly in (0,1): %r); issue requires a "
              "single auto level at 0.5 / anywhere between 0 and 1 -> %s"
              % (levels, inner, "PASS" if ok else "FAIL"))
    except Exception as exc:
        ok = False
        print("[probe 1/4 contour] bool 2-D array, no levels= given -> raised "
              "%s: %s; issue requires a single auto level strictly between 0 "
              "and 1 -> FAIL" % (type(exc).__name__, exc))
    results.append(ok)

    # ---- probe 2: contourf() on the same boolean array ---------------------
    try:
        fig, ax = plt.subplots()
        cs = ax.contourf(im)
        levels = _levels_of(cs)
        plt.close(fig)
        inner = _interior(levels)
        ok = (len(inner) == 1
              and len(levels) >= 2
              and min(levels) <= 0.0
              and max(levels) >= 1.0)
        print("[probe 2/4 contourf] bool 2-D array, no levels= given -> "
              "cs.levels=%r (levels strictly in (0,1): %r); same auto-detection "
              "must give exactly one False/True boundary, bracketed so both "
              "regions are filled -> %s" % (levels, inner, "PASS" if ok else "FAIL"))
    except Exception as exc:
        ok = False
        print("[probe 2/4 contourf] bool 2-D array, no levels= given -> raised "
              "%s: %s; same auto-detection must give exactly one False/True "
              "boundary -> FAIL" % (type(exc).__name__, exc))
    results.append(ok)

    # ---- probe 3: an explicit levels= argument still wins ------------------
    try:
        fig, ax = plt.subplots()
        cs_c = ax.contour(im, levels=[0.5])
        lv_c = _levels_of(cs_c)
        cs_f = ax.contourf(im, levels=[0.0, 0.5, 1.0])
        lv_f = _levels_of(cs_f)
        plt.close(fig)
        ok = (lv_c == [0.5] and lv_f == [0.0, 0.5, 1.0])
        print("[probe 3/4 explicit levels] contour(bool, levels=[.5]) -> %r, "
              "contourf(bool, levels=[0,.5,1]) -> %r; auto-detection must not "
              "override an explicit levels= -> %s"
              % (lv_c, lv_f, "PASS" if ok else "FAIL"))
    except Exception as exc:
        ok = False
        print("[probe 3/4 explicit levels] raised %s: %s; auto-detection must "
              "not override an explicit levels= -> FAIL"
              % (type(exc).__name__, exc))
    results.append(ok)

    # ---- probe 4: non-boolean input keeps the normal auto levels -----------
    try:
        fig, ax = plt.subplots()
        cs_c = ax.contour(zf)
        lv_c = _levels_of(cs_c)
        cs_f = ax.contourf(zf)
        lv_f = _levels_of(cs_f)
        plt.close(fig)
        ok = (len(lv_c) > 1 and len(lv_f) > 1)
        print("[probe 4/4 float guard] float 2-D array (range 0..19) -> "
              "contour levels=%r, contourf levels=%r; the issue asks to "
              "autodetect *boolean* inputs only, non-bool must keep the usual "
              "multi-level default -> %s"
              % (lv_c, lv_f, "PASS" if ok else "FAIL"))
    except Exception as exc:
        ok = False
        print("[probe 4/4 float guard] raised %s: %s; non-bool input must keep "
              "the usual multi-level default -> FAIL"
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

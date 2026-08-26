#!/usr/bin/env python
"""accept probe -- pico-006 (world mwaskom__seaborn-3187)

Verdict source (policy P1): issues/pico-006.md ONLY.

The issue: "legends describing large numbers that were created using
ScalarFormatter with an offset are formatted without their multiplicative offset
value."  Its example multiplies penguin body mass by 1000 so `body_mass_mg` is
"in the order of 1E6", and the legend then shows entries like 3, 4, 5, 6 -- the
bare mantissas ScalarFormatter emits once it has factored out a 1e6 offset.  The
issue closes with: "The offset value can be safely retrieved from all formatters
and based on that it can be used to create the legend title and/or labels."

So the acceptance is a magnitude question, not a formatting question: whatever a
reader can compute from the size legend (its labels, plus any offset the legend
carries in its title or as its own text) must land in the neighbourhood of the
real values, ~1e6, instead of being off by six orders of magnitude.  Both
presentations the issue allows ("title and/or labels") are accepted.

The issue names two paths and says both reproduce: the seaborn.objects path
(so.Plot(...).add(so.Dot()) with pointsize=) and the classic `scatterplot`.
Both are probed, and scatterplot is probed with its default legend mode, which
is the brief/locator path the ScalarFormatter complaint is about.

The container has no network, so the probe builds a penguins-shaped frame
locally instead of calling sns.load_dataset().

Exit codes: 0 = acceptance met, 1 = not met, 2 = probe broken.
"""

import re
import sys
import traceback

# --- offset markers a legend might carry, in any of the shapes matplotlib's
# --- ScalarFormatter.get_offset() can produce, plus plain-text variants.
_SUPERS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUPER_MAP = {c: str(i) for i, c in enumerate(_SUPERS)}

_OFFSET_PATTERNS = [
    # 1e6, 1E+06, 1.0e6
    re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*[eE]\s*\+?\s*(\d+)(?![\w.])"),
    # mathtext / caret: 10^{6}, \times 10^6
    re.compile(r"10\s*\^\s*\{?\s*\+?(\d+)\s*\}?"),
    # unicode superscript: 10⁶
    re.compile(r"10\s*([" + _SUPERS + r"]+)"),
]

_NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
# a full value written out in scientific form, e.g. '3*10^6' after cleaning
_SCI_RE = re.compile(
    r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\*?\s*10\s*\^\s*([+-]?\d+)$")


def _clean(text):
    """Strip mathtext decoration so a label like '$3$' parses as a number."""
    s = text.strip()
    s = s.replace("$", "").replace("\\mathdefault", "")
    s = s.replace("\\times", "*")
    # unicode superscripts -> caret form, so one caret pattern covers both
    for _c, _d in _SUPER_MAP.items():
        if _c in s:
            s = s.replace("10" + _c, "10^" + _d).replace(_c, _d)
    s = s.replace("−", "-")          # unicode minus
    s = s.replace("\u00d7", "*")        # times sign
    s = s.replace("{", "").replace("}", "")
    return s.strip()


def _as_number(text):
    # a label is a single token: drop whitespace and digit grouping first
    s = _clean(text).replace(",", "")
    s = "".join(ch for ch in s if not ch.isspace())
    if not s:
        return None
    if _NUMBER_RE.match(s):
        try:
            return float(s)
        except ValueError:
            return None
    m = _SCI_RE.match(s)          # e.g. a label written as 3x10^6
    if m:
        try:
            return float(m.group(1)) * (10.0 ** int(m.group(2)))
        except (ValueError, OverflowError):
            return None
    return None


def _offset_factor(text):
    """Multiplicative offset this text advertises, or None."""
    s = _clean(text)
    m = _OFFSET_PATTERNS[0].search(s)
    if m:
        return float(m.group(1)) * (10.0 ** int(m.group(2)))
    m = _OFFSET_PATTERNS[1].search(s)
    if m:
        return 10.0 ** int(m.group(1))
    m = _OFFSET_PATTERNS[2].search(s)
    if m:
        digits = "".join(_SUPER_MAP.get(c, "") for c in m.group(1))
        if digits:
            return 10.0 ** int(digits)
    return None


def _legend_texts(legends):
    """Every non-empty string in these Legend artists: labels and titles."""
    import matplotlib as mpl
    out = []
    for leg in legends:
        if leg is None:
            continue
        for artist in leg.findobj(mpl.text.Text):
            s = artist.get_text()
            if s and s.strip():
                out.append(s)
    return out


def _readings(texts):
    """Every largest-value a reader could reconstruct from this legend.

    Several readings are tried, because the issue allows the offset to live in
    "the legend title and/or labels":
      A) the labels already carry the full value (no offset needed);
      B) the labels are mantissas and some other legend text carries the offset.
    Returns a list of (value, explanation); empty if the legend carries no
    numeric entry at all.
    """
    numbers = [(t, _as_number(t)) for t in texts]
    numbers = [(t, v) for t, v in numbers if v is not None]

    offsets = [(t, _offset_factor(t)) for t in texts]
    offsets = [(t, f) for t, f in offsets if f is not None and f > 1.0]

    if not numbers:
        return []

    readings = []
    # reading A: labels as-is
    a_max = max(abs(v) for _, v in numbers)
    readings.append((a_max, "labels read literally -> max |label| = %g" % a_max))

    # reading B: labels x an offset advertised elsewhere in the legend
    for otext, factor in offsets:
        mantissas = [v for t, v in numbers if t != otext]
        if not mantissas:
            continue
        b_max = max(abs(v) for v in mantissas) * factor
        readings.append(
            (b_max, "labels x the offset %g carried by legend text %r -> max = %g"
             % (factor, otext, b_max)))
    return readings


def _conveys_magnitude(texts, lo, hi):
    """True iff some reading of the legend lands in the real data's ballpark."""
    readings = _readings(texts)
    if not readings:
        return False, "no numeric legend entries found"
    fits = [(v, why) for v, why in readings if lo <= v <= hi]
    if fits:
        return True, "reading that fits %g..%g: %s" % (lo, hi, fits[0][1])
    return False, "no reading fits %g..%g; tried: %s" % (
        lo, hi, "; ".join(why for _, why in readings))


def _make_frame():
    """A penguins-shaped frame; sns.load_dataset() needs network, we have none."""
    import numpy as np
    import pandas as pd

    rng = np.random.RandomState(0)
    n = 120
    species = np.asarray(["Adelie", "Chinstrap", "Gentoo"])[rng.randint(0, 3, n)]
    body_mass_g = rng.uniform(2700.0, 6300.0, n)
    # pin the ends so the data range is deterministic and spans > 2x (which
    # keeps ScalarFormatter on a purely multiplicative 1e6 offset)
    body_mass_g[0] = 2700.0
    body_mass_g[1] = 6300.0
    df = pd.DataFrame({
        "bill_length_mm": rng.uniform(32.0, 60.0, n),
        "bill_depth_mm": rng.uniform(13.0, 22.0, n),
        "species": species,
        "body_mass_g": body_mass_g,
    })
    df["body_mass_mg"] = df["body_mass_g"] * 1000
    return df


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: F401  (import order matters)
    import seaborn as sns
    import seaborn.objects as so

    df = _make_frame()
    data_min = float(df["body_mass_mg"].min())
    data_max = float(df["body_mass_mg"].max())
    # generous window: the bug is a ~1e6 error, so anything within two orders of
    # magnitude of the real values counts as "the legend conveys the magnitude".
    lo, hi = data_min / 100.0, data_max * 100.0

    results = []

    # ---- probe 1: the issue's own snippet, seaborn.objects ----------------
    try:
        p = (
            so.Plot(
                df, x="bill_length_mm", y="bill_depth_mm",
                color="species", pointsize="body_mass_mg",
            )
            .add(so.Dot())
        )
        plotter = p.plot()
        fig = getattr(plotter, "_figure", None)
        if fig is None:
            fig = getattr(plotter, "figure", None)
        if fig is None:
            raise RuntimeError("could not reach the Figure of %r" % (plotter,))
        # the objects interface puts its legend on the figure; fall back to any
        # axes-level legend so the probe does not depend on that placement
        legends = list(fig.legends) + [a.get_legend() for a in fig.axes]
        texts = _legend_texts(legends)
        ok, why = _conveys_magnitude(texts, lo, hi)
        print("[probe 1/2 so.Plot pointsize] body_mass_mg spans %g..%g; legend "
              "texts=%r; %s; the issue requires the legend to convey the real "
              "~1e6 magnitude, in its labels or via the ScalarFormatter offset "
              "-> %s" % (data_min, data_max, texts, why,
                         "PASS" if ok else "FAIL"))
        plt.close(fig)
    except Exception as exc:
        ok = False
        print("[probe 1/2 so.Plot pointsize] raised %s: %s; the issue requires "
              "the size legend to convey the real ~1e6 magnitude -> FAIL"
              % (type(exc).__name__, exc))
    results.append(ok)

    # ---- probe 2: "The issue also reproduces if you create the mentioned
    #                plot using scatterplot." (default legend mode) ----------
    try:
        fig2, ax = plt.subplots()
        sns.scatterplot(
            data=df, x="bill_length_mm", y="bill_depth_mm",
            hue="species", size="body_mass_mg", ax=ax,
        )
        texts = _legend_texts([ax.get_legend()] + list(fig2.legends))
        ok, why = _conveys_magnitude(texts, lo, hi)
        print("[probe 2/2 scatterplot size legend] default legend mode (the "
              "brief/locator path the ScalarFormatter complaint is about); "
              "legend texts=%r; %s; the issue says this path reproduces too and "
              "requires the real ~1e6 magnitude -> %s"
              % (texts, why, "PASS" if ok else "FAIL"))
        plt.close(fig2)
    except Exception as exc:
        ok = False
        print("[probe 2/2 scatterplot size legend] raised %s: %s; the issue "
              "says scatterplot reproduces too and requires the real ~1e6 "
              "magnitude -> FAIL" % (type(exc).__name__, exc))
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

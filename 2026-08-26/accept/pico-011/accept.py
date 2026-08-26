#!/usr/bin/env python
"""accept probe for pico-011 (world: sympy__sympy-13798).

Verdict source: issues/pico-011.md ONLY (policy P1).

The issue: `latex()` accepts a `mul_symbol` kwarg "that must be one of four
choices"; the reporter wants to supply their own, specifically a thin space
`\\,`, so that

    >>> latex(3*x**2*y)          # with mul_symbol='\\,'
    '3 \\, x^{2} \\, y'

and offers to make it "arbitrary (and backwards-compatible)". So the probes
are: an arbitrary mul_symbol is accepted and actually used as the separator,
and the four historical choices plus the default still render as before.
The issue also quotes sympy's existing integral rendering
`'\\int 2 x^{2} y\\, dx'` as *current behaviour*, so that is asserted too.

Comparisons normalise away whitespace: the issue is about which symbol lands
between the factors, not about how much padding an implementation puts round
it (the reporter typed the spaces in by hand: "I typed the thin spaces in
after the fact").

Exit codes: 0 = accepted, 1 = not accepted, 2 = probe broken.
"""

import sys
import traceback


def squash(s):
    """Drop all whitespace so ' \\, ' and '\\,' compare equal."""
    return "".join(str(s).split())


def run_probe(name, fn, results):
    """An exception inside a probe is a FAIL (the unfixed repo raises
    KeyError for an unknown mul_symbol), not a broken-probe alarm."""
    try:
        ok, detail = fn()
    except Exception as exc:  # noqa: BLE001 - probe-local, deliberate
        ok = False
        detail = "raised %s: %s" % (type(exc).__name__, exc)
    results.append(bool(ok))
    print("[%s] %s :: %s" % ("PASS" if ok else "FAIL", name, detail))
    sys.stdout.flush()


def main():
    # --- world setup (failures here are genuine alarms -> exit 2) ----------
    from sympy import Float, Integral, latex, symbols

    x, y = symbols("x y")
    expr = 3 * x ** 2 * y

    results = []

    # --- 1: the exact ask in the issue: mul_symbol='\,' --------------------
    def probe_thin_space():
        out = latex(expr, mul_symbol=r"\,")
        want = squash(r"3 \, x^{2} \, y")
        got = squash(out)
        return (
            got == want,
            "latex(3*x**2*y, mul_symbol=r'\\,') -> %r ; issue asks for "
            "'3 \\, x^{2} \\, y' (whitespace-insensitive)" % (out,),
        )

    run_probe("custom mul_symbol '\\,'", probe_thin_space, results)

    # --- 2: arbitrary, not just a second hard-coded name -------------------
    def probe_arbitrary():
        out = latex(3 * x * y, mul_symbol="*")
        got = squash(out)
        return (
            got == "3*x*y",
            "latex(3*x*y, mul_symbol='*') -> %r ; a second, unrelated symbol "
            "must also be honoured verbatim ('arbitrary')" % (out,),
        )

    run_probe("arbitrary mul_symbol '*'", probe_arbitrary, results)

    # --- 3: the custom symbol survives inside a bigger expression ----------
    def probe_thin_space_nested():
        out = latex(2 * x ** 2 * y + x * y, mul_symbol=r"\,")
        bad = [m for m in (r"\cdot", r"\times") if m in out]
        ok = squash(out).count(r"\,") >= 3 and not bad
        return (
            ok,
            "latex(2*x**2*y + x*y, mul_symbol=r'\\,') -> %r ; every factor "
            "separator must be the supplied symbol, none of %r may reappear"
            % (out, bad or [r"\cdot", r"\times"]),
        )

    run_probe("custom mul_symbol used throughout", probe_thin_space_nested, results)

    # --- 4: backwards compatible with the four historical choices ----------
    def probe_backwards_compatible():
        checks = [
            ("default", latex(expr), squash("3 x^{2} y"), "squash-equals"),
            ("dot", latex(expr, mul_symbol="dot"), r"\cdot", "contains"),
            ("times", latex(expr, mul_symbol="times"), r"\times", "contains"),
            ("ldot", latex(expr, mul_symbol="ldot"), r"\,.\,", "contains"),
        ]
        bad = []
        shown = []
        for name, got, want, mode in checks:
            ok = (squash(got) == want) if mode == "squash-equals" else (want in got)
            shown.append("%s->%r" % (name, got))
            if not ok:
                bad.append("%s (wanted %s %r)" % (name, mode, want))
        return (
            not bad,
            "historical choices still render: %s ; failures: %s"
            % ("; ".join(shown), bad or "none"),
        )

    run_probe("four documented choices unchanged", probe_backwards_compatible, results)

    # --- 5: the integral thin space quoted in the issue is unchanged -------
    def probe_integral():
        out = latex(Integral(2 * x ** 2 * y, x))
        want = squash(r"\int 2 x^{2} y\, dx")
        return (
            squash(out) == want,
            "latex(Integral(2*x**2*y, x)) -> %r ; issue quotes "
            "'\\int 2 x^{2} y\\, dx' as sympy's current behaviour" % (out,),
        )

    run_probe("integral differential spacing unchanged", probe_integral, results)

    # --- informational only (NOT gating): the issue is silent about how a
    # custom symbol should interact with sympy's separate number<->number
    # rule, so this is printed as evidence and deliberately not asserted.
    try:
        info_default = latex(Float("3.5e-15") * x)
    except Exception as exc:  # noqa: BLE001
        info_default = "raised %s: %s" % (type(exc).__name__, exc)
    try:
        info_custom = latex(Float("3.5e-15") * x, mul_symbol=r"\,")
    except Exception as exc:  # noqa: BLE001
        info_custom = "raised %s: %s" % (type(exc).__name__, exc)
    print(
        "[INFO] number<->number separation (not gating, issue is silent) :: "
        "latex(Float('3.5e-15')*x) -> %r ; with mul_symbol=r'\\,' -> %r"
        % (info_default, info_custom)
    )

    passed = sum(1 for r in results if r)
    print("summary: %d/%d probes passed" % (passed, len(results)))
    return 0 if results and all(results) else 1


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        traceback.print_exc()
        code = 2
    sys.exit(code)

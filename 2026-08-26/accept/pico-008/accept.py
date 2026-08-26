#!/usr/bin/env python
"""accept probe for pico-008 (world: pydata__xarray-6938).

Verdict source: issues/pico-008.md ONLY (policy P1).

The issue: "`.swap_dims()` can modify original object ... here the `.dims` of a
data variable that was swapped into being a dimension coordinate variable".
Expectation, in the reporter's words: "I expected it not to modify the original
object."  The MVCE builds `ds2` via
`ds.swap_dims(z='lev').rename_dims(lev='z').reset_index('lev').reset_coords()`
and observes that after `ds2.swap_dims(z='lev')`, "`ds2['lev']` now has
dimension 'lev' although otherwise same".

So: run the issue's own repro, then assert the *original* is untouched (and
that the returned object is still the correct swapped result -- a "fix" that
neuters swap_dims would not satisfy the issue either).

Exit codes: 0 = accepted, 1 = not accepted, 2 = probe broken.
"""

import sys
import traceback

NZ = 11


def run_probe(name, fn, results):
    """An exception inside a probe is a FAIL, not a broken-probe alarm."""
    try:
        ok, detail = fn()
    except Exception as exc:  # noqa: BLE001 - probe-local, deliberate
        ok = False
        detail = "raised %s: %s" % (type(exc).__name__, exc)
    results.append(bool(ok))
    print("[%s] %s :: %s" % ("PASS" if ok else "FAIL", name, detail))
    sys.stdout.flush()


def main():
    # --- world setup: the issue's MVCE verbatim ---------------------------
    # Failures constructing it are genuine alarms (-> exit 2): the issue
    # states this snippet runs and returns a result.
    import numpy as np
    import xarray as xr

    rng = np.random.RandomState(0)
    lev_values = np.arange(NZ) * 10

    def make_ds():
        return xr.Dataset(
            data_vars={
                "y": ("z", rng.rand(NZ)),
                "lev": ("z", np.arange(NZ) * 10),
                # ^ We want this to be a dimension coordinate
            },
        )

    def make_ds2():
        return (
            make_ds()
            .swap_dims(z="lev")
            .rename_dims(lev="z")
            .reset_index("lev")
            .reset_coords()
        )

    ds2 = make_ds2()
    results = []

    # --- 1: baseline sanity -- ds2 really does start out looking like ds ---
    def probe_baseline():
        dims = tuple(ds2["lev"].dims)
        return (
            dims == ("z",) and set(ds2.sizes) == {"z"},
            "before any swap_dims call, ds2['lev'].dims=%r and ds2.dims=%r "
            "(issue: 'This Dataset appears same as the original')"
            % (dims, dict(ds2.sizes)),
        )

    run_probe("baseline ds2 shape", probe_baseline, results)

    # --- 2: the issue's headline assertion --------------------------------
    def probe_no_mutation():
        local = make_ds2()
        before = tuple(local["lev"].dims)
        local.swap_dims(z="lev")
        after = tuple(local["lev"].dims)
        return (
            after == before == ("z",),
            "ds2['lev'].dims before swap_dims=%r, after=%r; issue expects "
            "swap_dims not to modify the original (unfixed: becomes ('lev',))"
            % (before, after),
        )

    run_probe("ds2 unmodified by swap_dims", probe_no_mutation, results)

    # --- 3: nothing else on the original moved either ---------------------
    def probe_no_mutation_wider():
        local = make_ds2()
        before_dims = dict(local.sizes)
        before_vars = sorted(local.data_vars)
        before_coords = sorted(local.coords)
        before_values = np.asarray(local["lev"].values).copy()
        local.swap_dims(z="lev")
        same_dims = dict(local.sizes) == before_dims
        same_vars = sorted(local.data_vars) == before_vars
        same_coords = sorted(local.coords) == before_coords
        same_values = np.array_equal(np.asarray(local["lev"].values), before_values)
        ok = same_dims and same_vars and same_coords and same_values
        return (
            ok,
            "original ds2 after swap_dims: dims %r (was %r), data_vars %r, "
            "coords %r, lev values unchanged=%s"
            % (
                dict(local.sizes),
                before_dims,
                sorted(local.data_vars),
                sorted(local.coords),
                same_values,
            ),
        )

    run_probe("ds2 dims/vars/coords/values intact", probe_no_mutation_wider, results)

    # --- 4: and the returned object is still the right answer -------------
    def probe_result_correct():
        swapped = make_ds2().swap_dims(z="lev")
        lev_dims = tuple(swapped["lev"].dims)
        is_coord = "lev" in swapped.coords
        size_ok = swapped.sizes.get("lev") == NZ
        y_dims = tuple(swapped["y"].dims)
        values_ok = np.array_equal(np.asarray(swapped["lev"].values), lev_values)
        ok = lev_dims == ("lev",) and is_coord and size_ok and y_dims == ("lev",) and values_ok
        return (
            ok,
            "returned object: lev.dims=%r, lev in coords=%s, sizes['lev']=%r, "
            "y.dims=%r, lev values preserved=%s; issue wants a Dataset with "
            "dimension coordinate 'lev'"
            % (lev_dims, is_coord, swapped.sizes.get("lev"), y_dims, values_ok),
        )

    run_probe("swap_dims result still correct", probe_result_correct, results)

    # --- 5: the first swap_dims in the MVCE leaves `ds` alone too ---------
    def probe_original_ds():
        local = make_ds()
        before = tuple(local["lev"].dims)
        local.swap_dims(z="lev")
        after = tuple(local["lev"].dims)
        return (
            after == before == ("z",),
            "the MVCE's first object ds: lev.dims before=%r after=%r"
            % (before, after),
        )

    run_probe("ds unmodified by swap_dims", probe_original_ds, results)

    # --- 6: same requirement through the DataArray entry point ------------
    def probe_dataarray():
        da = xr.DataArray(
            rng.rand(NZ),
            dims="z",
            coords={"lev": ("z", np.arange(NZ) * 10)},
        )
        before = tuple(da["lev"].dims)
        swapped = da.swap_dims(z="lev")
        after = tuple(da["lev"].dims)
        ok = after == before == ("z",) and tuple(swapped.dims) == ("lev",)
        return (
            ok,
            "DataArray.swap_dims: original lev.dims before=%r after=%r, "
            "result dims=%r" % (before, after, tuple(swapped.dims)),
        )

    run_probe("DataArray original unmodified", probe_dataarray, results)

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

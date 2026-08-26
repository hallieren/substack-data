#!/usr/bin/env python
"""accept probe for pico-002 (world: astropy__astropy-13398).

Verdict source: issues/pico-002.md ONLY (policy P1).

The issue asks for "a direct approach to ITRS to Observed transformations that
stays within the ITRS": direct ITRS<->AltAz and ITRS<->HADec transforms that

  * subtract the observer's ITRS position to form a *topocentric* ITRS vector
    and rotate it with the geodetic (WGS84) lon/lat matrices quoted in the
    issue, so an object that really is straight overhead comes out at alt=90
    without the "entirely nonintuitive solution laid out in
    test_straight_overhead()";
  * treat the ITRS position as TIME INVARIANT -- "the obstime of the output
    frame is simply adopted", because an ITRS->ITRS hop across obstimes
    "refers the ITRS coordinates to the SSB rather than the rotating ITRF"
    and leaves a nearby position "perhaps millions of kilometers from where
    it is intended to be".

Every probe below is an assertion about one of those two sentences (or about
the geometry of the matrices printed in the issue). Exit 0 iff all pass.

Exit codes: 0 = accepted, 1 = not accepted, 2 = probe broken.
"""

import sys
import traceback

TOL_ARCSEC = 5.0      # angular tolerance; the prescribed geometry is exact
TOL_METRE = 1.0       # positional tolerance for distance / round trip


def run_probe(name, fn, results):
    """Run one probe. An exception inside a probe is a FAIL, not an alarm:
    on the unfixed repo the transform may legitimately blow up."""
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
    import numpy as np  # noqa: F401  (kept: astropy pulls it in anyway)
    from astropy import units as u
    from astropy.time import Time
    from astropy.coordinates import Angle, AltAz, EarthLocation, HADec, ITRS
    from astropy.coordinates.baseframe import frame_transform_graph

    # network is off in the sealed container: never let astropy try to fetch
    # IERS/leap-second tables (it would just burn the time budget).
    try:
        from astropy.utils import iers

        iers.conf.auto_download = False
        try:
            iers.conf.auto_max_age = None
        except Exception:
            pass
        try:
            iers.conf.iers_degraded_accuracy = "ignore"
        except Exception:
            pass
    except Exception:
        pass

    # The issue's motivating scenario: something nearby (a satellite / an
    # aircraft / a mountain top) sitting exactly above the observer.
    obstime = Time("2010-01-01T12:00:00", scale="utc")
    other_obstime = obstime + 6.0 * u.hour
    lon = -1.0 * u.deg
    lat = 52.0 * u.deg
    home = EarthLocation.from_geodetic(lon, lat, height=0.0 * u.m)
    obj = EarthLocation.from_geodetic(lon, lat, height=10.0 * u.km)
    obj_itrs = obj.get_itrs(obstime)  # geocentric ITRS position, obstime set

    def n_hops(fromsys, tosys):
        trans = frame_transform_graph.get_transform(fromsys, tosys)
        if trans is None:
            raise RuntimeError("no transform path registered")
        return len(getattr(trans, "transforms", [trans]))

    results = []

    # --- 1..4: the direct transforms the issue proposes exist --------------
    def probe_direct(fromsys, tosys):
        def _fn():
            hops = n_hops(fromsys, tosys)
            return (
                hops == 1,
                "%s -> %s resolves in %d graph hop(s); issue asks for a direct "
                "transform that stays within the ITRS (expected 1)"
                % (fromsys.__name__, tosys.__name__, hops),
            )

        return _fn

    run_probe("direct ITRS->AltAz edge", probe_direct(ITRS, AltAz), results)
    run_probe("direct ITRS->HADec edge", probe_direct(ITRS, HADec), results)
    run_probe("direct AltAz->ITRS edge", probe_direct(AltAz, ITRS), results)
    run_probe("direct HADec->ITRS edge", probe_direct(HADec, ITRS), results)

    # --- 5: straight overhead comes out straight overhead ------------------
    def probe_overhead():
        aa = obj_itrs.transform_to(AltAz(obstime=obstime, location=home))
        alt_err = abs(aa.alt.to_value(u.deg) - 90.0) * 3600.0
        dist_err = abs(aa.distance.to_value(u.m) - 10000.0)
        ok = alt_err < TOL_ARCSEC and dist_err < TOL_METRE
        return (
            ok,
            "object 10 km above the observer, same obstime: alt=%.6f deg "
            "(err %.4f arcsec, tol %.1f), topocentric distance err %.4f m "
            "(tol %.1f)"
            % (aa.alt.to_value(u.deg), alt_err, TOL_ARCSEC, dist_err, TOL_METRE),
        )

    run_probe("ITRS->AltAz straight overhead", probe_overhead, results)

    # --- 6: the ITRS position is time invariant ---------------------------
    def probe_time_invariant():
        aa1 = obj_itrs.transform_to(AltAz(obstime=obstime, location=home))
        aa2 = obj_itrs.transform_to(AltAz(obstime=other_obstime, location=home))
        alt2_err = abs(aa2.alt.to_value(u.deg) - 90.0) * 3600.0
        drift = abs(aa2.alt.to_value(u.deg) - aa1.alt.to_value(u.deg)) * 3600.0
        ok = alt2_err < TOL_ARCSEC and drift < TOL_ARCSEC
        return (
            ok,
            "same ITRS position into AltAz(obstime=+6h): alt=%.6f deg "
            "(err %.4f arcsec), moved %.4f arcsec vs the matching-obstime "
            "result; issue says the output frame's obstime is simply adopted "
            "and the ITRS position is time invariant (tol %.1f arcsec)"
            % (aa2.alt.to_value(u.deg), alt2_err, drift, TOL_ARCSEC),
        )

    run_probe("ITRS treated as time invariant", probe_time_invariant, results)

    # --- 7: HADec follows the same geometry -------------------------------
    def probe_hadec():
        hd = obj_itrs.transform_to(HADec(obstime=obstime, location=home))
        ha_err = abs(Angle(hd.ha).wrap_at(180.0 * u.deg).to_value(u.arcsec))
        dec_err = abs(hd.dec.to_value(u.deg) - lat.to_value(u.deg)) * 3600.0
        ok = ha_err < TOL_ARCSEC and dec_err < TOL_ARCSEC
        return (
            ok,
            "same overhead object into HADec: ha err %.4f arcsec, dec=%.6f deg "
            "vs geodetic latitude %.1f deg (err %.4f arcsec, tol %.1f)"
            % (
                ha_err,
                hd.dec.to_value(u.deg),
                lat.to_value(u.deg),
                dec_err,
                TOL_ARCSEC,
            ),
        )

    run_probe("ITRS->HADec straight overhead", probe_hadec, results)

    # --- 8: the observed->ITRS direction inverts it ------------------------
    def probe_round_trip():
        aa = obj_itrs.transform_to(AltAz(obstime=obstime, location=home))
        back = aa.transform_to(ITRS(obstime=obstime))
        sep = (back.cartesian - obj_itrs.cartesian).norm().to_value(u.m)
        return (
            sep < TOL_METRE,
            "ITRS -> AltAz -> ITRS returns the geocentric position to within "
            "%.6f m (tol %.1f)" % (sep, TOL_METRE),
        )

    run_probe("AltAz->ITRS round trip", probe_round_trip, results)

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

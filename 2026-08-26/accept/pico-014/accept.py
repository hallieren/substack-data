"""accept — pico-014 (django__django-13401)

Verdict source: issues/pico-014.md ONLY (policy P1). The issue asks for:
  - fields inherited from an abstract base into two different concrete models
    must not compare equal (`B._meta.get_field('myfield') == C._meta.get_field('myfield')`
    is wrong, and `len({B..., C...}) == 1` is wrong);
  - `__hash__` and `__lt__` adjusted to match;
  - `__lt__` ordering first by `self.creation_counter`, so fields not affected
    by the collision are not re-ordered.
Nothing here comes from the maintainer's patch or from any hidden test.

Exit: 0 all probes pass · 1 some probe failed · 2 probe broken.
"""

import sys
import traceback

RESULTS = []


def report(label, ok, observed):
    RESULTS.append(bool(ok))
    print("[%s] %s | %s" % ("PASS" if ok else "FAIL", label, observed))


def probe(label, fn):
    """Run one probe; a raised exception is a FAILED probe, not a broken one.

    (A TypeError out of `<` is exactly one of the outcomes under test.)
    """
    try:
        ok, observed = fn()
    except Exception as exc:
        report(label, False, "raised %s: %s" % (type(exc).__name__, exc))
        return
    report(label, ok, observed)


def main():
    import copy

    import django
    from django.conf import settings

    settings.configure(
        DEBUG=False,
        USE_TZ=False,
        INSTALLED_APPS=[],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    django.setup()

    from django.db import models

    # The issue's models, plus a second abstract field created later so the
    # creation_counter ordering requirement can be checked across models.
    class A(models.Model):
        myfield = models.IntegerField()
        laterfield = models.IntegerField()

        class Meta:
            abstract = True
            app_label = "pico014"

    class B(A):
        class Meta:
            app_label = "pico014"

    class C(A):
        class Meta:
            app_label = "pico014"

    b_my = B._meta.get_field("myfield")
    c_my = C._meta.get_field("myfield")
    b_later = B._meta.get_field("laterfield")
    c_later = C._meta.get_field("laterfield")

    print("[INFO] creation_counters: B.myfield=%s C.myfield=%s B.laterfield=%s C.laterfield=%s"
          % (b_my.creation_counter, c_my.creation_counter,
             b_later.creation_counter, c_later.creation_counter))

    # 1. The issue's second line: the two fields must not compare equal.
    def p1():
        eq = b_my == c_my
        ne = b_my != c_my
        return (eq is False and ne is True,
                "B._meta.get_field('myfield') == C._meta.get_field('myfield') -> %s, != -> %s"
                % (eq, ne))

    probe("abstract field inherited into two models compares unequal", p1)

    # 2. The issue's first line: pulling both into a set must not de-duplicate.
    def p2():
        n = len({b_my, c_my})
        return (n == 2, "len({B.myfield, C.myfield}) -> %d (issue reports 1, wants 2)" % n)

    probe("the two fields survive as distinct members of a set", p2)

    # 3. __lt__ must stay a strict order on the colliding pair (same
    #    creation_counter): exactly one direction true, and no exception.
    def p3():
        fwd = bool(b_my < c_my)
        rev = bool(c_my < b_my)
        ordered = sorted([c_my, b_my])
        names = [f.model.__name__ for f in ordered]
        return (fwd != rev,
                "equal creation_counter tie: B<C -> %s, C<B -> %s; sorted([C,B]) -> %s"
                % (fwd, rev, names))

    probe("__lt__ breaks the equal-creation_counter tie one way only", p3)

    # 4. Ordering is by creation_counter FIRST, so unaffected pairs keep their order.
    def p4():
        fwd = bool(c_my < b_later)   # smaller counter, other model
        rev = bool(b_later < c_my)
        return (fwd is True and rev is False,
                "C.myfield(counter %d) < B.laterfield(counter %d) -> %s; reverse -> %s"
                % (c_my.creation_counter, b_later.creation_counter, fwd, rev))

    probe("__lt__ still orders by creation_counter before model", p4)

    # 5. Sorting a mixed list stays consistent with creation_counter first.
    def p5():
        order = sorted([b_later, c_later, c_my, b_my])
        counters = [f.creation_counter for f in order]
        return (counters == sorted(counters),
                "sorted([B.laterfield, C.laterfield, C.myfield, B.myfield]) counters -> %s"
                % counters)

    probe("sorting a mixed list of fields is by creation_counter first", p5)

    # 6. Equality/hash must not collapse into identity: the same field on the
    #    same model still compares (and hashes) equal to a copy of itself.
    def p6():
        clone = copy.deepcopy(b_my)
        eq_self = b_my == b_my
        eq_clone = b_my == clone
        h = hash(b_my) == hash(clone)
        return (eq_self is True and eq_clone is True and h,
                "B.myfield == itself -> %s; == deepcopy (same model, same counter) -> %s; "
                "hashes equal -> %s" % (eq_self, eq_clone, h))

    probe("same-model fields still compare and hash equal", p6)


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

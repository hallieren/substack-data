"""accept — pico-004 (django__django-15252)

Verdict source: issues/pico-004.md ONLY (policy P1). The issue says: with a
router whose allow_migrate returns True only for 'default', the migration
recorder must not create the django_migrations table on any other connection
("my expectation would be that the table is not created on any connection
other than the 'default' connection"), and the same is expected of
applied_migrations and record_unapplied. Nothing here comes from the
maintainer's patch or from any hidden test.

Exit: 0 all probes pass · 1 some probe failed · 2 probe broken.
"""

import sys
import traceback

RESULTS = []


def report(label, ok, observed):
    RESULTS.append(bool(ok))
    print("[%s] %s | %s" % ("PASS" if ok else "FAIL", label, observed))


def probe(label, fn):
    """Run one probe; a raised exception is a FAILED probe, not a broken one."""
    try:
        ok, observed = fn()
    except Exception as exc:  # behaviour of the code under test, not of the harness
        report(label, False, "raised %s: %s" % (type(exc).__name__, exc))
        return
    report(label, ok, observed)


def main():
    import django
    from django.conf import settings

    class Router:
        """The router from the issue: migrations allowed only on 'default'."""

        def allow_migrate(self, db, app_label, model_name=None, **hints):
            return db == "default"

    settings.configure(
        DEBUG=False,
        USE_TZ=False,
        INSTALLED_APPS=[],
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
            "other": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        },
        DATABASE_ROUTERS=[Router()],
    )
    django.setup()

    from django.db import connections
    from django.db.migrations.recorder import MigrationRecorder

    table = MigrationRecorder.Migration._meta.db_table

    def tables(alias):
        return list(connections[alias].introspection.table_names())

    def has_table(alias):
        return table in tables(alias)

    blocked = MigrationRecorder(connections["other"])
    allowed = MigrationRecorder(connections["default"])

    # 1. ensure_schema() on the disallowed connection must not create the table.
    def p1():
        blocked.ensure_schema()
        present = has_table("other")
        return (not present,
                "after ensure_schema() on 'other' (allow_migrate False): %s in tables=%s "
                "(tables=%s)" % (table, present, tables("other")))

    probe("ensure_schema does not create the recorder table on a disallowed connection", p1)

    # 2. record_applied() on the disallowed connection: no table, no crash
    #    (migrate is run against every connection, so it must stay a silent no-op).
    def p2():
        blocked.record_applied("pico004", "0001_initial")
        present = has_table("other")
        return (not present,
                "record_applied('pico004','0001_initial') on 'other' returned without error; "
                "%s in tables=%s" % (table, present))

    probe("record_applied writes nothing on a disallowed connection", p2)

    # 3. applied_migrations() on the disallowed connection: empty, no table, no crash.
    def p3():
        applied = blocked.applied_migrations()
        present = has_table("other")
        return (len(applied) == 0 and not present,
                "applied_migrations() on 'other' -> %d entries; %s in tables=%s"
                % (len(applied), table, present))

    probe("applied_migrations reports nothing on a disallowed connection", p3)

    # 4. record_unapplied() on the disallowed connection: no table, no crash.
    def p4():
        blocked.record_unapplied("pico004", "0001_initial")
        present = has_table("other")
        return (not present,
                "record_unapplied('pico004','0001_initial') on 'other' returned without error; "
                "%s in tables=%s" % (table, present))

    probe("record_unapplied writes nothing on a disallowed connection", p4)

    # 5. The allowed connection keeps working exactly as before.
    def p5():
        allowed.ensure_schema()
        created = has_table("default")
        allowed.record_applied("pico004", "0001_initial")
        applied = allowed.applied_migrations()
        recorded = ("pico004", "0001_initial") in applied
        return (created and recorded,
                "on 'default' (allow_migrate True): %s created=%s, ('pico004','0001_initial') "
                "recorded=%s (%d entries)" % (table, created, recorded, len(applied)))

    probe("the allowed connection still creates and records migrations", p5)

    # 6. ...and unrecording still works there.
    def p6():
        allowed.record_unapplied("pico004", "0001_initial")
        applied = allowed.applied_migrations()
        gone = ("pico004", "0001_initial") not in applied
        return (gone,
                "on 'default': record_unapplied removed the row -> present=%s (%d entries)"
                % (not gone, len(applied)))

    probe("the allowed connection still unrecords migrations", p6)


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

#!/usr/bin/env python
"""accept -- pico-001 / django__django-11885 "Combine fast delete queries".

Verdict source: issues/pico-001.md ONLY (policy P1).

The issue states that when the deletion Collector takes the fast-delete path
(DELETE FROM table WHERE table.col IN ...), the queries that hit the SAME table
must be combined into one, e.g.

    person.delete()   ->  DELETE FROM person_friends WHERE from_id = :id OR to_id = :id
                          DELETE FROM person        WHERE id = :id
    user.delete()     ->  DELETE FROM entry WHERE created_by_id = :id OR updated_by = :id
                          DELETE FROM user  WHERE id = :id

instead of one query per relation.  This script rebuilds exactly the two model
shapes the issue names (Person.friends = M2M('self'); Entry.created_by /
Entry.updated_by -> User) in a throwaway app, counts the DELETE statements per
table with CaptureQueriesContext, and checks that the right rows really go.

Exit codes (harness contract): 0 = accepted, 1 = not met, 2 = probe broken.
"""

import os
import re
import sys
import traceback

APP_DIR = "/tmp"
APP_NAME = "pico001app"

# The models must live in a real installed app: models registered under a bare
# Meta.app_label are invisible to apps.get_models(), and without that the
# Collector never sees the cascading relations at all.
MODELS_SRC = r'''
from django.db import models


class Person(models.Model):
    friends = models.ManyToManyField("self")


class User(models.Model):
    pass


class Entry(models.Model):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_entries"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="updated_entries"
    )
'''


def write_app():
    pkg = os.path.join(APP_DIR, APP_NAME)
    if not os.path.isdir(pkg):
        os.makedirs(pkg)
    for name, src in (("__init__.py", ""), ("models.py", MODELS_SRC)):
        f = open(os.path.join(pkg, name), "w")
        try:
            f.write(src)
        finally:
            f.close()
    if APP_DIR not in sys.path:
        sys.path.insert(0, APP_DIR)


def statements(captured):
    out = []
    for q in captured:
        sql = q.get("sql") or ""
        if sql.strip():
            out.append(" ".join(sql.split()))
    return out


def _from_table_re(table):
    # "... FROM <table> ..." with any quoting style.  The closing-quote anchor
    # keeps pico001app_person from also matching pico001app_person_friends.
    return re.compile(
        r"\bFROM\s+[\"`\[]?" + re.escape(table) + r"[\"`\]]?(\s|$|\.)", re.I
    )


def deletes_on(sqls, table):
    pat = _from_table_re(table)
    return [s for s in sqls if s.upper().lstrip().startswith("DELETE") and pat.search(s)]


def selects_on(sqls, table):
    pat = _from_table_re(table)
    return [s for s in sqls if s.upper().lstrip().startswith("SELECT") and pat.search(s)]


def all_deletes(sqls):
    return [s for s in sqls if s.upper().lstrip().startswith("DELETE")]


def short(sqls, n=4):
    return " | ".join(s[:160] for s in sqls[:n]) or "<none>"


def main():
    write_app()

    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="pico001",
            ALLOWED_HOSTS=["*"],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[APP_NAME],
            USE_TZ=False,
            DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        )
    django.setup()

    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from pico001app.models import Entry, Person, User

    through = Person._meta.get_field("friends").remote_field.through

    with connection.schema_editor() as editor:
        # create_model() also builds auto-created m2m through tables; only make
        # the through table explicitly if that did not happen.
        editor.create_model(Person)
        if through._meta.db_table not in connection.introspection.table_names():
            editor.create_model(through)
        editor.create_model(User)
        editor.create_model(Entry)

    person_t = Person._meta.db_table
    through_t = through._meta.db_table
    user_t = User._meta.db_table
    entry_t = Entry._meta.db_table

    failures = []

    # ---- probe 1: Entry.created_by / Entry.updated_by -> User ------------
    u1 = User.objects.create()
    u2 = User.objects.create()
    e1 = Entry.objects.create(created_by=u1, updated_by=u1)
    e2 = Entry.objects.create(created_by=u2, updated_by=u1)
    e3 = Entry.objects.create(created_by=u2, updated_by=u2)

    with CaptureQueriesContext(connection) as ctx:
        u1.delete()
    sqls = statements(ctx.captured_queries)

    entry_del = deletes_on(sqls, entry_t)
    user_del = deletes_on(sqls, user_t)
    entry_sel = selects_on(sqls, entry_t)
    total_del = all_deletes(sqls)

    ok1 = (
        len(entry_del) == 1
        and len(user_del) == 1
        and len(total_del) == 2
        and not entry_sel
    )
    print(
        "probe fk-pair: user.delete() with Entry.created_by+Entry.updated_by -> "
        "%d DELETE on %s (want 1), %d DELETE on %s (want 1), %d DELETE total "
        "(want 2), %d SELECT on %s (want 0) :: %s"
        % (
            len(entry_del),
            entry_t,
            len(user_del),
            user_t,
            len(total_del),
            len(entry_sel),
            entry_t,
            short(entry_del + user_del),
        )
    )
    if not ok1:
        failures.append("fk-pair fast deletes not combined into one query per table")

    left_entries = sorted(Entry.objects.values_list("pk", flat=True))
    left_users = sorted(User.objects.values_list("pk", flat=True))
    rows_ok1 = left_entries == [e3.pk] and left_users == [u2.pk]
    print(
        "probe fk-pair rows: entries left %s (want [%s]), users left %s (want [%s])"
        % (left_entries, e3.pk, left_users, u2.pk)
    )
    if not rows_ok1:
        failures.append(
            "fk-pair delete removed the wrong rows (expected e1=%s and e2=%s gone, "
            "e3=%s kept)" % (e1.pk, e2.pk, e3.pk)
        )

    # ---- probe 2: Person.friends = ManyToManyField('self') ---------------
    p1 = Person.objects.create()
    p2 = Person.objects.create()
    p3 = Person.objects.create()
    p1.friends.add(p2)
    p2.friends.add(p3)
    before_links = through.objects.count()

    with CaptureQueriesContext(connection) as ctx2:
        p1.delete()
    sqls2 = statements(ctx2.captured_queries)

    m2m_del = deletes_on(sqls2, through_t)
    person_del = deletes_on(sqls2, person_t)
    m2m_sel = selects_on(sqls2, through_t)
    total_del2 = all_deletes(sqls2)

    ok2 = (
        len(m2m_del) == 1
        and len(person_del) == 1
        and len(total_del2) == 2
        and not m2m_sel
    )
    print(
        "probe m2m-self: person.delete() with friends=M2M('self') -> "
        "%d DELETE on %s (want 1), %d DELETE on %s (want 1), %d DELETE total "
        "(want 2), %d SELECT on %s (want 0) :: %s"
        % (
            len(m2m_del),
            through_t,
            len(person_del),
            person_t,
            len(total_del2),
            len(m2m_sel),
            through_t,
            short(m2m_del + person_del),
        )
    )
    if not ok2:
        failures.append("m2m-self fast deletes not combined into one query per table")

    left_people = sorted(Person.objects.values_list("pk", flat=True))
    after_links = through.objects.count()
    rows_ok2 = left_people == sorted([p2.pk, p3.pk]) and after_links == before_links - 2
    print(
        "probe m2m-self rows: people left %s (want %s), through rows %d -> %d "
        "(want %d, only the p1 links gone)"
        % (
            left_people,
            sorted([p2.pk, p3.pk]),
            before_links,
            after_links,
            before_links - 2,
        )
    )
    if not rows_ok2:
        failures.append("m2m-self delete removed the wrong rows")

    if failures:
        print("ACCEPT: not met -- " + "; ".join(failures))
        return 1
    print(
        "ACCEPT: met -- fast-delete queries are combined per table and the "
        "correct rows were deleted"
    )
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

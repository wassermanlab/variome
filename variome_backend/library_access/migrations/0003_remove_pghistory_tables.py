"""
Migration to remove pghistory event tables and pgtrigger triggers that were
created by the previous history tracking solution (django-pghistory).

This migration is safe to run on:
- Fresh databases (the tables and triggers won't exist, so no-ops)
- Existing PostgreSQL databases upgrading from pghistory (cleans up old objects)
- Non-PostgreSQL databases (trigger removal is skipped, table drops use IF EXISTS)

NOTE: If you wish to preserve historical data from pghistory before running
this migration, export the following tables first:
  - library_access_userprofileevent
  - library_access_libraryuserevent
  - library_access_librarygroupevent
"""

from django.db import migrations


def remove_pgtrigger_triggers(apps, schema_editor):
    """Remove pgtrigger database triggers on PostgreSQL only."""
    if schema_editor.connection.vendor != "postgresql":
        return

    triggers = [
        ("pgtrigger_insert_insert_0d7fe", "auth_group"),
        ("pgtrigger_update_update_2f9f1", "auth_group"),
        ("pgtrigger_insert_insert_c7c6c", "auth_user"),
        ("pgtrigger_update_update_c68de", "auth_user"),
        ("pgtrigger_insert_insert_45284", "user_profile"),
        ("pgtrigger_update_update_f48ee", "user_profile"),
    ]
    with schema_editor.connection.cursor() as cursor:
        for trigger_name, table_name in triggers:
            cursor.execute(
                "DROP TRIGGER IF EXISTS %s ON %s" % (trigger_name, table_name)
            )


class Migration(migrations.Migration):

    dependencies = [
        ("library_access", "0002_add_simple_history"),
    ]

    operations = [
        # Remove pgtrigger triggers before dropping the tables they write to
        migrations.RunPython(
            remove_pgtrigger_triggers,
            reverse_code=migrations.RunPython.noop,
        ),
        # Drop old pghistory event tables (IF EXISTS makes this safe on fresh DBs)
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS library_access_userprofileevent",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS library_access_libraryuserevent",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS library_access_librarygroupevent",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

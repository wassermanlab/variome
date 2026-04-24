"""
Drop the legacy django-pghistory triggers and tables now that all historical
data has been copied to django-auditlog by migration 0002.

Triggers removed:
  pgtrigger_insert_insert_0d7fe  on auth_group
  pgtrigger_update_update_2f9f1  on auth_group
  pgtrigger_insert_insert_c7c6c  on auth_user
  pgtrigger_update_update_c68de  on auth_user
  pgtrigger_insert_insert_45284  on user_profile
  pgtrigger_update_update_f48ee  on user_profile

Tables removed:
  library_access_userprofileevent
  library_access_libraryuserevent
  library_access_librarygroupevent
  pgh_context

NOTE: This migration is temporarily disabled.  To re-enable it, remove the
``return`` statement at the top of ``drop_pghistory_tables``.
"""

from django.db import migrations


_TRIGGERS_TO_DROP = [
    ("pgtrigger_insert_insert_0d7fe", "auth_group"),
    ("pgtrigger_update_update_2f9f1", "auth_group"),
    ("pgtrigger_insert_insert_c7c6c", "auth_user"),
    ("pgtrigger_update_update_c68de", "auth_user"),
    ("pgtrigger_insert_insert_45284", "user_profile"),
    ("pgtrigger_update_update_f48ee", "user_profile"),
]

_TABLES_TO_DROP = [
    "library_access_userprofileevent",
    "library_access_libraryuserevent",
    "library_access_librarygroupevent",
    "pgh_context",
]


def drop_pghistory_tables(apps, schema_editor):
    # TEMPORARILY DISABLED: remove the next line to re-enable this migration.
    return

    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        for trigger_name, table_name in _TRIGGERS_TO_DROP:
            cursor.execute(
                "DROP TRIGGER IF EXISTS %s ON %s" % (
                    connection.ops.quote_name(trigger_name),
                    connection.ops.quote_name(table_name),
                )
            )
        for table_name in _TABLES_TO_DROP:
            cursor.execute(
                "DROP TABLE IF EXISTS %s" % connection.ops.quote_name(table_name)
            )


class Migration(migrations.Migration):

    dependencies = [
        ("library_access", "0002_migrate_pghistory_to_auditlog"),
    ]

    operations = [
        migrations.RunPython(
            drop_pghistory_tables,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

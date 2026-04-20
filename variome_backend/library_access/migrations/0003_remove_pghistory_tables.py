"""
Migration to remove pgtrigger database triggers that were created by the
previous history tracking solution (django-pghistory).

The legacy event tables are intentionally preserved for auditability:
  - library_access_userprofileevent
  - library_access_libraryuserevent
  - library_access_librarygroupevent

Staff can export their contents as CSV from the Django admin site via the
"Export Legacy History" button.
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
            # Both identifiers are hardcoded constants above; quote them for
            # correctness and to make static analysis tools happy.
            quoted = "DROP TRIGGER IF EXISTS %s ON %s" % (
                schema_editor.connection.ops.quote_name(trigger_name),
                schema_editor.connection.ops.quote_name(table_name),
            )
            cursor.execute(quoted)


class Migration(migrations.Migration):

    dependencies = [
        ("library_access", "0001_initial"),
    ]

    operations = [
        # Remove pgtrigger triggers so they no longer write to the legacy tables.
        # The legacy event tables themselves are kept for auditability purposes.
        migrations.RunPython(
            remove_pgtrigger_triggers,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

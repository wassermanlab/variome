"""
Drop the legacy django-pghistory tables now that all historical data has been
copied to django-auditlog by migration 0002.

Tables removed:
  library_access_userprofileevent
  library_access_libraryuserevent
  library_access_librarygroupevent
  pgh_context
"""

from django.db import migrations


_TABLES_TO_DROP = [
    "library_access_userprofileevent",
    "library_access_libraryuserevent",
    "library_access_librarygroupevent",
    "pgh_context",
]


def drop_pghistory_tables(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
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

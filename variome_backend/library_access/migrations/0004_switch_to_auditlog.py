"""
Migration to remove the django-simple-history Historical* tables that were
created in 0002_add_simple_history.  Audit history is now captured by
django-auditlog (see auditlog migrations).

The legacy pghistory event tables are unaffected by this migration.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("library_access", "0003_remove_pghistory_tables"),
        # Ensure auditlog's tables exist before we finish our own migration chain.
        ("auditlog", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(name="HistoricalLibraryGroup"),
        migrations.DeleteModel(name="HistoricalLibraryUser"),
        migrations.DeleteModel(name="HistoricalUserProfile"),
    ]

"""
Migration 0003 is temporarily disabled.

The legacy django-pghistory triggers and tables are kept in place while
both pghistory and django-auditlog run side by side.  This migration will
be re-enabled (and will actually drop those objects) once the transition
period is complete.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("library_access", "0002_migrate_pghistory_to_auditlog"),
    ]

    operations = [
        # No-op: pghistory tables and triggers are intentionally kept.
    ]

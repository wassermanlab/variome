# Generated by Django 4.2.13 on 2024-06-13 14:37

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tracking", "0002_auto_20180918_2014"),
        ("pghistory", "0006_delete_aggregateevent"),
        ("auth", "0012_alter_user_first_name_max_length"),
        (
            "library_access",
            "0002_libraryuserevent_userprofileevent_libraryuser_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="LibraryGroup",
            fields=[],
            options={
                "verbose_name": "User Group",
                "verbose_name_plural": "User Groups",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("auth.group",),
            managers=[
                ("objects", django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name="LibraryPageview",
            fields=[],
            options={
                "verbose_name": "Pageview",
                "verbose_name_plural": "Pageviews",
                "permissions": [
                    ("view_tracking_dashboard", "Can view tracking dashboard")
                ],
                "proxy": True,
                "default_permissions": (),
                "indexes": [],
                "constraints": [],
            },
            bases=("tracking.pageview",),
        ),
        migrations.CreateModel(
            name="LibrarySession",
            fields=[],
            options={
                "verbose_name": "Session",
                "verbose_name_plural": "Sessions",
                "proxy": True,
                "default_permissions": (),
                "indexes": [],
                "constraints": [],
            },
            bases=("tracking.visitor",),
        ),
        migrations.AlterModelOptions(
            name="userprofile",
            options={
                "verbose_name": "User Access Configuration",
                "verbose_name_plural": "User Access Configurations",
            },
        ),
        migrations.CreateModel(
            name="LibraryGroupEvent",
            fields=[
                ("pgh_id", models.AutoField(primary_key=True, serialize=False)),
                ("pgh_created_at", models.DateTimeField(auto_now_add=True)),
                ("pgh_label", models.TextField(help_text="The event label.")),
                ("id", models.IntegerField()),
                ("name", models.CharField(max_length=150, verbose_name="name")),
                (
                    "pgh_context",
                    models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="pghistory.context",
                    ),
                ),
                (
                    "pgh_obj",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="events",
                        to="library_access.librarygroup",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="librarygroup",
            trigger=pgtrigger.compiler.Trigger(
                name="insert_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "library_access_librarygroupevent" ("id", "name", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id") VALUES (NEW."id", NEW."name", _pgh_attach_context(), NOW(), \'insert\', NEW."id"); RETURN NULL;',
                    hash="81ee2e649ec5fb1decae3b23648b19d6d352f6bc",
                    operation="INSERT",
                    pgid="pgtrigger_insert_insert_0d7fe",
                    table="auth_group",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="librarygroup",
            trigger=pgtrigger.compiler.Trigger(
                name="update_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition="WHEN (OLD.* IS DISTINCT FROM NEW.*)",
                    func='INSERT INTO "library_access_librarygroupevent" ("id", "name", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id") VALUES (NEW."id", NEW."name", _pgh_attach_context(), NOW(), \'update\', NEW."id"); RETURN NULL;',
                    hash="aed4ab6908b2bcbb46bbd29c715d44698254e35e",
                    operation="UPDATE",
                    pgid="pgtrigger_update_update_2f9f1",
                    table="auth_group",
                    when="AFTER",
                ),
            ),
        ),
    ]

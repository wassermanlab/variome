# Generated by Django 4.2.13 on 2024-11-13 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0010_alter_variant_var_type"),
        ("ibvl", "0006_initial2_create_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="variomesettings",
            name="example_snv",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="library.variant",
            ),
        ),
    ]
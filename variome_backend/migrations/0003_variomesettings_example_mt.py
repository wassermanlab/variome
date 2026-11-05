import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0004_mt_mtgnomadfrequency_mtvariomefrequency"),
        ("variome_backend", "0002_alter_variomesettings_home_page_message"),
    ]

    operations = [
        migrations.AddField(
            model_name="variomesettings",
            name="example_mt",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"var_type": "M"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="mitochondrial_example_settings",
                to="library.variant",
            ),
        ),
    ]

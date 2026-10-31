import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0003_alter_snv_chr_alter_snv_clinvar_vcv_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MT",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("pos", models.IntegerField(db_index=True)),
                ("ref", models.CharField(max_length=400)),
                ("alt", models.CharField(max_length=255)),
                ("ucsc_url", models.CharField(blank=True, default="", max_length=511)),
                ("mitomap_url", models.CharField(blank=True, default="", max_length=511)),
                ("gnomad_url", models.CharField(blank=True, default="", max_length=511)),
                (
                    "dbsnp_id",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=30
                    ),
                ),
                ("dbsnp_url", models.CharField(blank=True, default="", max_length=511)),
                ("clinvar_url", models.CharField(blank=True, default="", max_length=511)),
                (
                    "clinvar_vcv",
                    models.DecimalField(
                        blank=True,
                        db_index=True,
                        decimal_places=3,
                        max_digits=15,
                        null=True,
                    ),
                ),
                (
                    "variant",
                    models.OneToOneField(
                        db_column="variant",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mt",
                        to="library.variant",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Mitochondrial variants"},
        ),
        migrations.CreateModel(
            name="MtGnomadFrequency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("an", models.PositiveIntegerField(blank=True, null=True)),
                ("ac_hom", models.PositiveIntegerField(blank=True, null=True)),
                ("ac_het", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "af_hom",
                    models.DecimalField(
                        blank=True, decimal_places=10, max_digits=12, null=True
                    ),
                ),
                (
                    "af_het",
                    models.DecimalField(
                        blank=True, decimal_places=10, max_digits=12, null=True
                    ),
                ),
                (
                    "max_hl",
                    models.DecimalField(
                        blank=True, decimal_places=10, max_digits=12, null=True
                    ),
                ),
                (
                    "variant",
                    models.OneToOneField(
                        db_column="variant",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="library.variant",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Mitochondrial gnomAD frequencies"},
        ),
        migrations.CreateModel(
            name="MtVariomeFrequency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("an", models.PositiveIntegerField(blank=True, null=True)),
                ("ac_hom", models.PositiveIntegerField(blank=True, null=True)),
                ("ac_het", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "af_hom",
                    models.DecimalField(
                        blank=True, decimal_places=10, max_digits=12, null=True
                    ),
                ),
                (
                    "af_het",
                    models.DecimalField(
                        blank=True, decimal_places=10, max_digits=12, null=True
                    ),
                ),
                (
                    "max_hl",
                    models.DecimalField(
                        blank=True, decimal_places=10, max_digits=12, null=True
                    ),
                ),
                ("hl_hist", models.TextField(blank=True, default="")),
                (
                    "variant",
                    models.OneToOneField(
                        db_column="variant",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="library.variant",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Mitochondrial Variome frequencies"},
        ),
    ]

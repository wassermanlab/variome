import logging

from django.core.management.base import BaseCommand
from django.db import connection, models

from variome_backend.library.models import SNV, Variant

log = logging.getLogger("management")


class Command(BaseCommand):
    help = (
        "Idempotently creates database indexes that speed up common library "
        "query patterns (SNV search by genomic position, dbSNP id and ClinVar "
        "id, and Variant filtering by var_type). Safe to run repeatedly: "
        "indexes that already exist are left untouched."
    )

    # Every index this command should ensure exists, as (model, Index) pairs.
    # Field choices are based on the filters used in library/views/search.py
    # and the list_filter options in library/admin.
    INDEXES = [
        # snv_search filters/orders on chr + pos (exact position and nearby range lookups)
        (SNV, models.Index(fields=["chr", "pos"], name="snv_chr_pos_idx")),
        # snv_search dbsnp result set does an exact match on dbsnp_id
        (SNV, models.Index(fields=["dbsnp_id"], name="snv_dbsnp_id_idx")),
        # snv_search clinvar result set does an exact match on clinvar_vcv
        (SNV, models.Index(fields=["clinvar_vcv"], name="snv_clinvar_vcv_idx")),
        # VariantAdmin.list_filter filters on var_type
        (Variant, models.Index(fields=["var_type"], name="variant_var_type_idx")),
    ]

    def handle(self, *args, **options):
        for model, index in self.INDEXES:
            table_name = model._meta.db_table

            with connection.cursor() as cursor:
                existing = connection.introspection.get_constraints(cursor, table_name)

            if index.name in existing:
                self.stdout.write(
                    self.style.WARNING(
                        f"'{index.name}' already exists on '{table_name}', skipping"
                    )
                )
                continue

            with connection.schema_editor() as schema_editor:
                schema_editor.add_index(model, index)

            self.stdout.write(
                self.style.SUCCESS(f"Created index '{index.name}' on '{table_name}'")
            )
            log.info(f"Created index {index.name} on {table_name}")

        self.stdout.write(self.style.SUCCESS("Index check complete."))

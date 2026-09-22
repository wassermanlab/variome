import logging

from django.core.management.base import BaseCommand
from django.db import connection, models

from variome_backend.library.models import (
    SNV,
    VariantAnnotation,
)

log = logging.getLogger("management")


class Command(BaseCommand):
    help = (
        "Idempotently removes custom library indexes. Safe to run repeatedly: "
        "indexes that do not exist are skipped."
    )

    INDEXES = [
        # SNV search indexes
        (SNV, models.Index(fields=["chr", "pos"], name="snv_chr_pos_idx")),
        (SNV, models.Index(fields=["dbsnp_id"], name="snv_dbsnp_id_idx")),
        (SNV, models.Index(fields=["clinvar_vcv"], name="snv_clinvar_vcv_idx")),

        # Annotation join index
        (
            VariantAnnotation,
            models.Index(
                fields=["variant_transcript"],
                name="variant_annotation_vt_idx",
            ),
        ),
    ]

    def handle(self, *args, **options):
        for model, index in self.INDEXES:
            table_name = model._meta.db_table

            with connection.cursor() as cursor:
                existing = connection.introspection.get_constraints(
                    cursor,
                    table_name,
                )

            if index.name not in existing:
                self.stdout.write(
                    self.style.WARNING(
                        f"'{index.name}' does not exist on '{table_name}', skipping"
                    )
                )
                continue

            with connection.schema_editor() as schema_editor:
                schema_editor.remove_index(model, index)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Removed index '{index.name}' from '{table_name}'"
                )
            )
            log.info(f"Removed index {index.name} from {table_name}")

        self.stdout.write(self.style.SUCCESS("Index removal complete."))
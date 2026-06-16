"""
Django management command to create indices on key tables/fields for all supported DB backends.
- Uses Django's schema_editor when possible, falls back to raw SQL for custom indices.
- Idempotent: skips indices that already exist.
- Logs all actions.
"""
import logging
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.apps import apps

log = logging.getLogger("management")

# Index specification: (model_label, field(s), index_name)
INDEX_SPECS = [
    ("library.SNV", ["pos"], "snvs_pos_idx"),
    ("library.SNV", ["chr"], "snvs_chr_idx"),
    ("library.SNV", ["dbsnp_id"], "snvs_dbsnp_idx"),
    ("library.SNV", ["clinvar_vcv"], "snvs_clinvar_idx"),
    ("library.Transcript", ["transcript_type"], "transcripts_type_idx"),
    ("library.VariantConsequence", ["variant_transcript"], "variants_consequences_vt_idx"),
    ("library.VariantTranscript", ["transcript"], "variants_transcripts_t_idx"),
    ("library.VariantTranscript", ["variant"], "variants_transcripts_v_idx"),
    ("library.SNV", ["variant"], "snvs_variant_idx"),
    ("library.VariantAnnotation", ["variant_transcript"], "variants_annotations_vt_idx"),
#    ("library.GenomicGnomadFrequency", ["variant"], "gnomad_frequencies_variant_idx"),
    ("library.GenomicVariomeFrequency", ["variant"], "variome_frequencies_variant_idx"),
]

class Command(BaseCommand):
    help = "Create indices on key tables/fields for all supported DB backends."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview index creation actions without making changes.'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        self.stdout.write("\n=== Starting index creation ===\n")
        vendor = connection.vendor
        self.stdout.write(f"Detected DB backend: {vendor}\n")
        if dry_run:
            self.stdout.write("[DRY RUN] No changes will be made.\n")
        with transaction.atomic():
            for model_label, fields, index_name in INDEX_SPECS:
                model = apps.get_model(model_label)
                table = model._meta.db_table
                # Check if index exists
                if self.index_exists(table, index_name):
                    self.stdout.write(f"Index {index_name} already exists on {table}, skipping.")
                    continue
                if dry_run:
                    self.stdout.write(f"[DRY RUN] Would create index {index_name} on {table}({', '.join(fields)})")
                    continue
                # Try to create index
                try:
                    self.create_index(table, fields, index_name)
                    self.stdout.write(f"Created index {index_name} on {table}({', '.join(fields)})")
                except Exception as e:
                    self.stderr.write(f"Failed to create index {index_name} on {table}: {e}\n")
        self.stdout.write("\n=== Index creation complete ===\n")

    def index_exists(self, table, index_name):
        with connection.cursor() as cursor:
            vendor = connection.vendor
            if vendor == "postgresql":
                cursor.execute("""
                    SELECT 1 FROM pg_indexes WHERE tablename = %s AND indexname = %s
                """, [table, index_name])
                return cursor.fetchone() is not None
            elif vendor == "mysql":
                cursor.execute("""
                    SHOW INDEX FROM `{}` WHERE Key_name = %s
                """.format(table), [index_name])
                return cursor.fetchone() is not None
            elif vendor == "oracle":
                cursor.execute("""
                    SELECT 1 FROM user_indexes WHERE table_name = UPPER(%s) AND index_name = UPPER(%s)
                """, [table, index_name])
                return cursor.fetchone() is not None
            else:
                # Fallback: try to create and catch duplicate error
                return False

    def create_index(self, table, fields, index_name):
        vendor = connection.vendor
        if vendor == "postgresql":
            field_list = ", ".join([f'"{f}"' for f in fields])
            sql = f'CREATE INDEX IF NOT EXISTS {index_name} ON "{table}" ({field_list})'
        elif vendor == "mysql":
            field_list = ", ".join([f'`{f}`' for f in fields])
            sql = f'CREATE INDEX {index_name} ON `{table}` ({field_list})'
        elif vendor == "oracle":
            field_list = ", ".join(fields)
            sql = f'CREATE INDEX {index_name} ON {table} ({field_list})'
        else:
            field_list = ", ".join(fields)
            sql = f'CREATE INDEX {index_name} ON {table} ({field_list})'
        with connection.cursor() as cursor:
            cursor.execute(sql)

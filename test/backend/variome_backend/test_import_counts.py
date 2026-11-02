import io
from unittest.mock import patch

from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase

from variome_backend.library.models import Severity, Variant
from variome_backend.management.import_tools import (
    ImportCode, ImportCounts, ImportMessage, VariantImporter,
)


class ImportCountsTests(TestCase):
    def importer(self, **overrides):
        options = {
            "path": "data/fixtures", "batchsize": 2, "dedupe_cache_window": 10000,
            "progress": False, "failfast": False, "ignore-existing": False,
            "batch": True, "delete": False, "out_hyphens": True,
        }
        options.update(overrides)
        return VariantImporter(options)

    def row(self, position):
        return {"variant_id": f"M-{position}-A-G", "var_type": "M", "filter": "PASS"}

    def test_creates_updates_and_ignores_existing_in_both_modes(self):
        for batch in (True, False):
            with self.subTest(batch=batch):
                Variant.objects.all().delete()
                importer = self.importer(batch=batch)
                _, _, counts = importer.import_data([self.row(1), self.row(2)])
                self.assertEqual(counts, ImportCounts(processed=2, created=2))
                _, _, counts = importer.import_data([self.row(1), self.row(3)])
                self.assertEqual(counts, ImportCounts(processed=2, created=1, updated=1))
                changed = self.row(1)
                changed["filter"] = "FAIL"
                importer = self.importer(batch=batch, **{"ignore-existing": True})
                _, _, counts = importer.import_data([changed])
                self.assertEqual(counts, ImportCounts(processed=1, skipped=1))
                self.assertEqual(Variant.objects.get(variant_id=changed["variant_id"]).filter, "PASS")

    def test_failed_bulk_insert_is_not_counted_as_created(self):
        with patch.object(Variant.objects, "bulk_create", side_effect=IntegrityError("test failure")):
            errors, _, counts = self.importer().import_data([self.row(1), self.row(2)])
        self.assertTrue(errors)
        self.assertEqual(counts, ImportCounts(processed=2, failed=2))
        self.assertFalse(Variant.objects.exists())

    def test_failfast_does_not_count_pending_rows_as_written(self):
        importer = self.importer(failfast=True)
        failure = ImportMessage(ImportCode.OBJECT_CREATE_FAILED, "test failure")
        with patch.object(importer, "created_row_object", side_effect=[
            importer.created_row_object(self.row(1)), (False, failure),
        ]):
            _, _, counts = importer.import_data([self.row(1), self.row(2), self.row(3)])
        self.assertEqual(counts, ImportCounts(processed=2, skipped=1, failed=1))
        self.assertFalse(Variant.objects.exists())

    def test_delete_counts_target_model_rows(self):
        Variant.objects.create(**self.row(1))
        _, _, counts = self.importer(delete=True).import_data([self.row(2)])
        self.assertEqual(counts, ImportCounts(processed=1, created=1, deleted=1))


class ImportSummaryTests(TransactionTestCase):
    def run_import(self, **options):
        output = io.StringIO()
        call_command(
            "import_bvl_vcf", vcf_file="", mt_vcf_file="data/fixtures/vcf/mt.vcf",
            progress=False, out_chr=False, stdout=output, stderr=io.StringIO(),
            **options,
        )
        return output.getvalue()

    def test_summary_reports_this_runs_creates_and_updates(self):
        for options, counts in (({}, [158, 158, 0, 0, 0, 0]), ({"batch": False}, [158, 0, 158, 0, 0, 0])):
            output = self.run_import(**options)
            row = next(line for line in output.splitlines() if line.startswith("✅ Variant "))
            self.assertEqual(row.split()[2:8], list(map(str, counts)))

    def test_dry_run_does_not_commit(self):
        output = self.run_import(**{"dry-run": True})
        self.assertIn("DRY RUN", output)
        self.assertFalse(Variant.objects.exists())
        self.assertFalse(Severity.objects.exists())

    def test_table_failure_rolls_back_and_is_reported(self):
        with patch.object(VariantImporter, "import_data", side_effect=RuntimeError("test failure")):
            output = self.run_import(**{"rollback-on-error": True})
        self.assertIn("ROLLED BACK", output)
        self.assertIn("FAILED; table rolled back", output)
        self.assertFalse(Variant.objects.exists())
        self.assertFalse(Severity.objects.exists())

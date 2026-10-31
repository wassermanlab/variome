import csv
import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase

from variome_backend.library.models import Severity, Variant
from variome_backend.management.import_tools import (
    ImportCode, ImportCounts, ImportMessage, VariantImporter, format_import_counts,
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

    def assert_counts(self, counts, **expected):
        self.assertEqual(counts, ImportCounts(**expected))
        self.assertEqual(
            counts.processed, counts.created + counts.updated + counts.skipped + counts.failed
        )

    def test_creates_updates_and_empty_input_ignore_unrelated_database_rows(self):
        for batch in (True, False):
            with self.subTest(batch=batch):
                Variant.objects.all().delete()
                Variant.objects.create(**self.row(99))
                importer = self.importer(batch=batch)
                errors, warnings, counts = importer.import_data([self.row(1), self.row(2), self.row(3)])
                self.assertEqual((errors, warnings), ([], []))
                self.assert_counts(counts, processed=3, created=3)
                errors, warnings, counts = importer.import_data([self.row(1), self.row(2), self.row(4)])
                self.assertEqual((errors, warnings), ([], []))
                self.assert_counts(counts, processed=3, created=1, updated=2)
                _, _, counts = importer.import_data([])
                self.assert_counts(counts)

    def test_ignore_existing_does_not_update_in_either_mode(self):
        for batch in (True, False):
            with self.subTest(batch=batch):
                Variant.objects.all().delete()
                existing = Variant.objects.create(**self.row(1))
                row = self.row(1)
                row["filter"] = "FAIL"
                importer = self.importer(batch=batch, **{"ignore-existing": True})
                errors, warnings, counts = importer.import_data([row, self.row(2)])
                self.assertEqual((errors, warnings), ([], []))
                self.assert_counts(counts, processed=2, created=1, skipped=1)
                existing.refresh_from_db()
                self.assertEqual(existing.filter, "PASS")

    def test_uncleanable_row_is_skipped(self):
        importer = self.importer()
        row = self.row(1)
        row["variant_id"] = "x" * (importer.variant_id_length + 1)
        errors, warnings, counts = importer.import_data([row])
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assert_counts(counts, processed=1, skipped=1)

    def test_nonbatch_ignores_row_created_earlier_in_same_run(self):
        importer = self.importer(batch=False, **{"ignore-existing": True})
        changed = self.row(1)
        changed["filter"] = "FAIL"
        errors, warnings, counts = importer.import_data([self.row(1), changed])
        self.assertEqual((errors, warnings), ([], []))
        self.assert_counts(counts, processed=2, created=1, skipped=1)
        self.assertEqual(Variant.objects.get().filter, "PASS")

    def test_failed_bulk_insert_counts_rows_not_error_messages(self):
        importer = self.importer()
        with patch.object(Variant.objects, "bulk_create", side_effect=IntegrityError("test failure")):
            errors, _, counts = importer.import_data([self.row(1), self.row(2), self.row(3)])
        self.assertEqual(len(errors), 2)
        self.assert_counts(counts, processed=3, failed=3)
        self.assertFalse(Variant.objects.exists())

    def test_failed_final_batch_is_not_counted_as_created(self):
        importer = self.importer()
        bulk_create = Variant.objects.bulk_create

        def insert(objects):
            if len(objects) == 1:
                raise IntegrityError("last batch failed")
            return bulk_create(objects)

        with patch.object(Variant.objects, "bulk_create", side_effect=insert):
            errors, _, counts = importer.import_data([self.row(1), self.row(2), self.row(3)])
        self.assertEqual(len(errors), 1)
        self.assert_counts(counts, processed=3, created=2, failed=1)
        self.assertEqual(Variant.objects.count(), 2)

    def test_update_failure_does_not_count_as_update(self):
        Variant.objects.create(**self.row(1))
        importer = self.importer()
        failure = ImportMessage(ImportCode.OBJECT_UPDATE_FAILED, "test failure")
        with patch.object(importer, "update", return_value=(False, failure)):
            errors, _, counts = importer.import_data([self.row(1), self.row(2)])
        self.assertEqual(errors, [failure])
        self.assert_counts(counts, processed=2, created=1, failed=1)

    def test_nonbatch_upsert_failure(self):
        importer = self.importer(batch=False)
        with patch.object(Variant.objects, "update_or_create", side_effect=IntegrityError("test failure")):
            errors, _, counts = importer.import_data([self.row(1)])
        self.assertEqual(len(errors), 1)
        self.assert_counts(counts, processed=1, failed=1)

    def test_failfast_reports_unwritten_pending_rows_as_skipped(self):
        importer = self.importer(failfast=True)
        create = importer.created_row_object
        failure = ImportMessage(ImportCode.OBJECT_CREATE_FAILED, "test failure")
        with patch.object(importer, "created_row_object", side_effect=[create(self.row(1)), (False, failure)]):
            errors, _, counts = importer.import_data([self.row(1), self.row(2), self.row(3)])
        self.assertEqual(errors, [failure])
        self.assert_counts(counts, processed=2, skipped=1, failed=1)
        self.assertFalse(Variant.objects.exists())

    def test_limit_counts_only_processed_rows(self):
        importer = self.importer()
        importer.limit = 1
        errors, warnings, counts = importer.import_data([self.row(1), self.row(2)])
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assert_counts(counts, processed=1, created=1)

    def test_delete_counts_only_target_model_rows(self):
        Variant.objects.create(**self.row(1))
        Variant.objects.create(**self.row(2))
        _, _, counts = self.importer(delete=True).import_data([self.row(3)])
        self.assert_counts(counts, processed=1, created=1, deleted=2)

    def test_csv_error_does_not_count_pending_creates_as_written(self):
        def rows():
            yield self.row(1)
            raise csv.Error("invalid row")

        errors, _, counts = self.importer().import_data(rows())
        self.assertEqual(len(errors), 1)
        self.assert_counts(counts, processed=1, skipped=1)


class ImportCountFormattingTests(TestCase):
    def test_alignment_and_status(self):
        counts = {
            "Gene": ImportCounts(),
            "Variant Transcript": ImportCounts(processed=12345, created=12344, failed=1),
            "MT": None,
            "Annotation": ImportCounts(),
        }
        lines = format_import_counts(counts, {"Annotation": ["read error"]})
        self.assertTrue(lines[1].startswith("✅ Gene"))
        self.assertTrue(lines[2].startswith("❌ Variant Transcript"))
        self.assertTrue(lines[3].startswith("❌ MT"))
        self.assertTrue(lines[4].startswith("❌ Annotation"))
        self.assertIn("12,345", lines[2])
        self.assertIn("counts unavailable", lines[3])
        # Emoji occupy two terminal cells, so replace them with two spaces.
        display = [line.replace("✅", "  ").replace("❌", "  ") for line in lines]
        for field in ("Processed", "Created", "Updated", "Skipped", "Failed", "Deleted"):
            end = display[0].index(field) + len(field)
            for line in display[1:]:
                self.assertNotEqual(line[end - 1], " ")
                if field != "Deleted":
                    self.assertEqual(line[end:end + 2], "  ")
        self.assertEqual(format_import_counts({}, {}), [])

    def test_duration_column(self):
        counts = {"Gene": ImportCounts(processed=1, created=1), "Variant": ImportCounts()}
        lines = format_import_counts(counts, {}, {"Gene": 3725.25})
        self.assertTrue(lines[0].endswith("Duration"))
        self.assertTrue(lines[1].endswith("1h 2m 5.2s"))
        self.assertTrue(lines[2].endswith(" -"))
        display = [line.replace("✅", "  ") for line in lines]
        self.assertEqual({len(line) for line in display}, {len(display[0])})
        self.assertNotIn("Duration", format_import_counts(counts, {})[0])


class ImportSummaryTests(TransactionTestCase):
    def assert_summary_row(self, output, name, values, icon="✅"):
        row = next(line for line in output.splitlines() if line.startswith(f"{icon} {name} "))
        expected = [icon, *name.split(), *map(str, values)]
        self.assertEqual(row.split()[:len(expected)], expected)
        self.assertRegex(row, r"\d+h \d+m \d+\.\ds$|counts unavailable$")

    def run_import(self, **options):
        output = io.StringIO()
        errors = io.StringIO()
        call_command(
            "import_bvl_vcf", vcf_file="", mt_vcf_file="data/fixtures/vcf/mt.vcf",
            progress=False, out_chr=False, stdout=output, stderr=errors,
            **options,
        )
        return output.getvalue(), errors.getvalue()

    def test_first_and_repeat_import_report_only_this_runs_operations(self):
        Variant.objects.create(variant_id="M-1-A-G", var_type="M")
        output, _ = self.run_import()
        self.assertIn("Import summary (COMMITTED)", output)
        self.assert_summary_row(output, "Variant", [158, 158, 0, 0, 0, 0])
        self.assert_summary_row(output, "Gene", [0, 0, 0, 0, 0, 0])
        output, _ = self.run_import(batch=False)
        self.assert_summary_row(output, "Variant", [158, 0, 158, 0, 0, 0])
        self.assert_summary_row(output, "MT", [158, 0, 158, 0, 0, 0])
        self.assertNotIn("out of", output)

    def test_dry_run_counts_are_explicitly_uncommitted(self):
        output, _ = self.run_import(**{"dry-run": True})
        self.assertIn("DRY RUN: operations below were not committed", output)
        self.assert_summary_row(output, "Variant", [158, 158, 0, 0, 0, 0])
        self.assertFalse(Variant.objects.exists())
        self.assertFalse(Severity.objects.exists())

    def test_rollback_still_prints_counts(self):
        with patch.object(VariantImporter, "created_row_object", return_value=(
            False, ImportMessage(ImportCode.OBJECT_CREATE_FAILED, "test failure")
        )):
            output, _ = self.run_import(**{"rollback-on-error": True})
        self.assertIn("ROLLED BACK: operations below were not committed", output)
        self.assert_summary_row(output, "Variant", [158, 0, 0, 0, 158, 0], icon="❌")
        self.assertFalse(Variant.objects.exists())
        self.assertFalse(Severity.objects.exists())

    def test_table_exception_does_not_report_successful_zero_counts(self):
        with patch.object(VariantImporter, "import_data", side_effect=RuntimeError("test failure")):
            output, _ = self.run_import(**{"rollback-on-error": True})
        self.assertIn("❌ Variant", output)
        self.assertIn("FAILED; table rolled back, counts unavailable", output)
        self.assertFalse(Variant.objects.exists())

    def test_tsv_command_uses_same_counts_and_honors_dry_run(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "variants"
            path.mkdir()
            (path / "variants.tsv").write_text(
                "variant_id\tvar_type\tfilter\nM-1-A-G\tM\tPASS\n",
                encoding="utf-8",
            )
            options = {
                name: False for name in (
                    "severities", "genes", "transcripts", "snvs", "gvfs", "ggfs",
                    "vts", "annotations", "consequences",
                )
            }
            for dry_run in (True, False):
                output = io.StringIO()
                call_command(
                    "import_bvl", path=directory, progress=False, stdout=output,
                    **options, **{"dry-run": dry_run},
                )
                self.assert_summary_row(output.getvalue(), "Variant", [1, 1, 0, 0, 0, 0])
                self.assertEqual(Variant.objects.exists(), not dry_run)


class ImportVerbosityTests(TransactionTestCase):
    def run_import(self, **options):
        output = io.StringIO()
        errors = io.StringIO()
        call_command(
            "import_bvl_vcf", vcf_file="data/fixtures/vcf/variome-tiny.vcf",
            progress=True, stdout=output, stderr=errors, **{"dry-run": True}, **options,
        )
        return output.getvalue(), errors.getvalue()

    def test_default_is_level_two_without_caching_or_timings(self):
        with self.assertLogs("management", level="INFO") as logs, \
                patch("sys.stderr", new_callable=io.StringIO) as sys_stderr:
            output, errors = self.run_import()
        stderr = sys_stderr.getvalue() + errors
        self.assertIn("Import summary (DRY RUN", output)
        self.assertRegex(output, r"Duration: \d+h \d+m \d+\.\ds")
        self.assertIn("variant consequence 1000...", stderr)
        self.assertIn("WARNINGS (1) in Transcript load", stderr)
        self.assertNotIn("Caching chromosome", stderr)
        self.assertNotIn(" took ", stderr)
        self.assertTrue(any("Checking VCF file" in line for line in logs.output))

    def test_level_three_adds_caching_and_timings(self):
        with patch("sys.stderr", new_callable=io.StringIO) as sys_stderr:
            output, errors = self.run_import(verbosity=3)
        stderr = sys_stderr.getvalue() + errors
        self.assertIn("Caching chromosome chr22 from positions", stderr)
        self.assertRegex(stderr, r"variant consequence 1000 \(took [\d.]+ seconds\)")
        self.assertRegex(errors, r"Consequence took \d+h \d+m \d+\.\ds")
        self.assertIn("Duration:", output)

    def test_level_one_shows_only_summary(self):
        with patch("sys.stderr", new_callable=io.StringIO) as sys_stderr, \
                patch("logging.Handler.handle") as handle:
            output, errors = self.run_import(verbosity=1)
        self.assertEqual(sys_stderr.getvalue() + errors, "")
        handle.assert_not_called()
        lines = [line for line in output.splitlines() if line]
        self.assertTrue(lines[0].startswith("Import summary (DRY RUN"))
        self.assertTrue(lines[-1].startswith("Duration: "))

    def test_counted_v_flags_and_help(self):
        from variome_backend.management.commands.import_bvl_vcf import Command

        parser = Command().create_parser("manage.py", "import_bvl_vcf")
        self.assertFalse(hasattr(parser.parse_args([]), "verbosity"))
        for flag, level in (("-v", 1), ("-vv", 2), ("-vvv", 3)):
            self.assertEqual(parser.parse_args([flag]).verbosity, level)
        help_text = parser.format_help()
        for text in ("-vv    (default)", "Updated    existing rows updated",
                     "Duration   wall-clock time", "✅", "❌"):
            self.assertIn(text, help_text)

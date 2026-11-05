import csv
import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase

from variome_backend.library.models import (
    Gene,
    Transcript,
    Variant,
    VariantTranscript,
    VariantAnnotation,
    VariantConsequence,
    SNV,
    MT,
    GenomicVariomeFrequency,
    MtVariomeFrequency,
)
from variome_backend.management.import_tools import Importer

from .helpers import (
    ROOT,
    MT_VCF,
    IMPORT_NUCLEAR_VCF,
    annotate_mt_for_header_edge_case,
    combine_vcf_fixtures,
    select_nuclear_import_record,
)

GENES = {"MIATNB", "LOC107985582"}
SHARED_TRANSCRIPTS = {"ENST00000717151", "ENST00000717153", "XR_001755472.2"}
NUCLEAR_CONSEQUENCES = {
    ("22-27000075-C-T", "intron_variant"),
    ("22-27000075-C-T", "non_coding_transcript_variant"),
}


class ImportVcfTestCase(TransactionTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.nuclear = self.path / "nuclear-fixture-record.vcf"
        select_nuclear_import_record(self.nuclear)
        self.mt = MT_VCF

    def run_import(self, **overrides):
        output, errors = io.StringIO(), io.StringIO()
        options = {
            "vcf_file": str(self.nuclear),
            "mt_vcf_file": str(self.mt),
            "input_tsv_dir": str(ROOT / "data" / "fixtures"),
            "out_chr": False,
            "out_hyphens": True,
            "progress": False,
            "stdout": output,
            "stderr": errors,
        }
        options.update(overrides)
        call_command("import_bvl_vcf", **options)
        self.assertNotIn("ERRORS", errors.getvalue(), errors.getvalue())
        self.assertNotIn("FAILED", output.getvalue(), output.getvalue())
        return output.getvalue()


class MultiVcfImportTests(ImportVcfTestCase):
    def assert_both_genomes(self):
        self.assertEqual(Variant.objects.count(), 159)
        self.assertEqual(
            list(
                Variant.objects.exclude(var_type="M").values_list(
                    "variant_id", flat=True
                )
            ),
            ["22-27000075-C-T"],
        )
        self.assertEqual(MT.objects.count(), 158)
        self.assertEqual(MtVariomeFrequency.objects.count(), 158)
        self.assertEqual(set(Gene.objects.values_list("short_name", flat=True)), GENES)
        self.assertEqual(
            set(Transcript.objects.values_list("transcript_id", flat=True)),
            SHARED_TRANSCRIPTS,
        )
        self.assertEqual(SNV.objects.count(), 1)
        self.assertEqual(
            SNV.objects.get(variant__variant_id="22-27000075-C-T").dbsnp_id,
            "rs8136857",
        )
        self.assertEqual(GenomicVariomeFrequency.objects.count(), 1)
        self.assertEqual(
            GenomicVariomeFrequency.objects.get(
                variant__variant_id="22-27000075-C-T"
            ).an_tot,
            6,
        )
        frequency = MtVariomeFrequency.objects.get(variant__variant_id="M-4440-G-T")
        self.assertEqual((frequency.an, frequency.ac_hom, frequency.ac_het), (1, 0, 1))
        self.assertEqual((float(frequency.af_hom), float(frequency.af_het)), (0, 1))
        self.assertAlmostEqual(float(frequency.max_hl), 0.009923)
        self.assertEqual(frequency.hl_hist, "1,0,0,0,0,0,0,0,0,0")
        frequency = MtVariomeFrequency.objects.get(variant__variant_id="M-8860-A-G")
        self.assertEqual((frequency.an, frequency.ac_hom, frequency.ac_het), (3, 3, 0))
        self.assertAlmostEqual(float(frequency.max_hl), 0.997)
        self.assertEqual(frequency.hl_hist, "0,0,0,0,0,0,0,0,0,3")
        self.assertEqual(
            set(
                MT.objects.filter(pos=9055).values_list(
                    "variant__variant_id", flat=True
                )
            ),
            {"M-9055-G-T", "M-9055-G-A"},
        )
        self.assertEqual(VariantTranscript.objects.count(), 3)
        self.assertEqual(VariantAnnotation.objects.count(), 3)
        self.assertEqual(VariantConsequence.objects.count(), 6)
        self.assertFalse(
            VariantTranscript.objects.filter(variant__var_type="M").exists()
        )

    def test_delete_combines_distinct_files_on_fresh_and_populated_database(self):
        for batch in (True, False):
            with self.subTest(batch=batch):
                for _ in range(2):
                    self.run_import(delete=True, batch=batch)
                    self.assert_both_genomes()

    def test_existing_import_then_delete_preserves_both_genomes(self):
        self.run_import()
        self.assert_both_genomes()
        self.run_import(delete=True)
        self.assert_both_genomes()
        self.run_import()
        self.assert_both_genomes()

    def test_each_table_importer_runs_once_and_counts_each_row_once(self):
        original = Importer.import_data
        invocations = {}
        counts = {}

        def track(importer, row_iter=None):
            name = importer.model.__name__
            invocations[name] = invocations.get(name, 0) + 1
            result = original(importer, row_iter)
            counts[name] = result[2]
            return result

        with patch.object(Importer, "import_data", new=track):
            self.run_import(delete=True)
        self.assertTrue(invocations)
        self.assertTrue(all(count == 1 for count in invocations.values()), invocations)
        self.assertEqual(counts["Variant"].processed, 159)
        self.assertEqual(counts["Variant"].created, 159)
        self.assertEqual(counts["Gene"].created, 2)
        self.assertEqual(counts["Transcript"].created, 3)
        self.assertEqual(counts["MT"].created, 158)
        self.assertEqual(counts["MtVariomeFrequency"].created, 158)
        self.assertTrue(all(count.failed == 0 for count in counts.values()), counts)
        self.assert_both_genomes()

    def test_multiple_consequences_survive_repeated_imports_in_both_modes(self):
        """The nuclear fixture already contains an ampersand-separated consequence."""
        expected = NUCLEAR_CONSEQUENCES
        for batch in (True, False):
            with self.subTest(batch=batch):
                self.run_import(delete=True, batch=batch)
                self.assertEqual(
                    set(
                        VariantConsequence.objects.filter(
                            variant_transcript__variant__variant_id="22-27000075-C-T"
                        ).values_list(
                            "variant_transcript__variant__variant_id",
                            "severity__consequence",
                        )
                    ),
                    expected,
                )
                self.run_import(batch=batch)
                self.assertEqual(VariantConsequence.objects.count(), 6)
                self.assertEqual(
                    set(
                        VariantConsequence.objects.filter(
                            variant_transcript__variant__variant_id="22-27000075-C-T"
                        ).values_list(
                            "variant_transcript__variant__variant_id",
                            "severity__consequence",
                        )
                    ),
                    expected,
                )

    def test_tsv_and_database_outputs_share_header_context_and_deduplication(self):
        self.run_import()
        self.assert_both_genomes()
        output = self.path / "tsv"
        self.run_import(convert_to_tsv=True, tsv_output_dir=str(output))

        def rows(table):
            with (output / table / f"{table}.tsv").open() as stream:
                return list(csv.DictReader(stream, delimiter="\t"))

        self.assertEqual(len(rows("variants")), 159)
        self.assertEqual(
            {row["variant_id"] for row in rows("variants")},
            set(Variant.objects.values_list("variant_id", flat=True)),
        )
        self.assertEqual(len(rows("genes")), 2)
        self.assertEqual(len(rows("transcripts")), 3)
        self.assertEqual(len(rows("variants_transcripts")), 3)
        self.assertEqual(len(rows("variants_annotations")), 3)
        self.assertEqual(len(rows("variants_consequences")), 6)
        self.assertEqual(len(rows("snvs")), 1)
        self.assertEqual(
            next(
                row["dbsnp_id"]
                for row in rows("snvs")
                if row["variant"] == "22-27000075-C-T"
            ),
            "rs8136857",
        )
        self.assertEqual(len(rows("mts")), 158)
        frequencies = {row["variant"]: row for row in rows("mt_variome_frequencies")}
        self.assertEqual(len(frequencies), 158)
        self.assertEqual(frequencies["M-4440-G-T"]["an"], "1")
        self.assertEqual(frequencies["M-4440-G-T"]["hl_hist"], "1,0,0,0,0,0,0,0,0,0")
        self.assertEqual(frequencies["M-8860-A-G"]["ac_hom"], "3")
        self.assertEqual(frequencies["M-8860-A-G"]["hl_hist"], "0,0,0,0,0,0,0,0,0,3")
        self.assertEqual(
            {
                (row["variant"], int(row["an"]), row["hl_hist"])
                for row in frequencies.values()
            },
            set(
                MtVariomeFrequency.objects.values_list(
                    "variant__variant_id", "an", "hl_hist"
                )
            ),
        )

    def test_equivalent_paths_read_combined_file_once(self):
        combined = self.path / "combined.vcf"
        combine_vcf_fixtures(combined, self.nuclear)
        alias = self.path / "alias.vcf"
        alias.symlink_to(combined)
        output = self.path / "same-file-tsv"
        self.run_import(
            vcf_file=str(combined),
            mt_vcf_file=str(alias),
            convert_to_tsv=True,
            tsv_output_dir=str(output),
        )
        lines = (output / "variants" / "variants.tsv").read_text().splitlines()
        self.assertEqual(len(lines), 160)
        self.run_import(vcf_file=str(combined), mt_vcf_file=str(alias), delete=True)
        self.assert_both_genomes()

    def test_disabled_mt_import_does_not_read_mt_file(self):
        self.run_import(mts=False, mt_vcf_file=str(self.path / "missing-mt.vcf"))
        self.assertEqual(
            list(Variant.objects.values_list("variant_id", flat=True)),
            ["22-27000075-C-T"],
        )
        self.assertFalse(MT.objects.exists())

    def test_disabled_tables_are_not_deleted(self):
        self.run_import()
        self.run_import(
            delete=True,
            genes=False,
            variants=False,
            transcripts=False,
            vts=False,
            annotations=False,
            consequences=False,
            severities=False,
            mt_vcf_file="",
        )
        self.assert_both_genomes()


class AnnotatedMtHeaderEdgeCaseTests(ImportVcfTestCase):
    """Canonical MT lacks CSQ: deliberately add nuclear annotations at one site."""

    def setUp(self):
        super().setUp()
        self.mt = self.path / "annotated-mt-header-edge.vcf"
        annotate_mt_for_header_edge_case(self.mt, IMPORT_NUCLEAR_VCF)

    def assert_both_genomes(self):
        # Genes/transcripts are shared across files; only per-variant rows increase.
        self.assertEqual(Variant.objects.count(), 159)
        self.assertEqual(MT.objects.count(), 158)
        self.assertEqual(set(Gene.objects.values_list("short_name", flat=True)), GENES)
        self.assertEqual(Transcript.objects.count(), 3)
        self.assertEqual(VariantTranscript.objects.count(), 6)
        self.assertEqual(VariantAnnotation.objects.count(), 6)
        self.assertEqual(VariantConsequence.objects.count(), 12)
        self.assertEqual(MT.objects.get(pos=4440).dbsnp_id, "rs8136857")
        self.assertEqual(
            set(
                VariantTranscript.objects.filter(
                    variant__variant_id="M-4440-G-T"
                ).values_list("transcript__transcript_id", "hgvsc")
            ),
            {
                ("ENST00000717151", "ENST00000717151.1:n.760-2081C>T"),
                ("ENST00000717153", "ENST00000717153.1:n.346-3392C>T"),
                ("XR_001755472.2", "XR_001755472.2:n.51+1889C>T"),
            },
        )

    def test_multiple_consequences_survive_repeated_imports_in_both_modes(self):
        expected = NUCLEAR_CONSEQUENCES | {
            ("M-4440-G-T", "intron_variant"),
            ("M-4440-G-T", "non_coding_transcript_variant"),
        }
        for batch in (True, False):
            with self.subTest(batch=batch):
                self.run_import(delete=True, batch=batch)
                self.run_import(batch=batch)
                self.assert_both_genomes()
                self.assertEqual(
                    set(
                        VariantConsequence.objects.filter(
                            variant_transcript__variant__variant_id__in=(
                                "22-27000075-C-T",
                                "M-4440-G-T",
                            )
                        ).values_list(
                            "variant_transcript__variant__variant_id",
                            "severity__consequence",
                        )
                    ),
                    expected,
                )

    def test_tsv_preserves_reordered_header_and_shared_annotations(self):
        self.run_import(delete=True)
        self.assert_both_genomes()
        output = self.path / "annotated-tsv"
        self.run_import(convert_to_tsv=True, tsv_output_dir=str(output))
        with (
            output / "variants_transcripts" / "variants_transcripts.tsv"
        ).open() as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        self.assertEqual(len(rows), 6)
        self.assertEqual(
            {row["transcript"] for row in rows if row["variant"] == "M-4440-G-T"},
            SHARED_TRANSCRIPTS,
        )
        with (output / "mts" / "mts.tsv").open() as stream:
            rows = {
                row["variant"]: row for row in csv.DictReader(stream, delimiter="\t")
            }
        self.assertEqual(rows["M-4440-G-T"]["dbsnp_id"], "rs8136857")

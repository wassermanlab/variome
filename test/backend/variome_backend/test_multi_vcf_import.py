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

ROOT = Path(__file__).resolve().parents[3]


class MultiVcfImportTests(TransactionTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.nuclear = self.path / "nuclear.vcf"
        self.mt = self.path / "mt.vcf"
        self.write_vcf(self.nuclear, mitochondrial=False)
        self.write_vcf(self.mt, mitochondrial=True)

    def write_vcf(self, path, mitochondrial):
        fields = [
            "Allele",
            "Consequence",
            "IMPACT",
            "SYMBOL",
            "Gene",
            "Feature_type",
            "Feature",
            "BIOTYPE",
            "HGVSc",
            "HGVSp",
            "Existing_variation",
            "VARIANT_CLASS",
            "SOURCE",
            "SIFT",
            "PolyPhen",
        ]
        if mitochondrial:
            fields.reverse()
        annotations = {
            "Allele": "G",
            "Consequence": "missense_variant",
            "IMPACT": "MODERATE",
            "SYMBOL": "SHARED",
            "Gene": "ENSG_SHARED",
            "Feature_type": "Transcript",
            "Feature": "ENST_SHARED",
            "BIOTYPE": "protein_coding",
            "HGVSc": "ENST_SHARED:c.1A>G",
            "HGVSp": "ENSP_SHARED:p.Lys1Arg",
            "Existing_variation": "rs222" if mitochondrial else "rs111",
            "VARIANT_CLASS": "SNV",
            "SOURCE": "Ensembl",
            "SIFT": "",
            "PolyPhen": "",
        }
        metrics = (
            "AN=10;AC_hom=0;AC_het=1;AF_hom=0;AF_het=0.1"
            if mitochondrial
            else "AN=20;AC=1;AF=0.05;numhomalt=0"
        )
        chromosome = "MT" if mitochondrial else "1"
        position = 200 if mitochondrial else 100
        metric_headers = [
            ("AN", "Integer"),
            ("AC", "Integer"),
            ("AF", "Float"),
            ("numhomalt", "Integer"),
            ("AC_hom", "Integer"),
            ("AC_het", "Integer"),
            ("AF_hom", "Float"),
            ("AF_het", "Float"),
        ]
        path.write_text(
            "##fileformat=VCFv4.2\n"
            f"##contig=<ID={chromosome}>\n"
            '##FILTER=<ID=PASS,Description="Passed">\n'
            + "".join(
                f'##INFO=<ID={name},Number=A,Type={kind},Description="Metric">\n'
                for name, kind in metric_headers
            )
            + '##INFO=<ID=CSQ,Number=.,Type=String,Description="VEP. Format: '
            + "|".join(fields)
            + '">\n'
            + "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
            + f"{chromosome}\t{position}\t.\tA\tG\t99\tPASS\t{metrics};CSQ="
            + "|".join(annotations[field] for field in fields)
            + "\n",
            encoding="utf-8",
        )

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

    def assert_both_genomes(self):
        self.assertEqual(
            set(Variant.objects.values_list("variant_id", flat=True)),
            {"1-100-A-G", "M-200-A-G"},
        )
        self.assertEqual(Gene.objects.count(), 1)
        self.assertEqual(Transcript.objects.count(), 1)
        self.assertEqual(Transcript.objects.get().gene.short_name, "SHARED")
        self.assertEqual(SNV.objects.get().dbsnp_id, "rs111")
        self.assertEqual(MT.objects.get().dbsnp_id, "rs222")
        self.assertEqual(GenomicVariomeFrequency.objects.get().an_tot, 20)
        self.assertEqual(MtVariomeFrequency.objects.get().an, 10)
        self.assertEqual(VariantTranscript.objects.count(), 2)
        self.assertEqual(VariantAnnotation.objects.count(), 2)
        self.assertEqual(VariantConsequence.objects.count(), 2)
        self.assertTrue(
            all(
                value == "ENSP_SHARED:p.Lys1Arg"
                for value in VariantAnnotation.objects.values_list("hgvsp", flat=True)
            )
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
        self.assertEqual(counts["Variant"].processed, 2)
        self.assertEqual(counts["Variant"].created, 2)
        self.assertEqual(counts["Gene"].created, 1)
        self.assertEqual(counts["Transcript"].created, 1)
        self.assert_both_genomes()

    def test_multiple_consequences_survive_repeated_imports_in_both_modes(self):
        self.nuclear.write_text(
            self.nuclear.read_text().replace(
                "missense_variant|", "missense_variant&splice_region_variant|"
            )
        )
        for batch in (True, False):
            with self.subTest(batch=batch):
                self.run_import(delete=True, batch=batch)
                expected = set(
                    VariantConsequence.objects.values_list(
                        "variant_transcript__variant__variant_id",
                        "severity__consequence",
                    )
                )
                self.assertEqual(
                    expected,
                    {
                        ("1-100-A-G", "missense_variant"),
                        ("1-100-A-G", "splice_region_variant"),
                        ("M-200-A-G", "missense_variant"),
                    },
                )
                self.run_import(batch=batch)
                self.assertEqual(VariantConsequence.objects.count(), 3)
                self.assertEqual(
                    set(
                        VariantConsequence.objects.values_list(
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

        self.assertEqual(
            {row["variant_id"] for row in rows("variants")},
            set(Variant.objects.values_list("variant_id", flat=True)),
        )
        self.assertEqual(len(rows("genes")), 1)
        self.assertEqual(len(rows("transcripts")), 1)
        self.assertEqual(len(rows("variants_transcripts")), 2)
        self.assertEqual(len(rows("variants_annotations")), 2)
        self.assertEqual(len(rows("variants_consequences")), 2)
        self.assertEqual(rows("snvs")[0]["dbsnp_id"], "rs111")
        self.assertEqual(rows("mts")[0]["dbsnp_id"], "rs222")

    def test_equivalent_paths_read_combined_file_once(self):
        combined = self.path / "combined.vcf"
        text = self.nuclear.read_text().replace(
            "##contig=<ID=1>\n", "##contig=<ID=1>\n##contig=<ID=MT>\n"
        )
        combined.write_text(
            text + "MT\t200\t.\tA\tG\t99\tPASS\tAN=10;AC_hom=0;AC_het=1\n"
        )
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
        self.assertEqual(len(lines), 3)
        self.run_import(vcf_file=str(combined), mt_vcf_file=str(alias), delete=True)
        self.assertEqual(Variant.objects.count(), 2)
        self.assertEqual(SNV.objects.count(), 1)
        self.assertEqual(MT.objects.count(), 1)

    def test_disabled_mt_import_does_not_read_mt_file(self):
        self.mt.unlink()
        self.run_import(mts=False)
        self.assertEqual(
            list(Variant.objects.values_list("variant_id", flat=True)), ["1-100-A-G"]
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

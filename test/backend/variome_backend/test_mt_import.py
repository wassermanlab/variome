import gzip
import io
import logging
import tempfile
from pathlib import Path

import vcfpy
from django.core.management import call_command
from django.test import TransactionTestCase

from variome_backend.library.models import (
    MT, SNV, Variant, VariantTranscript,
    GenomicVariomeFrequency, MtVariomeFrequency, MtGnomadFrequency,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "vcf"
SUPPLIED_MT = ROOT / "data" / "fixtures" / "vcf" / "mt.vcf"


class MitochondrialImportTests(TransactionTestCase):
    def import_vcf(self, filename, **options):
        output = io.StringIO()
        errors = io.StringIO()
        call_command(
            "import_bvl_vcf",
            vcf_file=str(filename),
            mt_vcf_file=str(filename),
            input_tsv_dir=str(ROOT / "data" / "fixtures"),
            out_chr=False,
            out_hyphens=True,
            progress=False,
            stdout=output,
            stderr=errors,
            **options,
        )
        self.assertNotIn("ERRORS", errors.getvalue(), errors.getvalue())

    def test_supplied_mt_import_without_csq(self):
        for batch in (True, False):
            with self.subTest(batch=batch):
                self.import_vcf(SUPPLIED_MT, batch=batch)
                self.assertEqual(Variant.objects.count(), 158)
                self.assertEqual(MT.objects.count(), 158)
                self.assertFalse(Variant.objects.exclude(var_type="M").exists())
                variant = Variant.objects.get(variant_id="M-4440-G-T")
                metadata = MT.objects.get(variant=variant)
                self.assertEqual((metadata.pos, metadata.ref, metadata.alt), (4440, "G", "T"))
                self.assertEqual(metadata.dbsnp_id, "")
                self.assertIsNone(metadata.clinvar_vcv)
                frequency = MtVariomeFrequency.objects.get(variant=variant)
                self.assertEqual(frequency.an, 1)
                self.assertEqual((frequency.ac_hom, frequency.ac_het), (0, 1))
                self.assertEqual((float(frequency.af_hom), float(frequency.af_het)), (0, 1))
                self.assertAlmostEqual(float(frequency.max_hl), 0.009923)
                self.assertEqual(frequency.hl_hist, "1,0,0,0,0,0,0,0,0,0")
                frequency = MtVariomeFrequency.objects.get(variant__variant_id="M-8860-A-G")
                self.assertEqual(frequency.an, 3)
                self.assertEqual((frequency.ac_hom, frequency.ac_het), (3, 0))
                self.assertEqual((float(frequency.af_hom), float(frequency.af_het)), (1, 0))
                self.assertEqual(frequency.hl_hist, "0,0,0,0,0,0,0,0,0,3")
                self.assertAlmostEqual(float(frequency.max_hl), 0.997)
                self.assertTrue(MT.objects.filter(variant__variant_id="M-9055-G-T").exists())
                self.assertTrue(MT.objects.filter(variant__variant_id="M-9055-G-A").exists())
                self.assertFalse(VariantTranscript.objects.exists())
                self.assertFalse(SNV.objects.exists())
                self.assertFalse(GenomicVariomeFrequency.objects.exists())

    def test_default_run_imports_nuclear_and_mt_vcfs(self):
        call_command("import_bvl_vcf", progress=False, stdout=io.StringIO(), stderr=io.StringIO())
        self.assertEqual(Variant.objects.filter(var_type="M").count(), 158)
        self.assertEqual(Variant.objects.exclude(var_type="M").count(), 73)
        self.assertEqual(MT.objects.count(), 158)
        self.assertEqual(MtVariomeFrequency.objects.count(), 158)
        self.assertEqual(SNV.objects.count(), 73)
        self.assertTrue(Variant.objects.filter(variant_id="chrM-9055-G-A").exists())

    def test_separate_files_ignore_records_of_the_other_genome(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.vcf"
            path.write_text(
                "##fileformat=VCFv4.2\n"
                "##contig=<ID=chr1>\n##contig=<ID=chrM>\n"
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
                "chr1\t100\t.\tA\tG\t.\tPASS\t.\n"
                "chrM\t200\t.\tA\tG\t.\tPASS\t.\n",
                encoding="utf-8",
            )
            for args, expected in (
                ({"vcf_file": str(path), "mt_vcf_file": ""}, ["1-100-A-G"]),
                ({"vcf_file": "", "mt_vcf_file": str(path)}, ["M-200-A-G"]),
                ({"vcf_file": str(path), "mt_vcf_file": str(path)}, ["1-100-A-G", "M-200-A-G"]),
            ):
                with self.subTest(**args):
                    Variant.objects.all().delete()
                    with self.assertLogs("management", level="WARNING") as logs:
                        logging.getLogger("management").warning("sentinel")
                        call_command(
                            "import_bvl_vcf", out_chr=False, progress=False,
                            stdout=io.StringIO(), stderr=io.StringIO(), **args,
                        )
                    self.assertEqual(
                        sorted(Variant.objects.values_list("variant_id", flat=True)), expected
                    )
                    self.assertEqual(MT.objects.count(), expected.count("M-200-A-G"))
                    ignored = [line for line in logs.output if "Ignoring 1 " in line]
                    self.assertEqual(len(ignored), 0 if len(expected) == 2 else 1)

    def test_supplied_mt_gzipped_conversion_without_csq(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mt.vcf.gz"
            with gzip.open(path, "wb") as stream:
                stream.write(SUPPLIED_MT.read_bytes())
            self.import_vcf(path, convert_to_tsv=True, tsv_output_dir=directory)
            metadata = (Path(directory) / "mts" / "mts.tsv").read_text()
            frequencies = (
                Path(directory) / "mt_variome_frequencies" / "mt_variome_frequencies.tsv"
            ).read_text()
        self.assertEqual(len(metadata.splitlines()), 159)
        self.assertEqual(len(frequencies.splitlines()), 159)
        for variant in ("M-4440-G-T", "M-9055-G-T", "M-9055-G-A"):
            self.assertIn(variant, metadata)
            self.assertIn(variant, frequencies)
        self.assertFalse(Variant.objects.exists())

    def test_supplied_mt_mixed_with_nuclear_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.vcf"
            with vcfpy.Reader.from_path(str(SUPPLIED_MT)) as mt_reader:
                header = mt_reader.header.copy()
                with vcfpy.Reader.from_path(str(SUPPLIED_MT.with_name("variome-tiny.vcf"))) as nuclear_reader:
                    nuclear_record = next(nuclear_reader)
                    for line in nuclear_reader.header.lines:
                        if line.key in ("INFO", "FORMAT", "FILTER", "contig"):
                            if not header.has_header_line(line.key, line.id):
                                header.add_line(line.copy())
                nuclear_record.FORMAT = ["GT"]
                nuclear_record.calls = [
                    vcfpy.Call(sample, {"GT": "./."}) for sample in header.samples.names
                ]
                nuclear_record.update_calls(nuclear_record.calls)
                with vcfpy.Writer.from_path(str(path), header) as writer:
                    writer.write_record(nuclear_record)
                    for record in mt_reader:
                        writer.write_record(record)
            self.import_vcf(path)
        self.assertEqual(Variant.objects.count(), 159)
        self.assertEqual(MT.objects.count(), 158)
        self.assertEqual(SNV.objects.count(), 1)
        self.assertEqual(GenomicVariomeFrequency.objects.count(), 1)

    def test_supplied_mt_gnomad_intersection_includes_second_alt(self):
        with tempfile.TemporaryDirectory() as directory:
            gnomad = Path(directory) / "gnomad.tsv"
            gnomad.write_text(
                "chromosome\tposition\tref\talt\tAN\tAC_hom\tAC_het\tAF_hom\tAF_het\tmax_observed_heteroplasmy\n"
                "MT\t9055\tG\tA\t1000\t0\t10\t0\t0.01\t0.9\n",
                encoding="utf-8",
            )
            self.import_vcf(SUPPLIED_MT, mt_gnomad_tsv=str(gnomad))
        frequency = MtGnomadFrequency.objects.get()
        self.assertEqual(frequency.variant.variant_id, "M-9055-G-A")
        self.assertEqual(frequency.an, 1000)

    def test_ibvl_import_creates_mitochondrial_models_and_annotations(self):
        self.import_vcf(FIXTURES / "mock_mt.vcf")
        variant = Variant.objects.get(variant_id="M-8602-T-C")
        self.assertEqual(variant.var_type, "M")
        self.assertEqual(MT.objects.get(variant=variant).dbsnp_id, "rs879029014")
        frequency = MtVariomeFrequency.objects.get(variant=variant)
        self.assertEqual(frequency.an, 100)
        self.assertEqual(frequency.ac_het, 10)
        self.assertEqual(frequency.hl_hist, "5,10,15,8,6,4,3,2,1,1")
        self.assertTrue(VariantTranscript.objects.filter(variant=variant).exists())
        self.assertFalse(SNV.objects.exists())
        self.assertFalse(GenomicVariomeFrequency.objects.exists())

    def test_variome_import_update_and_nonbatch(self):
        path = FIXTURES / "mock_mt_variome.vcf"
        self.import_vcf(path)
        self.assertEqual(MT.objects.count(), 3)
        self.assertEqual(MtVariomeFrequency.objects.count(), 2)
        variant = Variant.objects.get(variant_id="M-8603-TA-T")
        self.assertEqual(MT.objects.get(variant=variant).clinvar_vcv, 456)
        self.assertEqual(MtVariomeFrequency.objects.get(variant=variant).ac_hom, 0)
        MtVariomeFrequency.objects.filter(variant=variant).update(ac_hom=99)
        self.import_vcf(path)
        self.assertEqual(MtVariomeFrequency.objects.get(variant=variant).ac_hom, 0)
        self.import_vcf(path, batch=False)
        self.assertEqual(MT.objects.count(), 3)
        self.assertEqual(MtVariomeFrequency.objects.count(), 2)
        self.assertFalse(SNV.objects.exists())

    def test_gzipped_import_and_gnomad_intersection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mt.vcf.gz"
            with gzip.open(path, "wb") as stream:
                stream.write((FIXTURES / "mock_mt_variome.vcf").read_bytes())
            gnomad = Path(directory) / "gnomad.tsv"
            gnomad.write_text(
                "chromosome\tposition\tref\talt\tAN\tAC_hom\tAC_het\tAF_hom\tAF_het\tmax_observed_heteroplasmy\n"
                "MT\t8602\tT\tC\t1000\t0\t10\t0\t0.01\t0.9\n"
                "MT\t9999\tA\tC\t1000\t0\t10\t0\t0.01\t0.9\n",
                encoding="utf-8",
            )
            self.import_vcf(path, mt_gnomad_tsv=str(gnomad))
        frequency = MtGnomadFrequency.objects.get()
        self.assertEqual(frequency.variant.variant_id, "M-8602-T-C")
        self.assertEqual(frequency.an, 1000)
        self.assertEqual(frequency.ac_hom, 0)

    def test_conversion_writes_mt_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            self.import_vcf(
                FIXTURES / "mock_mt.vcf",
                convert_to_tsv=True,
                tsv_output_dir=directory,
            )
            metadata = (Path(directory) / "mts" / "mts.tsv").read_text()
            frequencies = (
                Path(directory) / "mt_variome_frequencies" / "mt_variome_frequencies.tsv"
            ).read_text()
        self.assertIn("M-8602-T-C", metadata)
        self.assertIn("5,10,15,8,6,4,3,2,1,1", frequencies)
        self.assertFalse(Variant.objects.exists())

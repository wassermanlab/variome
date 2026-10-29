import gzip
import io
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TransactionTestCase

from variome_backend.library.models import (
    MT, SNV, Variant, VariantTranscript,
    GenomicVariomeFrequency, MtVariomeFrequency, MtGnomadFrequency,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "vcf"


class MitochondrialImportTests(TransactionTestCase):
    def import_vcf(self, filename, **options):
        output = io.StringIO()
        errors = io.StringIO()
        call_command(
            "import_bvl_vcf",
            vcf_file=str(filename),
            input_tsv_dir=str(ROOT / "data" / "fixtures"),
            out_chr=False,
            out_hyphens=True,
            progress=False,
            stdout=output,
            stderr=errors,
            **options,
        )
        self.assertNotIn("ERRORS", errors.getvalue(), errors.getvalue())

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

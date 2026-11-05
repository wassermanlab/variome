import gzip
import io
import logging
import tempfile
from pathlib import Path

import vcfpy
from django.core.management import call_command
from django.test import TransactionTestCase

from variome_backend.library.models import (
    MT,
    SNV,
    Variant,
    VariantTranscript,
    GenomicVariomeFrequency,
    MtVariomeFrequency,
    MtGnomadFrequency,
)

from .helpers import ROOT, MT_VCF, IMPORT_NUCLEAR_VCF, combine_vcf_fixtures

FIXTURES = ROOT / "data" / "fixtures" / "vcf"
SUPPLIED_MT = MT_VCF


class MitochondrialImportTests(TransactionTestCase):
    def test_canonical_mt_format_and_samples_contract(self):
        """Lock the real input schema independently of importer output."""
        with vcfpy.Reader.from_path(str(SUPPLIED_MT)) as reader:
            self.assertEqual(reader.header.samples.names, ["HG002", "HG003", "HG004"])
            self.assertNotIn("CSQ", reader.header.info_ids())
            self.assertEqual(
                set(reader.header.format_ids()),
                {
                    "AD",
                    "AF",
                    "DP",
                    "F1R2",
                    "F2R1",
                    "FAD",
                    "GQ",
                    "GT",
                    "PGT",
                    "PID",
                    "PL",
                    "PS",
                    "SB",
                },
            )
            for name, number, kind in (
                ("GT", 1, "String"),
                ("AD", "R", "Integer"),
                ("AF", "A", "Float"),
                ("DP", 1, "Integer"),
            ):
                field = reader.header.get_format_field_info(name)
                self.assertEqual((field.number, field.type), (number, kind))
            records = {record.POS: record for record in reader}
        self.assertEqual(len(records), 157)
        record = records[4440]
        self.assertEqual(record.CHROM, "chrM")
        self.assertEqual(
            record.FORMAT, ["GT", "AD", "AF", "DP", "F1R2", "F2R1", "FAD", "SB"]
        )
        self.assertEqual(record.INFO["AN"], 2)
        self.assertEqual(
            [(call.sample, call.data["GT"], call.data["AF"]) for call in record.calls],
            [
                ("HG002", "0/1", [0.009923]),
                ("HG003", "./.", []),
                ("HG004", "./.", []),
            ],
        )
        self.assertEqual(
            [call.data["AF"] for call in records[8860].calls],
            [[0.997], [0.997], [0.997]],
        )
        self.assertEqual([alt.value for alt in records[9055].ALT], ["T", "A"])
        self.assertEqual(
            [call.data["AF"] for call in records[9055].calls],
            [[0.01, None], [None, 0.997], []],
        )

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
        self.assertNotIn("FAILED", output.getvalue(), output.getvalue())

    def test_supplied_mt_import_without_csq(self):
        for batch in (True, False):
            with self.subTest(batch=batch):
                self.import_vcf(SUPPLIED_MT, batch=batch)
                self.assertEqual(Variant.objects.count(), 158)
                self.assertEqual(MT.objects.count(), 158)
                self.assertFalse(Variant.objects.exclude(var_type="M").exists())
                variant = Variant.objects.get(variant_id="M-4440-G-T")
                metadata = MT.objects.get(variant=variant)
                self.assertEqual(
                    (metadata.pos, metadata.ref, metadata.alt), (4440, "G", "T")
                )
                self.assertEqual(metadata.dbsnp_id, "")
                self.assertIsNone(metadata.clinvar_vcv)
                frequency = MtVariomeFrequency.objects.get(variant=variant)
                self.assertEqual(frequency.an, 1)
                self.assertEqual((frequency.ac_hom, frequency.ac_het), (0, 1))
                self.assertEqual(
                    (float(frequency.af_hom), float(frequency.af_het)), (0, 1)
                )
                self.assertAlmostEqual(float(frequency.max_hl), 0.009923)
                self.assertEqual(frequency.hl_hist, "1,0,0,0,0,0,0,0,0,0")
                frequency = MtVariomeFrequency.objects.get(
                    variant__variant_id="M-8860-A-G"
                )
                self.assertEqual(frequency.an, 3)
                self.assertEqual((frequency.ac_hom, frequency.ac_het), (3, 0))
                self.assertEqual(
                    (float(frequency.af_hom), float(frequency.af_het)), (1, 0)
                )
                self.assertEqual(frequency.hl_hist, "0,0,0,0,0,0,0,0,0,3")
                self.assertAlmostEqual(float(frequency.max_hl), 0.997)
                self.assertTrue(
                    MT.objects.filter(variant__variant_id="M-9055-G-T").exists()
                )
                self.assertTrue(
                    MT.objects.filter(variant__variant_id="M-9055-G-A").exists()
                )
                self.assertFalse(VariantTranscript.objects.exists())
                self.assertFalse(SNV.objects.exists())
                self.assertFalse(GenomicVariomeFrequency.objects.exists())

    def test_default_run_imports_nuclear_and_mt_vcfs(self):
        call_command(
            "import_bvl_vcf", progress=False, stdout=io.StringIO(), stderr=io.StringIO()
        )
        self.assertEqual(Variant.objects.filter(var_type="M").count(), 158)
        self.assertEqual(Variant.objects.exclude(var_type="M").count(), 73)
        self.assertEqual(MT.objects.count(), 158)
        self.assertEqual(MtVariomeFrequency.objects.count(), 158)
        self.assertEqual(SNV.objects.count(), 73)
        self.assertTrue(Variant.objects.filter(variant_id="chrM-9055-G-A").exists())

    def test_separate_files_ignore_records_of_the_other_genome(self):
        """Combine unchanged fixture records to exercise nuclear/MT input scopes."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.vcf"
            combine_vcf_fixtures(path, IMPORT_NUCLEAR_VCF)
            for args, nuclear_count, mt_count, ignored_count in (
                ({"vcf_file": str(path), "mt_vcf_file": ""}, 73, 0, 157),
                ({"vcf_file": "", "mt_vcf_file": str(path)}, 0, 158, 73),
                (
                    {"vcf_file": str(path), "mt_vcf_file": str(path)},
                    73,
                    158,
                    0,
                ),
            ):
                with self.subTest(**args):
                    Variant.objects.all().delete()
                    output, errors = io.StringIO(), io.StringIO()
                    with self.assertLogs("management", level="WARNING") as logs:
                        logging.getLogger("management").warning("sentinel")
                        call_command(
                            "import_bvl_vcf",
                            out_chr=False,
                            progress=False,
                            stdout=output,
                            stderr=errors,
                            **args,
                        )
                    self.assertNotIn("FAILED", output.getvalue(), output.getvalue())
                    self.assertNotIn("ERRORS", errors.getvalue(), errors.getvalue())
                    self.assertEqual(
                        Variant.objects.exclude(var_type="M").count(), nuclear_count
                    )
                    self.assertEqual(
                        Variant.objects.filter(variant_id="22-27000075-C-T").exists(),
                        bool(nuclear_count),
                    )
                    self.assertEqual(Variant.objects.count(), nuclear_count + mt_count)
                    self.assertEqual(MT.objects.count(), mt_count)
                    if mt_count:
                        self.assertTrue(
                            MT.objects.filter(variant__variant_id="M-4440-G-T").exists()
                        )
                        self.assertEqual(
                            set(
                                MT.objects.filter(pos=9055).values_list(
                                    "alt", flat=True
                                )
                            ),
                            {"T", "A"},
                        )
                    ignored = [line for line in logs.output if "Ignoring " in line]
                    self.assertEqual(len(ignored), 1 if ignored_count else 0)
                    if ignored_count:
                        self.assertIn(f"Ignoring {ignored_count} ", ignored[0])

    def test_supplied_mt_gzipped_conversion_without_csq(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mt.vcf.gz"
            with gzip.open(path, "wb") as stream:
                stream.write(SUPPLIED_MT.read_bytes())
            self.import_vcf(path, convert_to_tsv=True, tsv_output_dir=directory)
            metadata = (Path(directory) / "mts" / "mts.tsv").read_text()
            frequencies = (
                Path(directory)
                / "mt_variome_frequencies"
                / "mt_variome_frequencies.tsv"
            ).read_text()
        self.assertEqual(len(metadata.splitlines()), 159)
        self.assertEqual(len(frequencies.splitlines()), 159)
        for variant in ("M-4440-G-T", "M-9055-G-T", "M-9055-G-A"):
            self.assertIn(variant, metadata)
            self.assertIn(variant, frequencies)
        self.assertFalse(Variant.objects.exists())

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
        """Retain compatibility coverage for the legacy nonstandard IBVL dialect."""
        self.import_vcf(FIXTURES / "mt_ibvl_legacy.vcf")
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
        path = SUPPLIED_MT
        self.import_vcf(path)
        self.assertEqual(MT.objects.count(), 158)
        self.assertEqual(MtVariomeFrequency.objects.count(), 158)
        variant = Variant.objects.get(variant_id="M-4440-G-T")
        self.assertIsNone(MT.objects.get(variant=variant).clinvar_vcv)
        self.assertEqual(MtVariomeFrequency.objects.get(variant=variant).ac_hom, 0)
        MtVariomeFrequency.objects.filter(variant=variant).update(ac_hom=99)
        self.import_vcf(path)
        self.assertEqual(MtVariomeFrequency.objects.get(variant=variant).ac_hom, 0)
        self.import_vcf(path, batch=False)
        self.assertEqual(MT.objects.count(), 158)
        self.assertEqual(MtVariomeFrequency.objects.count(), 158)
        self.assertFalse(SNV.objects.exists())

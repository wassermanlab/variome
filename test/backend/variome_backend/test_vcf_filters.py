"""
Unit tests for VCF CallFilter classes.

These tests validate the expected input/output structures for each CallFilter
using real VCF fixture files.

To focus on a single test (similar to fit() in Mocha):

1. Use unittest.skip decorator on other tests:
   @unittest.skip("Temporarily skipping")

2. Run specific test from command line:
    python -m unittest variome_backend.tests.test_vcf_filters.TestTranscriptsCallFilter
    python -m unittest variome_backend.tests.test_vcf_filters.TestTranscriptsCallFilter.test_transform_output_structure

3. Use pytest with -k flag (if pytest is installed):
    pytest variome_backend/tests/test_vcf_filters.py -k "Transcripts"

4. Use environment variable or attribute (demonstrated below with FOCUS_TEST)
"""

import unittest
import os
import copy

from variome_backend.management.VCFCallFilters.CallFilter import CallFilter
from variome_backend.management.VCFCallFilters.GenesCallFilter import GenesCallFilter
from variome_backend.management.VCFCallFilters.TranscriptsCallFilter import (
    TranscriptsCallFilter,
)
from variome_backend.management.VCFCallFilters.VariantsCallFilter import (
    VariantsCallFilter,
)
from variome_backend.management.VCFCallFilters.VariantsTranscriptsCallFilter import (
    VariantsTranscriptsCallFilter,
)
from variome_backend.management.VCFCallFilters.VariantsAnnotationsCallFilter import (
    VariantsAnnotationsCallFilter,
)
from variome_backend.management.VCFCallFilters.VariantsConsequencesCallFilter import (
    VariantsConsequencesCallFilter,
)
from variome_backend.management.VCFCallFilters.SnvsCallFilter import SnvsCallFilter
from variome_backend.management.VCFCallFilters.MtsCallFilter import MtsCallFilter
from variome_backend.management.VCFCallFilters.GenomicBvlFrequenciesCallFilter import (
    GenomicBvlFrequenciesCallFilter,
)
from variome_backend.management.VCFCallFilters.MtBvlFrequenciesCallFilter import (
    MtBvlFrequenciesCallFilter,
)
from variome_backend.management.VCFCallFilters.MtGnomadFrequenciesCallFilter import (
    MtGnomadFrequenciesCallFilter,
)
import tempfile
from pathlib import Path
from unittest.mock import patch

from variome_backend.management.vcf_import_settings import VcfImportSettings

from .helpers import (
    ROOT,
    MT_VCF,
    ANNOTATED_MT_VCF,
    NUCLEAR_VCF,
    IMPORT_NUCLEAR_VCF,
    combine_vcf_fixtures,
)

SUPPLIED_MT = str(MT_VCF)

# Default test settings (matches defaults used in production)
SETTINGS = VcfImportSettings(
    VCF_FILE=None,
    NA=".",
    OUT_CHR=True,
    OUT_HYPHENS=False,
    DEFAULT_TRANSCRIPT_SOURCE="E",
    CADD_DAMAGING_THRESHOLD=20,
    INPUT_TSV_PATH="data/fixtures",
    HASH_COMPARE=None,
    RANGES=None,
)


# --- FOCUS LOGIC FOR CLASSES AND METHODS ---
_focused_classes = set()
_focused_methods = set()


def focus(obj):
    """
    Decorator to mark a test class or method as focused.
    If any class or method is focused, only those run.
    """
    if isinstance(obj, type):  # class
        obj._focused = True
        _focused_classes.add(obj)
        return obj
    else:  # method
        obj._focused_method = True
        _focused_methods.add(obj)
        return obj


def _any_focus():
    return bool(_focused_classes or _focused_methods)


class FocusableTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # If any class or method is focused, skip this class unless focused or has focused methods
        if _any_focus():
            # If class is focused, allow
            if getattr(cls, "_focused", False):
                return
            # If any method in this class is focused, allow
            for attr in dir(cls):
                meth = getattr(cls, attr)
                if getattr(meth, "_focused_method", False):
                    print(f"Running focused test: {cls.__name__}.{attr}")
                    return
            # Otherwise, skip whole class
            raise unittest.SkipTest("Skipping - not focused")

    def setUp(self):
        # If any method is focused, skip this test unless it's focused
        if _focused_methods:
            test_method = getattr(self, self._testMethodName)
            if not getattr(test_method, "_focused_method", False):
                self.skipTest("Skipping - not focused method")


# Helper function to get fixture paths
def get_fixture_path(filename: str) -> str:
    """Get the absolute path to a fixture file."""
    return str(ROOT / "data" / "fixtures" / "vcf" / filename)


class TestBaseFilter(FocusableTestCase):

    testInstance = None

    class MockFilter(CallFilter):
        def __init__(self, vcf_file_path, settings):
            super().__init__(vcf_file_path, settings)

        def load_vcf_file(self, vcf_file_path: str):
            super().load_vcf_file(vcf_file_path)

        def getTableRows(self):
            # Return a simple dict for each variant: chrom, pos, id
            rows = []
            for rec in self.vcf_record_stream():
                rows.append({"chrom": rec.CHROM, "pos": rec.POS, "id": rec.ID})
            return rows

    def setUp(self):
        self.testInstance = self.MockFilter(get_fixture_path("mock_snv.vcf"), SETTINGS)

    def test_instance_creation(self):
        self.assertIsInstance(self.testInstance, CallFilter)

    def test_has_records(self):
        records = list(self.testInstance.vcf_record_stream())
        self.assertEqual(len(records), 2)

    def test_csq_getter(self):
        records = list(self.testInstance.vcf_record_stream())
        csq_values = self.testInstance.get_csq_values(records[1], "SYMBOL")
        self.assertEqual(csq_values, ["LA16c-60H5.7", "NBEAP3"])

    def test_csq_without_description(self):
        with patch("vcfpy.Header.get_info_field_info") as get_info:
            get_info.return_value.description = None
            instance = self.MockFilter(get_fixture_path("mock_snv.vcf"), SETTINGS)
        self.assertEqual(instance.csq_fields, [])
        self.assertEqual(instance.csq_index_map, {})

    def test_range_parameters(self):
        test_settings = copy.deepcopy(SETTINGS)
        test_settings.RANGES = "22:300-350"
        instance = self.MockFilter(get_fixture_path("manychrs.vcf"), test_settings)
        records = list(instance.vcf_record_stream())
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].POS, 300)
        self.assertEqual(records[1].POS, 350)

        test_settings.RANGES = "1:1002-1003,2:1701-1703"
        instance = self.MockFilter(get_fixture_path("manychrs.vcf"), test_settings)
        records = list(instance.vcf_record_stream())
        self.assertEqual(len(records), 5)
        self.assertEqual(records[0].POS, 1002)
        self.assertEqual(records[1].POS, 1003)
        self.assertEqual(records[2].POS, 1701)
        self.assertEqual(records[3].POS, 1702)
        self.assertEqual(records[4].POS, 1703)

    def test_make_variant_id(self):
        test_settings = copy.deepcopy(SETTINGS)
        test_settings.OUT_CHR = True
        test_settings.OUT_HYPHENS = True
        instance = self.MockFilter(get_fixture_path("mock_snv.vcf"), test_settings)
        first_record = list(instance.vcf_record_stream())[0]
        self.assertEqual(instance.make_variant_id(first_record), "chr1-100000-A-G")

        test_settings.OUT_CHR = False
        test_settings.OUT_HYPHENS = False
        instance = self.MockFilter(get_fixture_path("mock_snv.vcf"), test_settings)
        first_record = list(instance.vcf_record_stream())[0]
        self.assertEqual(instance.make_variant_id(first_record), "1_100000_A_G")

    def test_should_retry_loading_vcf_if_file_disappears(self):
        """Test that load_vcf_file retries if file is temporarily unavailable."""
        import builtins
        from unittest import mock
        import io

        # Path to a real VCF fixture file
        vcf_path = get_fixture_path("mock_snv.vcf")
        test_settings = copy.deepcopy(SETTINGS)

        # Prepare a real file handle for the second call
        real_open = builtins.open
        call_count = {"count": 0}

        def flaky_open(file, mode="r", *args, **kwargs):
            if os.path.abspath(file) == os.path.abspath(vcf_path) and "b" in mode:
                call_count["count"] += 1
                if (
                    call_count["count"] < 3
                ):  # Simulate file disappearance on the first two calls
                    raise FileNotFoundError("Simulated file disappearance")
                else:
                    return real_open(file, mode, *args, **kwargs)
            return real_open(file, mode, *args, **kwargs)

        # Patch open only in the CallFilter module context
        with mock.patch("builtins.open", side_effect=flaky_open):
            with mock.patch("time.sleep", return_value=None):
                # Now instantiate the filter, which will trigger file open
                try:
                    instance = self.MockFilter(vcf_path, test_settings)
                    # If we get here, the retry worked
                    self.assertIsInstance(instance, CallFilter)
                except FileNotFoundError:
                    self.fail(
                        "CallFilter did not retry loading the VCF file after disappearance."
                    )


class TestGenesCallFilter(FocusableTestCase):
    """Test GenesCallFilter."""

    # Class variables initialized to None
    filter = None

    def setUp(self):
        """Set up test fixtures."""
        self.filter = GenesCallFilter(get_fixture_path("mock_snv.vcf"), SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2, "Expected 2 rows from mock_snv.vcf")
        self.assertIn("short_name", result[0])


class TestTranscriptsCallFilter(FocusableTestCase):
    """Test TranscriptsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path("mock_snv.vcf")
        self.filter = TranscriptsCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)

        self.assertIn("transcript_id", result[0])
        self.assertIn("gene", result[0])
        self.assertIn("transcript_type", result[0])
        self.assertIn("tsl", result[0])
        # Check transcript type is encoded (E or R)
        self.assertIn(result[0]["transcript_type"], ["."])
        self.assertIn(result[1]["transcript_type"], ["E"])


class TestVariantsCallFilter(FocusableTestCase):
    """Test VariantsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path("mock_snv.vcf")
        self.filter = VariantsCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2, "Expected 2 rows from mock_snv.vcf")

        self.assertIn("variant_id", result[0])
        self.assertIn("var_type", result[0])
        # Check variant type matches
        self.assertEqual(result[0]["var_type"], "SNV")


class TestVariantsTranscriptsCallFilter(FocusableTestCase):
    """Test VariantsTranscriptsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path("mock_snv.vcf")
        self.filter = VariantsTranscriptsCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3, "Expected 3 rows from mock_snv.vcf")
        valid_result = result[
            1
        ]  # sometimes (or with diff config, result 0 will be valid)

        self.assertEqual(valid_result["transcript"], "ENST00000398242.2")
        self.assertEqual(valid_result["hgvsc"], "ENST00000398242.2:n.402G>C")


class TestVariantsAnnotationsCallFilter(FocusableTestCase):
    """Test VariantsAnnotationsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path("mock_snv.vcf")
        self.filter = VariantsAnnotationsCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)

        self.assertIn("hgvsp", result[0])
        self.assertIn("sift", result[0])
        self.assertIn("polyphen", result[0])
        self.assertIn("transcript", result[0])
        self.assertIn("variant", result[0])


class TestVariantsConsequencesCallFilter(FocusableTestCase):
    """Test VariantsConsequencesCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path("mock_snv.vcf")
        self.filter = VariantsConsequencesCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)

        self.assertIn("severity", result[0])
        self.assertIn("variant", result[0])
        self.assertIn("transcript", result[0])
        self.assertEqual(result[0]["severity"], 40)
        self.assertEqual(result[1]["severity"], 27)


class TestSnvsCallFilter(FocusableTestCase):
    """Test SnvsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path("mock_snv.vcf")
        self.filter = SnvsCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())

        self.assertIsInstance(result, list)

        self.assertIn("variant", result[0])
        self.assertIn("type", result[0])
        self.assertIn("chr", result[0])
        self.assertIn("pos", result[0])
        self.assertIn("dbsnp_id", result[0])
        self.assertEqual(result[0]["dbsnp_id"], "rs200028125")


class TestGenomicBvlFrequenciesCallFilter(FocusableTestCase):
    """Test GenomicBvlFrequenciesCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path("mock_snv.vcf")
        self.filter = GenomicBvlFrequenciesCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertIn("variant", result[0])
        self.assertIn("af_tot", result[0])
        self.assertIn("ac_tot", result[0])
        self.assertEqual(result[0]["af_tot"], 0.188889)
        self.assertEqual(result[0]["hom_tot"], 34)


class TestMtsCallFilter(FocusableTestCase):
    """Canonical MT metadata, plus explicitly labeled legacy IBVL coverage."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = SUPPLIED_MT
        self.filter = MtsCallFilter(
            self.vcf_files,
            SETTINGS,
            mt_vcf_file_path=self.vcf_files,
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        try:
            result = self.filter.getTableRows()
        except NotImplementedError:
            self.skipTest("MtsCallFilter.getTableRows() not yet implemented")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 158)

        self.assertIn("variant", result[0])
        self.assertIn("pos", result[0])
        self.assertIn("ref", result[0])
        self.assertIn("alt", result[0])

    def test_ibvl_metadata(self):
        """The old IBVL custom-column dialect remains supported separately."""
        row = MtsCallFilter(
            None, SETTINGS, mt_vcf_file_path=get_fixture_path("mock_mt.vcf")
        ).getTableRows()[0]
        self.assertEqual(row["variant"], "chrM_8602_T_C")
        self.assertEqual(row["dbsnp_id"], "rs879029014")
        self.assertIn("variant=8602T%3EC", row["mitomap_url"])

    def test_variome_metadata_and_indel_ids(self):
        instance = MtsCallFilter(None, SETTINGS, mt_vcf_file_path=SUPPLIED_MT)
        rows = {row["variant"]: row for row in instance.getTableRows()}
        self.assertEqual(rows["chrM_4440_G_T"]["clinvar_vcv"], ".")
        self.assertEqual(rows["chrM_5600_AC_A"]["alt"], "A")
        record = next(
            record for record in instance.vcf_record_stream() if record.POS == 5600
        )
        record.INFO["ClinVar_Variation_ID"] = "123"
        with patch.object(instance, "vcf_record_stream", return_value=iter([record])):
            row = instance.getTableRows()[0]
        self.assertEqual(row["clinvar_vcv"], "123")
        self.assertIn("/123/", row["clinvar_url"])
        record._variome_csq_index_map = {"Existing_variation": 0}
        record.INFO["CSQ"] = ["rs123&VCV000456"]
        with patch.object(instance, "vcf_record_stream", return_value=iter([record])):
            row = instance.getTableRows()[0]
        self.assertEqual(row["clinvar_vcv"], "000456")
        self.assertIn("/000456/", row["clinvar_url"])

    def test_mt_variants_do_not_populate_nuclear_tables(self):
        for path in (get_fixture_path("mock_mt.vcf"), SUPPLIED_MT):
            self.assertEqual(list(SnvsCallFilter(path, SETTINGS).getTableRows()), [])
            self.assertEqual(
                list(GenomicBvlFrequenciesCallFilter(path, SETTINGS).getTableRows()), []
            )
            self.assertTrue(
                all(
                    row["var_type"] == "M"
                    for row in VariantsCallFilter(
                        None, SETTINGS, mt_vcf_file_path=path
                    ).getTableRows()
                )
            )

    def test_mt_range_aliases(self):
        for chrom in ("M", "MT", "chrM", "chrMT"):
            settings = copy.copy(SETTINGS)
            settings.RANGES = f"{chrom}:4440-4440"
            rows = MtsCallFilter(
                None, settings, mt_vcf_file_path=SUPPLIED_MT
            ).getTableRows()
            self.assertEqual(len(rows), 1)


class TestMtBvlFrequenciesCallFilter(FocusableTestCase):
    """Canonical MT frequencies, plus explicitly labeled legacy IBVL coverage."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = SUPPLIED_MT
        self.filter = MtBvlFrequenciesCallFilter(
            self.vcf_files,
            SETTINGS,
            mt_vcf_file_path=self.vcf_files,
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        try:
            result = self.filter.getTableRows()
        except NotImplementedError:
            self.skipTest(
                "MtBvlFrequenciesCallFilter.getTableRows() not yet implemented"
            )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 158)

        self.assertIn("variant", result[0])
        self.assertIn("an", result[0])
        self.assertIn("ac_hom", result[0])
        self.assertIn("ac_het", result[0])

    def test_ibvl_metrics_and_histogram(self):
        """The old IBVL custom-column dialect remains supported separately."""
        row = MtBvlFrequenciesCallFilter(
            None, SETTINGS, mt_vcf_file_path=get_fixture_path("mock_mt.vcf")
        ).getTableRows()[0]
        self.assertEqual(row["an"], 100)
        self.assertEqual(row["ac_hom"], 5)
        self.assertEqual(row["ac_het"], 10)
        self.assertEqual(row["af_hom"], 0.05)
        self.assertEqual(row["max_hl"], 0.95)
        self.assertEqual(row["hl_hist"], "5,10,15,8,6,4,3,2,1,1")

    def test_explicit_cohort_info_and_format_overrides_on_canonical_record(self):
        """Deliberately add cohort metrics to test precedence over sample AF."""
        instance = MtBvlFrequenciesCallFilter(
            None, SETTINGS, mt_vcf_file_path=SUPPLIED_MT
        )
        record = next(instance.vcf_record_stream())
        metrics = {
            "AN": 100,
            "AC_hom": [5],
            "AC_het": [10],
            "AF_hom": [0.05],
            "AF_het": [0.1],
            "max_observed_heteroplasmy": [0.95],
            "heteroplasmy_histogram": [5, 10, 15, 8, 6, 4, 3, 2, 1, 1],
        }
        record.INFO.update(metrics)
        format_record = copy.deepcopy(record)
        format_record.POS += 1
        format_record.INFO = {}
        format_record.FORMAT = list(metrics)
        format_record.calls[0].data = {
            **metrics,
            "AC_hom": 0,
            "AC_het": 1,
            "AF_hom": 0,
            "AF_het": 0.01,
            "heteroplasmy_histogram": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        unobserved = copy.deepcopy(record)
        unobserved.INFO = {"AN": 0}
        unobserved.FORMAT = []
        unobserved.calls = []
        with patch.object(
            instance,
            "vcf_record_stream",
            return_value=iter(
                [
                    record,
                    format_record,
                    unobserved,
                ]
            ),
        ):
            rows = instance.getTableRows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["an"], 100)
        self.assertEqual(rows[0]["hl_hist"], "5,10,15,8,6,4,3,2,1,1")
        self.assertEqual(rows[1]["ac_hom"], 0)
        self.assertEqual(rows[1]["af_hom"], 0)
        self.assertEqual(rows[1]["ac_het"], 1)
        self.assertEqual(rows[1]["hl_hist"], "1,0,0,0,0,0,0,0,0,0")

    def test_missing_metrics_are_not_reported_as_zero(self):
        """Deliberately remove sample data and cohort metrics from a real record."""
        record = next(self.filter.vcf_record_stream())
        record.INFO = {"AN": 100}
        record.FORMAT = []
        record.calls = []
        with patch.object(
            self.filter, "vcf_record_stream", return_value=iter([record])
        ):
            row = self.filter.getTableRows()[0]
        self.assertIsNone(row["ac_hom"])
        self.assertIsNone(row["ac_het"])
        self.assertIsNone(row["af_hom"])
        self.assertIsNone(row["max_hl"])
        self.assertEqual(row["hl_hist"], "")

    def test_multiallelic_cohort_metrics_are_selected_per_alt(self):
        """Deliberately add per-ALT cohort overrides at canonical MT 9055."""
        instance = MtBvlFrequenciesCallFilter(
            None,
            SETTINGS,
            mt_vcf_file_path=SUPPLIED_MT,
        )
        record = next(
            record for record in instance.vcf_record_stream() if record.POS == 9055
        )
        record.INFO.update(
            {
                "AC_hom": [1, 2],
                "AC_het": [3, 4],
                "AF_hom": [0.1, 0.2],
                "AF_het": [0.3, 0.4],
                "max_observed_heteroplasmy": [0.8, 0.9],
            }
        )
        with patch.object(instance, "vcf_record_stream", return_value=iter([record])):
            rows = instance.getTableRows()
        self.assertEqual(
            [row["variant"] for row in rows], ["chrM_9055_G_T", "chrM_9055_G_A"]
        )
        self.assertEqual([row["an"] for row in rows], [4, 4])
        self.assertEqual([row["ac_hom"] for row in rows], [1, 2])
        self.assertEqual([row["ac_het"] for row in rows], [3, 4])
        self.assertEqual([row["af_hom"] for row in rows], [0.1, 0.2])
        self.assertEqual([row["af_het"] for row in rows], [0.3, 0.4])
        self.assertEqual([row["max_hl"] for row in rows], [0.8, 0.9])

    def test_histogram_and_max_hl_derived_per_alt_from_sample_af(self):
        instance = MtBvlFrequenciesCallFilter(
            None,
            SETTINGS,
            mt_vcf_file_path=SUPPLIED_MT,
        )
        record = next(
            record for record in instance.vcf_record_stream() if record.POS == 9055
        )
        with patch.object(
            instance, "vcf_record_stream", return_value=iter([copy.deepcopy(record)])
        ):
            rows = instance.getTableRows()
        self.assertEqual(
            [row["hl_hist"] for row in rows],
            ["1,0,0,0,0,0,0,0,0,0", "0,0,0,0,0,0,0,0,0,1"],
        )
        self.assertEqual([row["max_hl"] for row in rows], [0.01, 0.997])
        self.assertEqual([row["an"] for row in rows], [1, 1])
        self.assertEqual([row["ac_hom"] for row in rows], [0, 1])
        self.assertEqual([row["ac_het"] for row in rows], [1, 0])
        self.assertEqual([row["af_hom"] for row in rows], [0, 1])
        self.assertEqual([row["af_het"] for row in rows], [1, 0])
        for call, af in zip(record.calls, ([0.05], [0.1], [0.95])):
            call.data["AF"] = af
        record.ALT = record.ALT[:1]
        with patch.object(instance, "vcf_record_stream", return_value=iter([record])):
            row = instance.getTableRows()[0]
        self.assertEqual(row["hl_hist"], "1,1,0,0,0,0,0,0,0,1")
        self.assertEqual(row["max_hl"], 0.95)
        self.assertEqual(row["an"], 3)
        self.assertEqual((row["ac_hom"], row["ac_het"]), (1, 2))
        self.assertAlmostEqual(row["af_hom"], 1 / 3)
        self.assertAlmostEqual(row["af_het"], 2 / 3)

    def test_sample_denominator_includes_zero_and_excludes_missing_af(self):
        """Deliberately replace canonical AF values with zero, heteroplasmy, missing."""
        instance = MtBvlFrequenciesCallFilter(
            None,
            SETTINGS,
            mt_vcf_file_path=SUPPLIED_MT,
        )
        record = next(
            record for record in instance.vcf_record_stream() if record.POS == 8860
        )
        record.INFO.pop("AN")
        for call, af in zip(record.calls, ([0], [0.5], [None])):
            call.data["AF"] = af
        with patch.object(instance, "vcf_record_stream", return_value=iter([record])):
            row = instance.getTableRows()[0]
        self.assertEqual(row["an"], 2)
        self.assertEqual((row["ac_hom"], row["ac_het"]), (0, 1))
        self.assertEqual((row["af_hom"], row["af_het"]), (0, 0.5))

    def test_invalid_sample_af_is_reported_not_counted(self):
        """Deliberately inject invalid AF values into a canonical sample call."""
        instance = MtBvlFrequenciesCallFilter(
            None,
            SETTINGS,
            mt_vcf_file_path=SUPPLIED_MT,
        )
        record = next(
            record for record in instance.vcf_record_stream() if record.POS == 8860
        )
        for invalid in (-0.1, 1.1, float("nan"), float("inf")):
            with self.subTest(af=invalid):
                record.calls[0].data["AF"] = [invalid]
                with patch.object(
                    instance, "vcf_record_stream", return_value=iter([record])
                ):
                    with self.assertRaisesRegex(ValueError, "Invalid FORMAT/AF"):
                        instance.getTableRows()


class TestExplicitFilterInputs(unittest.TestCase):
    shared_filters = (
        GenesCallFilter,
        TranscriptsCallFilter,
        VariantsCallFilter,
        VariantsTranscriptsCallFilter,
        VariantsAnnotationsCallFilter,
        VariantsConsequencesCallFilter,
    )

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.nuclear = NUCLEAR_VCF
        self.mt = MT_VCF

    def test_shared_filters_merge_selected_records_and_deduplicate(self):
        counts = (2, 3, 160, 3, 3, 4)
        for filter_cls, count in zip(self.shared_filters, counts):
            with self.subTest(filter=filter_cls.__name__):
                instance = filter_cls(self.nuclear, SETTINGS, mt_vcf_file_path=self.mt)
                rows = list(instance.getTableRows())
                self.assertEqual(len(rows), count)
                self.assertEqual(list(instance.getTableRows()), rows)
                if filter_cls is VariantsCallFilter:
                    self.assertTrue(
                        {
                            "chr1_100000_A_G",
                            "chr22_16123121_G_C",
                            "chrM_4440_G_T",
                            "chrM_9055_G_T",
                            "chrM_9055_G_A",
                        }.issubset({row["variant_id"] for row in rows})
                    )

    def test_specialized_filters_ignore_the_other_input(self):
        for filter_cls in (SnvsCallFilter, GenomicBvlFrequenciesCallFilter):
            with self.subTest(filter=filter_cls.__name__):
                rows = list(
                    filter_cls(
                        get_fixture_path("mock_snv.vcf"),
                        SETTINGS,
                        mt_vcf_file_path="unused-missing-mt.vcf",
                    ).getTableRows()
                )
                self.assertTrue(rows)
                self.assertTrue(
                    all(not row["variant"].startswith("chrM_") for row in rows)
                )
        for filter_cls in (MtsCallFilter, MtBvlFrequenciesCallFilter):
            with self.subTest(filter=filter_cls.__name__):
                rows = list(
                    filter_cls(
                        "unused-missing-nuclear.vcf",
                        SETTINGS,
                        mt_vcf_file_path=self.mt,
                    ).getTableRows()
                )
                self.assertEqual(len(rows), 158)
                self.assertTrue(all(row["variant"].startswith("chrM_") for row in rows))

    def test_missing_optional_paths(self):
        for filter_cls in self.shared_filters + (
            SnvsCallFilter,
            GenomicBvlFrequenciesCallFilter,
            MtsCallFilter,
            MtBvlFrequenciesCallFilter,
            MtGnomadFrequenciesCallFilter,
        ):
            with self.subTest(filter=filter_cls.__name__):
                self.assertEqual(
                    list(
                        filter_cls(
                            None,
                            SETTINGS,
                            mt_vcf_file_path=None,
                        ).getTableRows()
                    ),
                    [],
                )
        self.assertEqual(MtsCallFilter(self.nuclear, SETTINGS).getTableRows(), [])
        self.assertEqual(
            MtBvlFrequenciesCallFilter(self.nuclear, SETTINGS).getTableRows(), []
        )
        rows = list(VariantsCallFilter(self.nuclear, SETTINGS).getTableRows())
        self.assertEqual(len(rows), 2)
        rows = list(
            VariantsCallFilter(None, SETTINGS, mt_vcf_file_path=self.mt).getTableRows()
        )
        self.assertEqual(len(rows), 158)

    def test_identical_and_equivalent_files_are_read_once(self):
        combined = Path(self.directory.name) / "combined.vcf"
        combine_vcf_fixtures(combined)
        alias = Path(self.directory.name) / "alias.vcf"
        alias.symlink_to(combined)
        hardlink = Path(self.directory.name) / "hardlink.vcf"
        hardlink.hardlink_to(combined)
        for mt_path in (combined, alias, hardlink):
            instance = VariantsCallFilter(combined, SETTINGS, mt_vcf_file_path=mt_path)
            with patch.object(
                instance, "_all_vcf_records", wraps=instance._all_vcf_records
            ) as read:
                self.assertEqual(len(list(instance.getTableRows())), 160)
                self.assertEqual(read.call_count, 1)

    def test_distinct_mixed_files_only_contribute_the_selected_genome(self):
        """Relocate two fixture contaminants so deduplication cannot hide scope bugs."""
        nuclear = Path(self.directory.name) / "mixed-nuclear.vcf"
        mitochondrial = Path(self.directory.name) / "mixed-mt.vcf"
        combine_vcf_fixtures(nuclear)
        lines = nuclear.read_text().splitlines()
        headers = [line for line in lines if line.startswith("#")]
        mt_records = [line for line in lines if line.startswith("chrM\t")]
        nuclear_records = [
            line for line in lines if not line.startswith(("#", "chrM\t"))
        ]
        wrong_mt = next(
            line for line in mt_records if line.startswith("chrM\t4440\t")
        ).replace("\t4440\t", "\t4441\t", 1)
        wrong_nuclear = next(
            line for line in nuclear_records if line.startswith("1\t100000\t")
        ).replace("\t100000\t", "\t100001\t", 1)
        nuclear.write_text(
            "\n".join(headers + nuclear_records + [wrong_mt]) + "\n",
            encoding="utf-8",
        )
        mitochondrial.write_text(
            "\n".join(headers + mt_records + [wrong_nuclear]) + "\n",
            encoding="utf-8",
        )
        instance = VariantsCallFilter(nuclear, SETTINGS, mt_vcf_file_path=mitochondrial)
        with patch.object(
            instance, "_all_vcf_records", wraps=instance._all_vcf_records
        ) as read:
            rows = list(instance.getTableRows())
        self.assertEqual(read.call_count, 2)
        variant_ids = {row["variant_id"] for row in rows}
        self.assertNotIn("chrM_4441_G_T", variant_ids)
        self.assertNotIn("chr1_100001_A_G", variant_ids)
        self.assertTrue(
            {
                "chrM_4440_G_T",
                "chrM_8860_A_G",
                "chrM_9055_G_T",
                "chrM_9055_G_A",
            }.issubset(variant_ids)
        )
        self.assertEqual(len(rows), 160)
        self.assertEqual(
            {row["variant_id"] for row in rows if row["var_type"] != "M"},
            {"chr1_100000_A_G", "chr22_16123121_G_C"},
        )
        self.assertEqual(sum(row["var_type"] == "M" for row in rows), 158)

    def test_no_csq_header_does_not_inherit_other_files_fields(self):
        instance = GenesCallFilter(self.nuclear, SETTINGS, mt_vcf_file_path=self.mt)
        self.assertEqual(
            list(instance.getTableRows()),
            [
                {"short_name": "LA16c-60H5.7"},
                {"short_name": "NBEAP3"},
            ],
        )

    def test_legacy_ibvl_dialect_keeps_its_parser_on_repeated_reads(self):
        instance = GenesCallFilter(
            get_fixture_path("mock_snv.vcf"),
            SETTINGS,
            mt_vcf_file_path=get_fixture_path("mock_mt.vcf"),
        )
        expected = [
            {"short_name": "LA16c-60H5.7"},
            {"short_name": "NBEAP3"},
            {"short_name": "MT-ATP6"},
        ]
        self.assertEqual(list(instance.getTableRows()), expected)
        self.assertEqual(list(instance.getTableRows()), expected)


class TestAnnotatedFilterHeaderEdgeCases(unittest.TestCase):
    """Read synthetic MT annotations alongside the canonical nuclear CSQ header."""

    def setUp(self):
        self.nuclear = IMPORT_NUCLEAR_VCF
        self.mt = ANNOTATED_MT_VCF
        self.settings = copy.copy(SETTINGS)
        self.settings.RANGES = "22:27000075-27000323,M:1-16569"

    def test_shared_filters_deduplicate_shared_genes_transcripts_and_records(self):
        """Duplicate the annotated canonical record; no output row should duplicate."""
        with tempfile.TemporaryDirectory() as directory:
            duplicate_mt = Path(directory) / "duplicate-mt.vcf"
            lines = self.mt.read_text().splitlines()
            duplicate = next(line for line in lines if line.startswith("chrM\t4440\t"))
            duplicate_mt.write_text(
                self.mt.read_text() + duplicate + "\n", encoding="utf-8"
            )
            for mt in (self.mt, duplicate_mt):
                for filter_cls, count in zip(
                    TestExplicitFilterInputs.shared_filters, (2, 3, 160, 9, 9, 18)
                ):
                    with self.subTest(filter=filter_cls.__name__, mt=mt.name):
                        instance = filter_cls(
                            self.nuclear, self.settings, mt_vcf_file_path=mt
                        )
                        rows = list(instance.getTableRows())
                        self.assertEqual(len(rows), count)
                        self.assertEqual(list(instance.getTableRows()), rows)
        genes = GenesCallFilter(self.nuclear, self.settings, mt_vcf_file_path=self.mt)
        self.assertEqual(
            list(genes.getTableRows()),
            [{"short_name": "MIATNB"}, {"short_name": "LOC107985582"}],
        )

    def test_suspended_and_materialized_records_keep_their_csq_header(self):
        instance = GenesCallFilter(
            self.nuclear, self.settings, mt_vcf_file_path=self.mt
        )
        nuclear_stream = instance.vcf_record_stream(self.nuclear)
        first = next(nuclear_stream)
        mt_records = list(instance.vcf_record_stream(self.mt))
        annotated = next(record for record in mt_records if record.POS == 4440)
        self.assertEqual(
            instance.get_csq_values(first, "SYMBOL"),
            ["MIATNB", "MIATNB", "LOC107985582"],
        )
        resumed = next(nuclear_stream)
        self.assertEqual(
            instance.get_csq_values(resumed, "SYMBOL"),
            ["MIATNB", "MIATNB", "LOC107985582"],
        )
        self.assertEqual(
            instance.get_csq_values(annotated, "SYMBOL"),
            ["MIATNB", "MIATNB", "LOC107985582"],
        )
        self.assertEqual(
            instance.get_csq_values(annotated, "Feature"),
            ["ENST00000717151", "ENST00000717153", "XR_001755472.2"],
        )
        nuclear_stream.close()


class TestMtGnomadFrequenciesCallFilter(FocusableTestCase):
    def test_intersection_and_chromosome_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gnomad.tsv"
            path.write_text(
                "chromosome\tposition\tref\talt\tAN\tAC_hom\tAC_het\tAF_hom\tAF_het\tmax_observed_heteroplasmy\n"
                "chrMT\t4440\tG\tT\t1000\t0\t10\t0\t0.01\t0.9\n"
                "M\t5600\tAC\tA\t1000\t1\t0\t0.001\t0\t1\n"
                "M\t9999\tA\tC\t1000\t1\t1\t0.001\t0.001\t1\n",
                encoding="utf-8",
            )
            rows = list(
                MtGnomadFrequenciesCallFilter(
                    "unused-missing-nuclear.vcf",
                    SETTINGS,
                    path,
                    mt_vcf_file_path=SUPPLIED_MT,
                ).getTableRows()
            )
            self.assertEqual(
                list(
                    MtGnomadFrequenciesCallFilter(
                        SUPPLIED_MT,
                        SETTINGS,
                        path,
                        mt_vcf_file_path=None,
                    ).getTableRows()
                ),
                [],
            )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["variant"], "chrM_4440_G_T")
        self.assertEqual(rows[0]["ac_hom"], 0)
        self.assertEqual(rows[1]["variant"], "chrM_5600_AC_A")


if __name__ == "__main__":
    unittest.main()

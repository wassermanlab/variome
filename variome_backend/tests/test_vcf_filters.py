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

from variome_backend.management.filters.settings import VcfImportSettings

# Default test settings (matches defaults used in production)
SETTINGS = VcfImportSettings(
    VCF_FILE=None,
    NA=".",
    OUT_CHR=True,
    OUT_HYPHENS=True,
    DEFAULT_TRANSCRIPT_SOURCE="E",
    CADD_DAMAGING_THRESHOLD=20,
    SEVERITIES_TSV_PATH="data/fixtures/severities.tsv",
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
            if getattr(cls, '_focused', False):
                return
            # If any method in this class is focused, allow
            for attr in dir(cls):
                meth = getattr(cls, attr)
                if getattr(meth, '_focused_method', False):
                    print(f"Running focused test: {cls.__name__}.{attr}")
                    return
            # Otherwise, skip whole class
            raise unittest.SkipTest("Skipping - not focused")

    def setUp(self):
        # If any method is focused, skip this test unless it's focused
        if _focused_methods:
            test_method = getattr(self, self._testMethodName)
            if not getattr(test_method, '_focused_method', False):
                self.skipTest("Skipping - not focused method")


from variome_backend.management.filters.CallFilter import CallFilter
from variome_backend.management.filters.GenesCallFilter import GenesCallFilter
from variome_backend.management.filters.TranscriptsCallFilter import TranscriptsCallFilter
from variome_backend.management.filters.VariantsCallFilter import VariantsCallFilter
from variome_backend.management.filters.VariantsTranscriptsCallFilter import VariantsTranscriptsCallFilter
from variome_backend.management.filters.VariantsAnnotationsCallFilter import VariantsAnnotationsCallFilter
from variome_backend.management.filters.VariantsConsequencesCallFilter import VariantsConsequencesCallFilter
from variome_backend.management.filters.SnvsCallFilter import SnvsCallFilter
from variome_backend.management.filters.MtsCallFilter import MtsCallFilter
from variome_backend.management.filters.GenomicBvlFrequenciesCallFilter import GenomicBvlFrequenciesCallFilter
from variome_backend.management.filters.MtBvlFrequenciesCallFilter import MtBvlFrequenciesCallFilter


# Helper function to get fixture paths
def get_fixture_path(filename: str) -> str:
    """Get the absolute path to a fixture file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'management', 'fixtures', 'vcf', filename)

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
                rows.append({
                    'chrom': rec.CHROM,
                    'pos': rec.POS,
                    'id': rec.ID
                })
            return rows
    def setUp(self):
        self.testInstance = self.MockFilter(get_fixture_path('mock_snv.vcf'), SETTINGS)

    def test_instance_creation(self):
        self.assertIsInstance(self.testInstance, CallFilter)

    def test_has_records(self):
        records = list(self.testInstance.vcf_record_stream())
        self.assertEqual(len(records), 2)

    def test_csq_getter(self):
        records = list(self.testInstance.vcf_record_stream())
        csq_values = self.testInstance.get_csq_values(records[1], 'SYMBOL')
        self.assertEqual(csq_values, ['LA16c-60H5.7', 'NBEAP3'])

    def test_severity_map_loaded(self):
        self.assertIn('missense_variant', self.testInstance.severity_map)
        self.assertIsInstance(self.testInstance.severity_map['missense_variant'], int)

    def test_range_parameters(self):
        test_settings = copy.deepcopy(SETTINGS)
        test_settings.RANGES = '22:300-350'
        instance = self.MockFilter(get_fixture_path('manychrs.vcf'), test_settings)
        records = list(instance.vcf_record_stream())
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].POS, 300)
        self.assertEqual(records[1].POS, 350)

        test_settings.RANGES = '1:1002-1003,2:1701-1703'
        instance = self.MockFilter(get_fixture_path('manychrs.vcf'), test_settings)
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
        instance = self.MockFilter(get_fixture_path('mock_snv.vcf'), test_settings)
        first_record = list(instance.vcf_record_stream())[0]
        self.assertEqual(instance.make_variant_id(first_record),'chr1-100000-A-G')

        test_settings.OUT_CHR = False
        test_settings.OUT_HYPHENS = False
        instance = self.MockFilter(get_fixture_path('mock_snv.vcf'), test_settings)
        first_record = list(instance.vcf_record_stream())[0]
        self.assertEqual(instance.make_variant_id(first_record),'1_100000_A_G')

    def test_should_retry_loading_vcf_if_file_disappears(self):
        """Test that load_vcf_file retries if file is temporarily unavailable."""
        import builtins
        from unittest import mock
        import io

        # Path to a real VCF fixture file
        vcf_path = get_fixture_path('mock_snv.vcf')
        test_settings = copy.deepcopy(SETTINGS)

        # Prepare a real file handle for the second call
        real_open = builtins.open
        call_count = {'count': 0}

        def flaky_open(file, mode='r', *args, **kwargs):
            if os.path.abspath(file) == os.path.abspath(vcf_path) and 'b' in mode:
                call_count['count'] += 1
                if call_count['count'] < 3:  # Simulate file disappearance on the first two calls
                    raise FileNotFoundError("Simulated file disappearance")
                else:
                    return real_open(file, mode, *args, **kwargs)
            return real_open(file, mode, *args, **kwargs)

        # Patch open only in the CallFilter module context
        with mock.patch('builtins.open', side_effect=flaky_open):
            with mock.patch('time.sleep', return_value=None):
                # Now instantiate the filter, which will trigger file open
                try:
                    instance = self.MockFilter(vcf_path, test_settings)
                    # If we get here, the retry worked
                    self.assertIsInstance(instance, CallFilter)
                except FileNotFoundError:
                    self.fail("CallFilter did not retry loading the VCF file after disappearance.")

class TestGenesCallFilter(FocusableTestCase):
    """Test GenesCallFilter."""

    # Class variables initialized to None
    filter = None

    def setUp(self):
        """Set up test fixtures."""
        self.filter = GenesCallFilter(
            get_fixture_path('mock_snv.vcf'),
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2, "Expected 2 rows from mock_snv.vcf")
        self.assertIn('short_name', result[0])

class TestTranscriptsCallFilter(FocusableTestCase):
    """Test TranscriptsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_snv.vcf')
        self.filter = TranscriptsCallFilter(self.vcf_files, SETTINGS)

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)

        self.assertIn('transcript_id', result[0])
        self.assertIn('gene', result[0])
        self.assertIn('transcript_type', result[0])
        self.assertIn('tsl', result[0])
        # Check transcript type is encoded (E or R)
        self.assertIn(result[0]['transcript_type'], ['.'])
        self.assertIn(result[1]['transcript_type'], ['E'])

class TestVariantsCallFilter(FocusableTestCase):
    """Test VariantsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_snv.vcf')
        self.filter = VariantsCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2, "Expected 2 rows from mock_snv.vcf")

        self.assertIn('variant_id', result[0])
        self.assertIn('var_type', result[0])
        # Check variant type matches
        self.assertEqual(result[0]['var_type'], 'SNV')

class TestVariantsTranscriptsCallFilter(FocusableTestCase):
    """Test VariantsTranscriptsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_snv.vcf')
        self.filter = VariantsTranscriptsCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3, "Expected 3 rows from mock_snv.vcf")
        valid_result = result[1] # sometimes (or with diff config, result 0 will be valid)

        self.assertEqual(valid_result['transcript'], 'ENST00000398242.2')
        self.assertEqual(valid_result['hgvsc'], 'ENST00000398242.2:n.402G>C')

class TestVariantsAnnotationsCallFilter(FocusableTestCase):
    """Test VariantsAnnotationsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_snv.vcf')
        self.filter = VariantsAnnotationsCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)

        self.assertIn('hgvsp', result[0])
        self.assertIn('sift', result[0])
        self.assertIn('polyphen', result[0])
        self.assertIn('transcript', result[0])
        self.assertIn('variant', result[0])

class TestVariantsConsequencesCallFilter(FocusableTestCase):
    """Test VariantsConsequencesCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_snv.vcf')
        self.filter = VariantsConsequencesCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)

        self.assertIn('severity', result[0])
        self.assertIn('variant', result[0])
        self.assertIn('transcript', result[0])
        self.assertEqual(result[0]['severity'], 40)
        self.assertEqual(result[1]['severity'], 27)

class TestSnvsCallFilter(FocusableTestCase):
    """Test SnvsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_snv.vcf')
        self.filter = SnvsCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())

        self.assertIsInstance(result, list)

        self.assertIn('variant', result[0])
        self.assertIn('type', result[0])
        self.assertIn('chr', result[0])
        self.assertIn('pos', result[0])


class TestGenomicBvlFrequenciesCallFilter(FocusableTestCase):
    """Test GenomicBvlFrequenciesCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_snv.vcf')
        self.filter = GenomicBvlFrequenciesCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""

        result = list(self.filter.getTableRows())
        self.assertIsInstance(result, list)
        self.assertIn('variant', result[0])
        self.assertIn('af_tot', result[0])
        self.assertIn('ac_tot', result[0])
        self.assertEqual(result[0]['af_tot'], 0.188889)
        self.assertEqual(result[0]['hom_tot'], 34)


# Mitochondrial (not yet implemented)
class TestMtsCallFilter(FocusableTestCase):
    """Test MtsCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        self.skipTest("MtsCallFilter.getTableRows() not yet implemented")
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_mt.vcf')
        self.filter = MtsCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        try:
            result = self.filter.getTableRows()
        except NotImplementedError:
            self.skipTest("MtsCallFilter.getTableRows() not yet implemented")

        self.assertIsInstance(result, list)


        self.assertIn('variant', result[0])
        self.assertIn('pos', result[0])
        self.assertIn('ref', result[0])
        self.assertIn('alt', result[0])

class TestMtBvlFrequenciesCallFilter(FocusableTestCase):
    """Test MtBvlFrequenciesCallFilter."""

    # Class variables initialized to None
    filter = None
    vcf_files = None

    def setUp(self):
        self.skipTest("MtBvlFrequenciesCallFilter.getTableRows() not yet implemented")
        """Set up test fixtures."""
        self.vcf_files = get_fixture_path('mock_mt.vcf')
        self.filter = MtBvlFrequenciesCallFilter(
            self.vcf_files,
            SETTINGS
        )

    def test_getTableRows_output_structure(self):
        """Test that getTableRows returns correct structure."""
        try:
            result = self.filter.getTableRows()
        except NotImplementedError:
            self.skipTest("MtBvlFrequenciesCallFilter.getTableRows() not yet implemented")

        self.assertIsInstance(result, list)

        self.assertIn('variant', result[0])
        self.assertIn('an', result[0])
        self.assertIn('ac_hom', result[0])
        self.assertIn('ac_het', result[0])

if __name__ == '__main__':
    unittest.main()

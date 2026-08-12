"""
CallFilter base class for VCF import filters.
"""

from time import sleep

from variome_backend.management.vcf_import_utils import validate_get

import vcfpy
import os
import logging

import gzip
import io
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, before_sleep_log

#file open retries
ATTEMPTS = 12
INTERVAL = 40

def wait_with_sleep(retry_state):
    return INTERVAL

logger = logging.getLogger(__name__)

class CallFilter(ABC):
    def __init__(self, vcf_file_path: str, settings):
        self.csq_fields = []
        self.csq_index_map = {}
        self.vcf_header = None
        self._vcf_file_path = vcf_file_path
        self.settings = settings

        self._init_vcf_header_and_csq()

    @retry(
        stop=stop_after_attempt(ATTEMPTS),
        wait=wait_with_sleep,
        retry=retry_if_exception_type(FileNotFoundError),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def stream_with_retries(self, file_path):

        if file_path.endswith('.gz'):
            gz = gzip.open(file_path, 'rb')
            return io.TextIOWrapper(gz, encoding='utf-8', errors='replace')
        else:
            return io.TextIOWrapper(open(file_path, 'rb'), encoding='utf-8', errors='replace')

    @retry(
        stop=stop_after_attempt(ATTEMPTS),
        wait=wait_with_sleep,
        retry=retry_if_exception_type(FileNotFoundError),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _init_vcf_header_and_csq(self):

        child_class_name = self.__class__.__name__
        logger.info(f"scanning {self._vcf_file_path} using {child_class_name}...")
        # Only read header and csq fields, not all records
        if self._vcf_file_path.endswith('.gz'):
            with gzip.open(self._vcf_file_path, 'rb') as gz:
                with io.TextIOWrapper(gz, encoding='utf-8', errors='replace') as f:
                    vcf_reader = vcfpy.Reader(stream=f)
                    self.vcf_header = vcf_reader.header
                    csq = vcf_reader.header.get_info_field_info("CSQ")
                    csq_elements = csq.description.split("Format: ")[1]
                    self.csq_fields = csq_elements.split("|")
                    self.csq_index_map = {field: index for index, field in enumerate(self.csq_fields)}
        else:
            with io.TextIOWrapper(open(self._vcf_file_path, 'rb'), encoding='utf-8', errors='replace') as f:
                vcf_reader = vcfpy.Reader(stream=f)
                self.vcf_header = vcf_reader.header
                csq = vcf_reader.header.get_info_field_info("CSQ")
                csq_elements = csq.description.split("Format: ")[1]
                self.csq_fields = csq_elements.split("|")
                self.csq_index_map = {field: index for index, field in enumerate(self.csq_fields)}

    def vcf_record_stream(self):
        """
        Generator that yields VCF records one at a time from the file.
        """
        RANGES = self.settings.RANGES
        ranges = RANGES.split(",") if RANGES else []
        range_map = {}
        for r in ranges:
            chrom, pos_range = r.split(":")
            start, end = map(int, pos_range.split("-"))
            range_map[str.replace(chrom, "chr", "")] = (start, end)

        def yield_records_in_ranges(reader):
            if RANGES:
                for record in reader:
                    chrom_key = record.CHROM
                    # Try all possible chrom representations
                    keys = [chrom_key, chrom_key.replace("chr", ""), "chr"+chrom_key]
                    found = False
                    for k in keys:
                        if k in range_map:
                            start, end = range_map[k]
                            if start <= record.POS <= end:
                                yield record
                                found = True
                            break
            else:
                for record in reader:
                    yield record

        with self.stream_with_retries(self._vcf_file_path) as stream:
            yield from yield_records_in_ranges(vcfpy.Reader(stream=stream))




    def describe(self) -> str:
        description = ""
        csq_fields = '\n'.join(self.csq_fields)
        description += f"INFO fields:"
        if hasattr(self, 'vcf_header') and self.vcf_header is not None:
            info_fields = '(from header) \n'
            info_fields += '\n'.join(self.vcf_header.info_ids())
        else:
            info_fields = '(not found)'
        description += f"\n{info_fields}\n"
        description += f"CSQ fields:\n{csq_fields}\n"
        return description

    def load_vcf_file(self, file, type = "SNV"):
        return []

    def get_csq_values(self, record: vcfpy.Record, field_name: str) -> List[str]:
        """
        Helper method to extract a specific CSQ field value from a VCF record.

        Args:
            record: VCF record object
            field_name: Name of the CSQ field to extract
        """
        index = self.csq_index_map.get(field_name)
        values = []
        if index is None:
            return []
        csq_list = record.INFO.get("CSQ", [])
        if not csq_list:
            return []
        for csq_entry in csq_list:
            csq_parts = csq_entry.split("|")
            if index >= len(csq_parts):
                return []
            else:
                values.append(csq_parts[index])
        return values

    def get_info_value(self, record: vcfpy.Record, field_name: str, fallback = None) -> str:
        """
        Helper method to extract a specific INFO field value from a VCF record.

        Args:
            record: VCF record object
            field_name: Name of the INFO field to extract
        """
        return record.INFO.get(field_name, fallback)

    def make_variant_id(self, record: vcfpy.Record) -> str:
        OUT_HYPHENS = self.settings.OUT_HYPHENS
        OUT_CHR = self.settings.OUT_CHR

        """
        Helper method to construct a variant ID from VCF record fields.

        Args:
            record: VCF record object
        """
        if OUT_CHR:
            chrom = "chr"+ record.CHROM.replace("chr", "")
        else:
            chrom = record.CHROM.replace("chr", "")
        pos = record.POS
        ref = record.REF
        alt = record.ALT[0].value  # assuming single ALT allele
        if OUT_HYPHENS:
            # variome prefers
            variant_id = f"{chrom}-{pos}-{ref}-{alt}"
        else:
            # VCF standard seems to store using _ as separators
            variant_id = f"{chrom}_{pos}_{ref}_{alt}"
        return variant_id

    @abstractmethod
    def getTableRows(self) -> List[Dict[str, Any]]:
        """
        Extract table rows from the loaded VCF data.

        Returns:
            List of dictionaries where each dict represents a row in the table.
        """
        pass

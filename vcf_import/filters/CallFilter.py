"""
CallFilter base class and global VCF options.
"""


# Global VCF options (imported from constants)
from vcf_import.constants import HYPEN_VARIANT_NOTATION, CHR_NOTATION, NA, SEVERITIES_TSV_PATH
from vcf_import.tools import validate_get

import vcfpy
import os
import logging

import gzip
import io
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class CallFilter(ABC):
    def __init__(self, vcf_file_path: str):
        self.csq_fields = []
        self.csq_index_map = {}
        self.severity_map = {}
        self.vcf_header = None
        self._vcf_file_path = vcf_file_path
        self._init_vcf_header_and_csq()

    def _init_vcf_header_and_csq(self):
        child_class_name = self.__class__.__name__
        logger.info(f"booting up {child_class_name}...")
        #read severity table file
        severity_table_path = SEVERITIES_TSV_PATH
        try:
            with open(severity_table_path, "r") as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split("\t")
                    if len(parts) == 2:
                        severity, consequence = parts
                    elif len(parts) == 3:
                        severity, _, consequence = parts
                    self.severity_map[consequence] = int(severity)
        except FileNotFoundError:
            logger.warning("Severity table file not found: %s", severity_table_path)
            exit()
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
        if self._vcf_file_path.endswith('.gz'):
            with gzip.open(self._vcf_file_path, 'rb') as gz:
                with io.TextIOWrapper(gz, encoding='utf-8', errors='replace') as f:
                    vcf_reader = vcfpy.Reader(stream=f)
                    for record in vcf_reader:
                        yield record
        else:
            with io.TextIOWrapper(open(self._vcf_file_path, 'rb'), encoding='utf-8', errors='replace') as f:
                vcf_reader = vcfpy.Reader(stream=f)
                for record in vcf_reader:
                    yield record
        
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
        def read_vcf(reader: vcfpy.Reader):
            self.vcf_header = reader.header
                
            if type == "SNV":
            
                csq = reader.header.get_info_field_info("CSQ")
                csq_elements = csq.description.split("Format: ")[1]
                self.csq_fields = csq_elements.split("|")
                self.csq_index_map = {field: index for index, field in enumerate(self.csq_fields)}
                
                for record in reader:
                    try:
                        self.vcf_records.append(record)
                    except Exception as e:
                        logger.error(f"Error processing record {record} in file {file}: {e}")
                        
            elif type == "MT":
                # ????? TBA
                exit()
                
                self.csq_index_map = {field: index for index, field in enumerate(self.csq_fields)}

                for record in reader:    
                    self.vcf_records.append(record)
                
        if file.endswith('.gz'):
            with gzip.open(file, 'rb') as gz:
                with io.TextIOWrapper(gz, encoding='utf-8', errors='replace') as f:  # or errors='ignore'
                    vcf_reader = vcfpy.Reader(stream=f)
                    read_vcf(vcf_reader)
                        
        else:
            with io.TextIOWrapper(open(file, 'rb'), encoding='utf-8', errors='replace') as f:
                vcf_reader = vcfpy.Reader(stream=f)
                read_vcf(vcf_reader)
        
    
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
        for list in csq_list:
            csq_parts = list.split("|")
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
        """
        Helper method to construct a variant ID from VCF record fields.
        
        Args:
            record: VCF record object
        """
        if HYPEN_VARIANT_NOTATION:
            if CHR_NOTATION:
                chrom = record.CHROM
            else:
                chrom = record.CHROM.replace("chr", "")
            pos = record.POS
            ref = record.REF
            alt = record.ALT[0].value  # assuming single ALT allele
            variant_id = f"{chrom}-{pos}-{ref}-{alt}"
        else:
            variant_id = record.ID[0]
        return variant_id
    @abstractmethod
    def getTableRows(self) -> List[Dict[str, Any]]:
        """
        Extract table rows from the loaded VCF data.
        
        Returns:
            List of dictionaries where each dict represents a row in the table.
        """
        pass
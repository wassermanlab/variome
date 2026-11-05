from variome_backend.management.VCFCallFilters.CallFilter import CallFilter
from typing import List, Dict, Any


class GenesCallFilter(CallFilter):
    """
    Generates the 'genes' table.
    """

    def __init__(self, vcf_file_path, settings, mt_vcf_file_path=None):
        super().__init__(vcf_file_path, settings, mt_vcf_file_path)

    def getTableRows(self):
        """
        Generator that yields unique gene symbols as dicts, one at a time.
        """
        short_names = set()
        for record in self.shared_record_stream():
            for gene_symbol in self.get_csq_values(record, "SYMBOL"):
                if gene_symbol and gene_symbol != self.settings.NA:
                    if gene_symbol not in short_names:
                        short_names.add(gene_symbol)
                        yield {"short_name": gene_symbol}

from variome_backend.management.VCFCallFilters.CallFilter import CallFilter
from typing import List, Dict, Any


class VariantsCallFilter(CallFilter):
    """
    Generates the 'variants' table (master variant list).
    """
    def __init__(self, vcf_file_path, settings):
        super().__init__(vcf_file_path, settings)

    def getTableRows(self):
        """
        Generator that yields variant rows one at a time.
        """
        seen = set()
        for record in self.vcf_record_stream():
            filter_val = ";".join(record.FILTER)
            type_info = record.INFO.get("TYPE")
            if isinstance(type_info, list) and type_info:
                # Variome vcf dialect uses TYPE in INFO for variant type
                var_type = type_info[0]
            else:
                #IBVL vcf dialect uses VARIANT_CLASS in CSQ for variant type
                var_classes = self.get_csq_values(record, "VARIANT_CLASS")
                var_type = var_classes[0] if isinstance(var_classes, list) and var_classes else None
            if self.is_mitochondrial(record):
                var_type = "M"
            elif var_type not in ["SNV", "SNP"] and var_type is not None:
                var_type = "INDEL"
            elif var_type is None:
                var_type = self.settings.NA
            for variant_id in self.make_variant_ids(record):
                if variant_id in seen:
                    continue
                seen.add(variant_id)
                yield {
                    'variant_id': variant_id,
                    'var_type': var_type,
                    'filter': filter_val if filter_val != "" else self.settings.NA
                }

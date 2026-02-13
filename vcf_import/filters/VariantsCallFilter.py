from .CallFilter import CallFilter
from typing import List, Dict, Any

from constants import NA

class VariantsCallFilter(CallFilter):
    """
    Generates the 'variants' table (master variant list).
    """
    def __init__(self, vcf_file_path: str):
        super().__init__(vcf_file_path)
    def getTableRows(self) -> List[Dict[str, Any]]:
        variants = {}
        for record in self.vcf_records:
            variant_id = self.make_variant_id(record)
            filter = ";".join(record.FILTER)
            type_info = record.INFO.get("TYPE")
            if isinstance(type_info, list) and type_info:
                # Variome vcf dialect uses TYPE in INFO for variant type
                var_type = type_info[0]
            else:
                #IBVL vcf dialect uses VARIANT_CLASS in CSQ for variant type
                var_classes = self.get_csq_values(record, "VARIANT_CLASS")
                var_type = var_classes[0] if isinstance(var_classes, list) and var_classes else None
            if var_type not in ["SNV", "SNP"] and var_type is not None:
                var_type = "INDEL"
            elif var_type is None:
                var_type = NA
                
#           
#            if var_type == []:
#                var_type = self.get_info_value(record, "TYPE")
            if variant_id not in variants:
                variants[variant_id] = {
                    'variant_id': variant_id, 
                    'var_type': var_type,
                    'filter': filter if filter != "" else NA
                }
                
        return list(variants.values())

from .CallFilter import CallFilter
from typing import List, Dict, Any
from vcf_import.constants import NA
import urllib.parse

class VariantsAnnotationsCallFilter(CallFilter):
    """
    Generates the 'variants_annotations' table.
    """
    def getTableRows(self):
        """
        Generator that yields annotation rows one at a time.
        """
        for record in self.vcf_record_stream():
            variant = self.make_variant_id(record)
            hgvsp_list = self.get_csq_values(record, "HGVSp")
            sift_list = self.get_csq_values(record, "SIFT")
            polyphen_list = self.get_csq_values(record, "PolyPhen")
            transcript_list = self.get_csq_values(record, "Feature")
            impact_list = self.get_csq_values(record, "IMPACT")
            l = len(hgvsp_list)
            if not (l == len(sift_list) == len(polyphen_list) == len(transcript_list)):
                def pad_list(lst, target_len):
                    return lst + [NA] * (target_len - len(lst))
                sift_list = pad_list(sift_list, l)
                polyphen_list = pad_list(polyphen_list, l)
            for i in range(l):
                hgvsp = urllib.parse.unquote(hgvsp_list[i]) if hgvsp_list[i] not in [NA, ""] else NA
                sift = sift_list[i]
                polyphen = polyphen_list[i]
                transcript = transcript_list[i]
                impact = impact_list[i] if impact_list and len(impact_list) > i else NA
                yield {
                    'hgvsp': hgvsp,
                    'sift': sift,
                    'polyphen': polyphen,
                    'transcript': transcript if transcript else NA,
                    'variant': variant,
                    'impact': impact
                }

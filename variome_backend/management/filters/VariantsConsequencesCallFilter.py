from variome_backend.management.filters.CallFilter import CallFilter
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VariantsConsequencesCallFilter(CallFilter):
    """
    Generates the 'variants_consequences' table.
    """
    def __init__(self, vcf_file_path, settings):
        super().__init__(vcf_file_path, settings)

    def getTableRows(self):
        """
        Generator that yields variant consequence rows one at a time.
        """
        for record in self.vcf_record_stream():
            variant = self.make_variant_id(record)
            transcript_list = self.get_csq_values(record, "Feature")
            consequence_list = self.get_csq_values(record, "Consequence")
            l = len(transcript_list)
            if l != len(consequence_list):
                continue
            for i in range(l):
                transcript = transcript_list[i]
                consequences = consequence_list[i].split("&")
                for consequence in consequences:
                    severity = self.severity_map.get(consequence)
                    if severity is not None:
                        yield {
                            'severity': severity,
                            'variant': variant,
                            'transcript': transcript if transcript else self.settings.NA,
                        }

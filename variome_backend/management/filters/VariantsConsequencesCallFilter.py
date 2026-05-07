from variome_backend.management.filters.CallFilter import CallFilter
from typing import List, Dict, Any
import logging
import os

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

        severity_map = {}
        """Load the consequence-to-severity mapping from the severities TSV file."""
        input_tsv_path = getattr(self.settings, "INPUT_TSV_PATH", None)
        if not input_tsv_path:
            logger.warning(
                "INPUT_TSV_PATH is not set; severity lookups will return no results"
            )
            return
        severity_table_path = os.path.join(input_tsv_path, "severities.tsv")
        try:
            with open(severity_table_path, "r") as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        severity, consequence = parts[0], parts[-1]
                        severity_map[consequence] = int(severity)
        except FileNotFoundError:
            logger.warning("Severity table file not found: %s", severity_table_path)


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
                    severity = severity_map.get(consequence)
                    if severity is not None:
                        yield {
                            'severity': severity,
                            'variant': variant,
                            'transcript': transcript if transcript else self.settings.NA,
                        }

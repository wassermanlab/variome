from variome_backend.management.VCFCallFilters.CallFilter import CallFilter
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VariantsTranscriptsCallFilter(CallFilter):
    """
    Generates the 'variants_transcripts' table.
    """
    def __init__(self, vcf_file_path, settings, mt_vcf_file_path=None):
        super().__init__(vcf_file_path, settings, mt_vcf_file_path)

    def getTableRows(self):
        """
        Generator that yields variant-transcript rows one at a time.
        """
        na = self.settings.NA
        seen = set()
        for record in self.shared_record_stream():
            transcript = self.get_csq_values(record, "Feature")
            variant = self.make_variant_id(record)
            hgvsc = self.get_csq_values(record, "HGVSc")
            l = len(transcript)
            lh = len(hgvsc)
            if l != lh:
                logging.warning(f"mismatched lengths for transcript and hgvsc: {l} vs {lh}")
                continue
            for i in range(l):
                t = transcript[i]
                h = hgvsc[i]
                if t == "NA" or t == "" or t is None:
                    t = na
                if h == "NA" or h == "" or h is None:
                    h = na
                key = (variant, t)
                if key in seen:
                    continue
                seen.add(key)
                yield {
                    'transcript': t,
                    'variant': variant,
                    'hgvsc': h
                }

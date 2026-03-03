from .CallFilter import CallFilter
from typing import List, Dict, Any
import logging
from vcf_import.tools import validate_get
logger = logging.getLogger(__name__)

class TranscriptsCallFilter(CallFilter):
    """
    Generates the 'transcripts' table.
    """
    def __init__(self, vcf_file_path, settings):
        super().__init__(vcf_file_path, settings)
    def getTableRows(self):
        """
        Generator that yields transcript rows one at a time.
        """
        seen = set()
        for record in self.vcf_record_stream():
            feature = self.get_csq_values(record, "Feature")
            if feature == "" or feature == "NA" or feature is None or len(feature) == 0:
                logger.warning("skipping transcript with no feature: %s", feature)
                feature = self.settings.NA
            symbol = self.get_csq_values(record, "SYMBOL")
            source = self.get_csq_values(record, "SOURCE")
            biotype = self.get_csq_values(record, "BIOTYPE")
            l = len(feature)
            tsl = [None] * l  # variome sets this to none (.)  it could be: self.get_csq_values(record, "TSL")
            if not (l == len(symbol) == len(source) == len(tsl)):
                continue
            for i in range(l):
                transcript_id = validate_get(feature, i)
                if transcript_id in seen:
                    continue
                seen.add(transcript_id)
                transcript_type = source[i]
                if transcript_type == "Ensembl":
                    transcript_type = "E"
                elif transcript_type == "RefSeq" or transcript_type == "Refseq":
                    transcript_type = "R"
                else:
                    if transcript_id is not self.settings.NA:
                        transcript_type = self.settings.DEFAULT_TRANSCRIPT_SOURCE
                    else:
                        transcript_type = self.settings.NA
                if not (biotype and biotype[i]):
                    biotype_val = self.settings.NA
                else:
                    biotype_val = biotype[i]
                yield {
                    'transcript_id': transcript_id,
                    'gene': validate_get(symbol, i),
                    'transcript_type': transcript_type,
                    'tsl': validate_get(tsl, i),
                    'biotype': biotype_val
                }

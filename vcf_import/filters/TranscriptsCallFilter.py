from .CallFilter import CallFilter
from typing import List, Dict, Any
from vcf_import.constants import NA, DEFAULT_TRANSCRIPT_SOURCE
import logging
from vcf_import.tools import validate_get
logger = logging.getLogger(__name__)

class TranscriptsCallFilter(CallFilter):
    """
    Generates the 'transcripts' table.
    """
    def getTableRows(self) -> List[Dict[str, Any]]:
        """
        Associate transcripts with genes from VEP annotations.
        Returns:
            List of dicts with structure: 
            {'transcript_id': str, 'gene': str, 'transcript_type': str, 'tsl': str}
        """
        transcripts = {}
        for record in self.vcf_records:
            feature = self.get_csq_values(record, "Feature")
            if feature == "" or feature == "NA" or feature is None or len(feature) == 0:
                logger.warning("skipping transcript with no feature: %s", feature)
                feature = NA
            symbol = self.get_csq_values(record, "SYMBOL")
            source = self.get_csq_values(record, "SOURCE")
            biotype = self.get_csq_values(record, "BIOTYPE")
            l = len(feature)
            tsl = [] # variome sets this to none (.)  it could be: self.get_csq_values(record, "TSL")
            for i in range(l):
                tsl.append(None)
            if not (l == len(symbol) == len(source) == len(tsl)):
#                logger.warning("mismatched lengths for transcript feature, symbol, source, tsl: %d vs %d vs %d vs %d", l, len(symbol), len(source), len(tsl))
                continue
            for i in range(l):
                transcript_id = validate_get(feature, i)

                if transcript_id not in transcripts:
                    transcript_type = source[i]
                    if transcript_type == "Ensembl":
                        transcript_type = "E"
                    elif transcript_type == "RefSeq" or transcript_type == "Refseq":
                        transcript_type = "R"
                    else:
                        if transcript_id is not NA:
                            transcript_type = DEFAULT_TRANSCRIPT_SOURCE
                        else:
                            transcript_type = NA
                    if biotype and biotype[i]:
                        pass
                    else:
                        biotype = NA
                    transcripts[transcript_id] = {
                        'transcript_id': transcript_id,
                        'gene': validate_get(symbol, i),
                        'transcript_type': transcript_type,
                        'tsl': validate_get(tsl, i),
                        'biotype': validate_get(biotype, i)
                    }
        return list(transcripts.values())

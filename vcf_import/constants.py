"""
Global constants for VCF import module.
"""
import os
import dotenv
import logging

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# fallback None value filler
VCF_FILE = os.getenv("VCF_FILE", None)  # Path to the input VCF file, can be set via environment variable
NA = os.getenv("NA", ".")
CHR_NOTATION = os.getenv("CHR_NOTATION", "False").lower() in ("true", "1", "t")  # whether to keep 'chr' prefix in chromosome names
HYPEN_VARIANT_NOTATION = os.getenv("HYPEN_VARIANT_NOTATION", "True").lower() in ("true", "1", "t")  # whether to use hyphen '-' in variant IDs instead of underscores '_'
DEFAULT_TRANSCRIPT_SOURCE = os.getenv("DEFAULT_TRANSCRIPT_SOURCE", "E")  # Default transcript source if unknown
CADD_DAMAGING_THRESHOLD = int(os.getenv("CADD_DAMAGING_THRESHOLD", 20))  # CADD phred score threshold (if greater than or equal, counts as damaging)
SEVERITIES_TSV_PATH = os.getenv("SEVERITIES_TSV_PATH", "data/fixtures/severities.tsv")  # Path to severity table file

logger.info(f"""

VCF Import settings:
  VCF_FILE={VCF_FILE},
  NA={NA},
  CHR_NOTATION={CHR_NOTATION},
  HYPEN_VARIANT_NOTATION={HYPEN_VARIANT_NOTATION},
  DEFAULT_TRANSCRIPT_SOURCE={DEFAULT_TRANSCRIPT_SOURCE},
  CADD_DAMAGING_THRESHOLD={CADD_DAMAGING_THRESHOLD},
  SEVERITIES_TSV_PATH={SEVERITIES_TSV_PATH}
"""
)
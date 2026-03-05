"""
Global constants for VCF import module.
"""
import os
import dotenv
import logging
from dataclasses import dataclass

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Settings:
    VCF_FILE: str
    NA: str
    OUT_USEHYPHENS: bool
    DEFAULT_TRANSCRIPT_SOURCE: str
    CADD_DAMAGING_THRESHOLD: int
    SEVERITIES_TSV_PATH: str
    HASH_COMPARE: str
    OUT_CHR_NOTATION: bool
    RANGES: str

SETTINGS = Settings(
    VCF_FILE=os.getenv("VCF_FILE", None),
    NA=os.getenv("NA", "."),
    OUT_CHR_NOTATION=os.getenv("OUT_CHR_NOTATION", "False").lower() in ("true", "1", "t"),
    OUT_USEHYPHENS=os.getenv("OUT_USEHYPHENS", "True").lower() in ("true", "1", "t"),
    DEFAULT_TRANSCRIPT_SOURCE=os.getenv("DEFAULT_TRANSCRIPT_SOURCE", "E"),
    CADD_DAMAGING_THRESHOLD=int(os.getenv("CADD_DAMAGING_THRESHOLD", 20)),
    SEVERITIES_TSV_PATH=os.getenv("SEVERITIES_TSV_PATH", "data/fixtures/severities.tsv"),
    HASH_COMPARE=os.getenv("HASH_COMPARE", None),
    RANGES=os.getenv("RANGES", None),
)
logger.info(SETTINGS)
logger.info(f"""

VCF Import settings:
  VCF_FILE={SETTINGS.VCF_FILE},
  NA={SETTINGS.NA},
  OUT_CHR_NOTATION={SETTINGS.OUT_CHR_NOTATION},
  OUT_USEHYPHENS={SETTINGS.OUT_USEHYPHENS},
  DEFAULT_TRANSCRIPT_SOURCE={SETTINGS.DEFAULT_TRANSCRIPT_SOURCE},
  CADD_DAMAGING_THRESHOLD={SETTINGS.CADD_DAMAGING_THRESHOLD},
  SEVERITIES_TSV_PATH={SETTINGS.SEVERITIES_TSV_PATH},
  RANGES={SETTINGS.RANGES}
""")
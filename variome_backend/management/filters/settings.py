"""
Settings dataclass for VCF import filters.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class VcfImportSettings:
    VCF_FILE: Optional[str]
    NA: str
    OUT_CHR: bool
    OUT_HYPHENS: bool
    DEFAULT_TRANSCRIPT_SOURCE: str
    CADD_DAMAGING_THRESHOLD: int
    SEVERITIES_TSV_PATH: str
    HASH_COMPARE: Optional[str]
    RANGES: Optional[str]

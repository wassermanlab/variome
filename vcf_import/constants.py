"""
Global constants for VCF publisher.
"""

NA = "."  # fallback None value filler
CHR_NOTATION = False  # whether to keep 'chr' prefix in chromosome names
HYPEN_VARIANT_NOTATION = True  # whether to use hyphen '-' in variant IDs instead of underscores '_'
DEFAULT_TRANSCRIPT_SOURCE = "E"  # Default transcript source if unknown
CADD_DAMAGING_THRESHOLD = 20  # CADD phred score threshold (if greater than or equal, counts as damaging)
from variome_backend.management.VCFCallFilters.CallFilter import CallFilter
from typing import List, Dict, Any
import json
import math

HISTOGRAM_BINS = 10
HOMOPLASMY_THRESHOLD = 0.95
COHORT_FIELDS = ("AC_hom", "AC_het", "AF_hom", "AF_het")


class MtBvlFrequenciesCallFilter(CallFilter):
    """
    Generates the 'mt_bvl_frequencies' table.
    """
    def __init__(self, vcf_file_path: str, settings):
        super().__init__(vcf_file_path, settings)

    @staticmethod
    def sample_heteroplasmy_levels(record, allele_index):
        """Valid per-sample FORMAT/AF of one ALT, including reference observations."""
        levels = []
        for call in record.calls:
            value = call.data.get("AF")
            if isinstance(value, list):
                value = value[allele_index] if allele_index < len(value) else None
            if value in (None, "", "."):
                continue
            level = float(value)
            if not math.isfinite(level) or not 0 <= level <= 1:
                raise ValueError(
                    f"Invalid FORMAT/AF {value} in sample {call.sample} "
                    f"at {record.CHROM}:{record.POS}"
                )
            levels.append(level)
        return levels

    @staticmethod
    def histogram(levels):
        bins = [0] * HISTOGRAM_BINS
        for level in levels:
            bins[min(int(level * HISTOGRAM_BINS + 1e-9), HISTOGRAM_BINS - 1)] += 1
        return ",".join(map(str, bins))

    def getTableRows(self) -> List[Dict[str, Any]]:
        rows = []
        seen = set()
        for record in self.vcf_record_stream():
            if not self.is_mitochondrial(record):
                continue
            def scalar(value):
                if isinstance(value, list):
                    return value[0] if value else None
                return value

            if scalar(record.INFO.get("AN")) not in (None, "", "."):
                # Variome dialect uses INFO; tabular IBVL metrics are normalized there.
                fields = record.INFO
            else:
                # IBVL VCF dialect supplies cohort metrics in a FORMAT/GT sample.
                fields = next(
                    (call.data for call in record.calls
                     if scalar(call.data.get("AN")) not in (None, "", ".")), {}
                )

            def number(name, cast, allele_index=0):
                value = fields.get(name)
                if isinstance(value, list):
                    value = value[allele_index] if allele_index < len(value) else None
                return cast(value) if value not in (None, "", ".") else None

            an = number("AN", int)
            derive_from_samples = "AF" in getattr(record, "FORMAT", [])
            if not an and not derive_from_samples:
                continue
            hl_histogram = fields.get("heteroplasmy_histogram")
            if isinstance(hl_histogram, list) and len(hl_histogram) == 1 and isinstance(hl_histogram[0], str):
                hl_histogram = hl_histogram[0]
            if isinstance(hl_histogram, str):
                if hl_histogram.startswith("{"):
                    hl_histogram = json.loads(hl_histogram)
                else:
                    hl_histogram = hl_histogram.replace("|", ",").split(",")
            if isinstance(hl_histogram, dict):
                hl_histogram = hl_histogram.get("bin_freq", [])
            hl_hist = ",".join(map(str, hl_histogram)) if hl_histogram else ""
            has_cohort_metrics = any(name in fields for name in COHORT_FIELDS)
            for allele_index, variant in enumerate(self.make_variant_ids(record)):
                if variant in seen:
                    continue
                seen.add(variant)
                allele_hist = hl_hist
                max_hl = number("max_observed_heteroplasmy", float, allele_index)
                allele_an = an
                ac_hom = number("AC_hom", int, allele_index)
                ac_het = number("AC_het", int, allele_index)
                af_hom = number("AF_hom", float, allele_index)
                af_het = number("AF_het", float, allele_index)
                if derive_from_samples:
                    levels = self.sample_heteroplasmy_levels(record, allele_index)
                    carriers = [level for level in levels if level > 0]
                    if carriers and not allele_hist:
                        allele_hist = self.histogram(carriers)
                    if levels and max_hl is None:
                        max_hl = max(levels)
                    if levels and not has_cohort_metrics:
                        # MT frequencies count observed samples, not diploid GT alleles.
                        allele_an = len(levels)
                        ac_hom = sum(level >= HOMOPLASMY_THRESHOLD for level in levels)
                        ac_het = sum(0 < level < HOMOPLASMY_THRESHOLD for level in levels)
                        af_hom = ac_hom / allele_an
                        af_het = ac_het / allele_an
                rows.append({
                    'variant': variant,
                    'an': allele_an,
                    'ac_hom': ac_hom,
                    'ac_het': ac_het,
                    'af_hom': af_hom,
                    'af_het': af_het,
                    'hl_hist': allele_hist,
                    'max_hl': max_hl
                })
        return rows

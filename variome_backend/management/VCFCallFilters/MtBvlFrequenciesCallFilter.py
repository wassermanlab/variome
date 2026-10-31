from variome_backend.management.VCFCallFilters.CallFilter import CallFilter
from typing import List, Dict, Any
import json

HISTOGRAM_BINS = 10


class MtBvlFrequenciesCallFilter(CallFilter):
    """
    Generates the 'mt_bvl_frequencies' table.
    """
    def __init__(self, vcf_file_path: str, settings):
        super().__init__(vcf_file_path, settings)

    @staticmethod
    def sample_heteroplasmy_levels(record, allele_index):
        """Per-sample FORMAT/AF (heteroplasmy level) of carriers of one ALT allele."""
        levels = []
        for call in record.calls:
            value = call.data.get("AF")
            if isinstance(value, list):
                value = value[allele_index] if allele_index < len(value) else None
            if value in (None, "", "."):
                continue
            level = float(value)
            if level > 0:
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
            if not an:
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
            derive_from_samples = (
                fields is record.INFO and "AF" in getattr(record, "FORMAT", [])
            )
            for allele_index, variant in enumerate(self.make_variant_ids(record)):
                if variant in seen:
                    continue
                seen.add(variant)
                allele_hist = hl_hist
                max_hl = number("max_observed_heteroplasmy", float, allele_index)
                if derive_from_samples:
                    # Without cohort metrics, sample FORMAT/AF values are heteroplasmy levels
                    levels = self.sample_heteroplasmy_levels(record, allele_index)
                    if levels and not allele_hist:
                        allele_hist = self.histogram(levels)
                    if levels and max_hl is None:
                        max_hl = max(levels)
                rows.append({
                    'variant': variant,
                    'an': an,
                    'ac_hom': number("AC_hom", int, allele_index),
                    'ac_het': number("AC_het", int, allele_index),
                    'af_hom': number("AF_hom", float, allele_index),
                    'af_het': number("AF_het", float, allele_index),
                    'hl_hist': allele_hist,
                    'max_hl': max_hl
                })
        return rows

from variome_backend.management.VCFCallFilters.CallFilter import CallFilter
from typing import List, Dict, Any
import json


class MtBvlFrequenciesCallFilter(CallFilter):
    """
    Generates the 'mt_bvl_frequencies' table.
    """
    def __init__(self, vcf_file_path: str, settings):
        super().__init__(vcf_file_path, settings)

    def getTableRows(self) -> List[Dict[str, Any]]:
        rows = []
        seen = set()
        for record in self.vcf_record_stream():
            if not self.is_mitochondrial(record):
                continue
            variant = self.make_variant_id(record)
            if variant in seen:
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

            def number(name, cast):
                value = scalar(fields.get(name))
                return cast(value) if value not in (None, "", ".") else None

            an = number("AN", int)
            if not an:
                continue
            seen.add(variant)
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
            rows.append({
                'variant': variant,
                'an': an,
                'ac_hom': number("AC_hom", int),
                'ac_het': number("AC_het", int),
                'af_hom': number("AF_hom", float),
                'af_het': number("AF_het", float),
                'hl_hist': hl_hist,
                'max_hl': number("max_observed_heteroplasmy", float)
            })
        return rows

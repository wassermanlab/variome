import csv
from types import SimpleNamespace

from .CallFilter import CallFilter


class MtGnomadFrequenciesCallFilter(CallFilter):
    """Intersect the documented gnomAD MT TSV with mitochondrial VCF variants."""

    def __init__(self, vcf_file_path, settings, tsv_path=None):
        super().__init__(vcf_file_path, settings)
        self.tsv_path = tsv_path

    def getTableRows(self):
        if not self.tsv_path:
            return
        variants = {
            self.make_variant_id(record)
            for record in self.vcf_record_stream()
            if self.is_mitochondrial(record)
        }
        seen = set()
        with open(self.tsv_path, encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                record = SimpleNamespace(
                    CHROM=row.get("chromosome") or row.get("chr") or row.get("chrom"),
                    POS=int(row.get("position") or row.get("pos")),
                    REF=row["ref"],
                    ALT=[SimpleNamespace(value=row["alt"])],
                )
                if not self.is_mitochondrial(record):
                    continue
                variant = self.make_variant_id(record)
                if variant not in variants or variant in seen:
                    continue
                seen.add(variant)

                def number(name, cast):
                    value = row.get(name)
                    return cast(value) if value not in (None, "", ".") else None

                yield {
                    "variant": variant,
                    "an": number("AN", int),
                    "ac_hom": number("AC_hom", int),
                    "ac_het": number("AC_het", int),
                    "af_hom": number("AF_hom", float),
                    "af_het": number("AF_het", float),
                    "max_hl": number("max_observed_heteroplasmy", float),
                }

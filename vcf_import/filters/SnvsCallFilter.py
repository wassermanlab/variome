from venv import logger
from .CallFilter import CallFilter
from typing import List, Dict, Any, Optional
from vcf_import.constants import NA, CHR_NOTATION, CADD_DAMAGING_THRESHOLD

class SnvsCallFilter(CallFilter):
    """
    Generates the 'snvs' table (SNV-specific annotations).
    """
    def __init__(self, vcf_file_path: str, assembly: Optional[str] = None):
        super().__init__(vcf_file_path)
        self.assembly = assembly
    def getTableRows(self):
        """
        Generator that yields SNV rows one at a time.
        """
        seen = set()
        for record in self.vcf_record_stream():
            variant = self.make_variant_id(record)
            if variant in seen:
                continue
            seen.add(variant)
            chrom = record.CHROM.replace("chr", "") if not CHR_NOTATION else record.CHROM
            pos = record.POS
            ref = record.REF
            alt = record.ALT[0].value  # assuming single ALT allele

            class_list = self.get_csq_values(record, "VARIANT_CLASS")
            cadd_phred_list = record.INFO.get("CADD_PHREDscore", self.get_csq_values(record, "CADD_PHRED")) # variome: CADD_PHREDscore in info; ibvl: CADD_PHRED in csq!
            existing_variation_list = self.get_csq_values(record, "Existing_variation")
            ds_ag_list = self.get_csq_values(record, "DS_AG")
            ds_al_list = self.get_csq_values(record, "DS_AL")
            ds_dg_list = self.get_csq_values(record, "DS_DG")
            ds_dl_list = self.get_csq_values(record, "DS_DL")
            dbsnp_ids = []

            clinvar_vcvs = []
            clinvar_from_info = record.INFO.get("ClinVar_Variation_ID", None)
            for ev in existing_variation_list:
                if ev.startswith("rs"):
                    dbsnp_ids.append(ev)
                if ev.startswith("VCV"):
                    clinvar_vcvs.append(ev)
            variant_class = record.INFO.get("TYPE")[0] if record.INFO.get("TYPE") else (class_list[0] if class_list else NA)
            if cadd_phred_list and cadd_phred_list[0] != "":
                try:
                    cadd_score = float(cadd_phred_list[0])
                    if float(cadd_score).is_integer():
                        cadd_score = str(cadd_score).replace('.0', '')
                except (ValueError, TypeError):
                    cadd_score = None
            else:
                cadd_score = None
            
            # Determine variant length
            if variant_class in ["SNV", "SNP"]:
                var_length = 1
            else:
                var_length = abs(len(alt) - len(ref)) + 1
                
            # other options:
#            elif variant_class in ["INS", "DEL"]:
#                var_length = abs(len(alt) - len(ref))
#            elif variant_class in ["INDEL"]:
#                var_length = max(len(ref), len(alt))

            # CADD interpretation (threshold 20)
            if cadd_score is not None:
                cadd_intr = "Damaging" if float(cadd_score) >= 20 else "Tolerable"
            else:
                cadd_score = NA
                cadd_intr = NA

            # Max SpliceAI score
            # Detect VCF dialect for SpliceAI
            spliceai_info = record.INFO.get("SpliceAI")
            if spliceai_info:
                # SpliceAI is in INFO field (e.g., T|TTC28|0.00|0.00|0.01|0.00|...)
                # Can be a list, take first if so
                if isinstance(spliceai_info, list):
                    spliceai_str = spliceai_info[0]
                else:
                    spliceai_str = spliceai_info
                spliceai_parts = spliceai_str.split("|")
                # AG, AL, DG, DL are 3rd, 4th, 5th, 6th fields (0-based: 2,3,4,5)
                splice_ai_raw = [spliceai_parts[i] if len(spliceai_parts) > i else '.' for i in range(2,6)]
            else:
                # Fallback: use DS_* from CSQ
                splice_ai_raw = ds_ag_list + ds_al_list + ds_dg_list + ds_dl_list
            # If all are '.' (or empty), set splice_ai to '.'
            if all((s == '.' or s == '' or s is None) for s in splice_ai_raw):
                max_splice_ai = NA
            else:
                splice_ai_scores = []
                for score in splice_ai_raw:
                    try:
                        splice_ai_scores.append(float(score))
                    except (ValueError, TypeError):
                        continue
                if splice_ai_scores:
                    max_splice_ai = max(splice_ai_scores)
                    if float(max_splice_ai).is_integer():
                        max_splice_ai = str(max_splice_ai).replace('.0', '')
                else:
                    max_splice_ai = NA
            window = 25
            chrom_noprefix = chrom.replace("chr", "") if chrom.startswith("chr") else chrom
            start = max(1, pos - window)
            end = pos + window
            ucsc_url = f"https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&highlight=hg38.{chrom_noprefix}%3A{pos}-{pos}&position={chrom_noprefix}%3A{start}-{end}"
            ensembl_url = f"https://asia.ensembl.org/Homo_sapiens/Location/View?r={chrom_noprefix}%3A{start}-{end}"
            gnomad_url = f"https://gnomad.broadinstitute.org/variant/{chrom_noprefix}-{pos}-{ref}-{alt}?dataset=gnomad_r4"
            dbsnp_url = f"https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs={dbsnp_ids[0]}" if dbsnp_ids else NA
            if (clinvar_vcvs and clinvar_vcvs[0].startswith("VCV")):
                clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{clinvar_vcvs[0][3:]}/"
            elif clinvar_from_info:
                clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{clinvar_from_info}/"
            else:
                clinvar_url = NA
            yield {
                'variant': variant,
                'type': variant_class,
                'length': var_length,
                'chr': chrom,
                'pos': pos,
                'ref': ref,
                'alt': alt,
                'cadd_score': cadd_score,
                'cadd_intr': cadd_intr,
                'dbsnp_id': NA, # variome currently is . but it could be: dbsnp_ids[0] if dbsnp_ids else NA,
                'dbsnp_url': NA, # variome currently is . but could be: dbsnp_url,
                'ucsc_url': ucsc_url,
                'ensembl_url': ensembl_url,
                'clinvar_url': clinvar_url,
                'gnomad_url': gnomad_url,
                "clinvar_vcv": clinvar_vcvs[0] if clinvar_vcvs else clinvar_from_info if clinvar_from_info else NA,
                "splice_ai": max_splice_ai
            }

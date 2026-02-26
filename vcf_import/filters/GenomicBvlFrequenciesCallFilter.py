from asyncio.log import logger
import logging

from numpy import record
from .CallFilter import CallFilter
from typing import List, Dict, Any
from vcf_import.constants import NA
from vcf_import.tools import validate_get

class GenomicBvlFrequenciesCallFilter(CallFilter):
    """
    Generates the 'genomic_bvl_frequencies' table.
    """
    def getTableRows(self):
        """
        Generator that yields genomic BVL frequency rows one at a time.
        """
        for record in self.vcf_record_stream():
            if (record.POS == 27019487):
                logger.info(f"Processing record {record.ID} at {record.CHROM}:{record.POS}")

            variant = self.make_variant_id(record)
            qual = record.QUAL
            info = record.INFO

            def parse_info_field(field):
                values = info.get(field, None)
                if values is None:
                    return [None, None, None]
                return values[0:3]

            if "AF_tot_XX_XY" in info:
                #ibvl style
                af_tot, af_xx, af_xy = parse_info_field("AF_tot_XX_XY")
                ac_tot, ac_xx, ac_xy = parse_info_field("AC_tot_XX_XY")
                an_tot, an_xx, an_xy = parse_info_field("AN_tot_XX_XY")
                hom_tot, hom_xx, hom_xy = parse_info_field("hom_tot_XX_XY")
                yield {
                    'variant': variant,
                    'af_tot': af_tot,
                    'ac_tot': ac_tot,
                    'an_tot': an_tot,
                    'hom_tot': hom_tot,
                    'af_xx': af_xx,
                    'af_xy': af_xy,
                    'ac_xy': ac_xy,
                    'an_xx': an_xx,
                    'ac_xx': ac_xx,
                    'an_xy': an_xy,
                    'hom_xx': hom_xx,
                    'hom_xy': hom_xy,
                    'quality': qual
                }
            else:
                #variome style
                af_tot = info.get("AF", None)
                af_xx = info.get("AF_XX", None)
                af_xy = info.get("AF_XY", None)
                ac_tot = info.get("AC", None)
                ac_xx = info.get("AC_XX", None)
                ac_xy = info.get("AC_XY", None)
                an_tot = info.get("AN", None)
                an_xx = info.get("AN_XX", None)
                an_xy = info.get("AN_XY", None)
                hom_tot = info.get("numhomalt", None)
                hom_xx = info.get("numhomalt_XX", None)
                hom_xy = info.get("numhomalt_XY", None)
                hemi_tot = info.get("numhemi", None)
                hemi_xx = info.get("numhemi_XX", None)
                hemi_xy = info.get("numhemi_XY", None)
                l = len(ac_tot) if ac_tot is not None else 0
                for i in range(l):
                    try:
                        yield {
                            'variant': variant,
                            'af_tot': validate_get(af_tot, i),
                            'ac_tot': validate_get(ac_tot, i),
                            'an_tot': validate_get(an_tot, i),
                            'hom_tot': validate_get(hom_tot, i),
                            'hemi_tot': validate_get(hemi_tot, i),
                            'af_xx': validate_get(af_xx, i),
                            'af_xy': validate_get(af_xy, i),
                            'ac_xx': validate_get(ac_xx, i),
                            'ac_xy': validate_get(ac_xy, i),
                            'an_xx': validate_get(an_xx, i),
                            'an_xy': validate_get(an_xy, i),
                            'hom_xx': validate_get(hom_xx, i),
                            'hom_xy': validate_get(hom_xy, i),
                            'hemi_xx': validate_get(hemi_xx, i),
                            'hemi_xy': validate_get(hemi_xy, i),
                            'quality': qual
                        }
                    except Exception as e:
                        logging.warning(f"Error parsing frequency fields for variant {variant}: {e}")

from rest_framework import viewsets
from django.contrib.auth.decorators import login_required

from ..models import (
    Variant,
    VariantTranscript
)


def snv_annotations(variant_id, database=None):
    """ gets the annotations for a variant's transcripts, organized by gene name """
    errors = []
    transcripts_by_gene = []
    
    try:

        values_names = {
            "transcript__gene__short_name": "gene",
            "transcript__transcript_id": "transcript",
            "consequence__severity__consequence": "consequence",
            "annotation__impact": "impact",
            "transcript__biotype": "biotype",
            "transcript__transcript_type": "database",
            "hgvsc": "hgvsc",
            "annotation__hgvsp": "hgvsp",
#            "annotation__polyphen": "polyphen",
#            "annotation__sift": "sift",
#            "variant__snv__cadd_intr": "cadd intr",
#            "variant__snv__cadd_score": "cadd score",
        }
        
        variant_effects = (
            VariantTranscript.objects.filter(
                variant__variant_id=variant_id
            )
            .values(*values_names.keys())
            .all()
        )

        if len(variant_effects) == 0:
            raise VariantTranscript.DoesNotExist
#        print("transcripts", transcripts)
        variant_effects = [
            {values_names[key]: value for key, value in transcript.items()}
            for transcript in variant_effects
        ]

        for t in variant_effects:
            gene = t["gene"]
            gene_exists = any(
                gene == gene_dict["gene"] for gene_dict in transcripts_by_gene
            )
            if gene_exists:
                for d in transcripts_by_gene:
                    d["transcripts"].append(t) if d.get("gene") == gene else None
            else:
                transcripts_by_gene.append({"gene": gene, "transcripts": [t]})

    #        for transcript in transcripts:
    #            print("transcript", transcript, "\n")
    #        print("transcripts by gene", transcripts_by_gene)
    except Variant.DoesNotExist:
        errors.append("Variant ID was not found: " + variant_id)

    except VariantTranscript.DoesNotExist:
        return None
#        errors.append("No Transcripts were found for variant: " + variant_id)

    return {"annotations": transcripts_by_gene, "errors": errors}

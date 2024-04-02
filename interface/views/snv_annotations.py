from rest_framework import viewsets
from interface.models import (
    Variant,
    Gene,
    Transcript,
    VariantTranscript,
    VariantAnnotation,
    VariantConsequence,
)
from interface.serializers import (
    VariantTranscriptSerializer,
    VariantConsequenceSerializer,
    VariantAnnotationSerializer,
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.http import Http404
from django.http.response import JsonResponse


@api_view(["GET"])
def snv_annotations(request, variant_id, **kwargs):
    """ gets the annotations for a variant's transcripts, organized by gene name """
    errors = []
    transcripts_by_gene = []
    database = request.GET.get(
        "transcript_database", None
    )  # E for Ensembl or R for Refseq
    if database is None or database not in ["E", "R"]:
        errors.append("Database type is required or invalid.")
        pass

    json = kwargs.get("JSON", False)

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
            "annotation__polyphen": "polyphen",
            "annotation__sift": "sift",
            "variant__snv__cadd_intr": "cadd intr",
            "variant__snv__cadd_score": "cadd score",
        }
        transcripts = (
            VariantTranscript.objects.filter(
                variant__variant_id=variant_id, transcript__transcript_type=database
            )
            .values(*values_names.keys())
            .all()
        )

        if len(transcripts) == 0:
            raise VariantTranscript.DoesNotExist

        transcripts = [
            {values_names[key]: value for key, value in transcript.items()}
            for transcript in transcripts
        ]

        for t in transcripts:
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
        errors.append("No Transcripts were found for variant: " + variant_id)

    if request.method == "GET":
        data_out = {"annotations": transcripts_by_gene, "errors": errors}

        if json:
            return JsonResponse(data_out)
        else:
            return Response(data_out)

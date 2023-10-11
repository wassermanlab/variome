from rest_framework import viewsets
from interface.models import (
    Variant,
    Gene,
    Transcript,
    VariantTranscript,
    VariantAnnotation,
    VariantConsequence
)
from interface.serializers import (
    VariantTranscriptSerializer,
    VariantConsequenceSerializer,
    VariantAnnotationSerializer
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.http import Http404
from django.http.response import JsonResponse

@api_view(['GET'])
def snv_annotations(request, variant_id, **kwargs):
    """
    """

    json = kwargs.get('JSON', False)

    try:
        # Get all relevant information from the database 
        variant = Variant.objects.get(variant_id=variant_id)
        variants_transcripts = VariantTranscript.objects.filter(variant_id=variant.id)
        variants_consequences = VariantConsequence.objects.filter(variant_transcript__in=variants_transcripts)
        variants_annotations = VariantAnnotation.objects.filter(variant_transcript__in=variants_transcripts)
    except Variant.DoesNotExist:
        raise Http404
    except VariantTranscript.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        data_out = []
        #for variant_transcript in variants_transcripts:
        #    data = {
        #        "variant_transcript": VariantTranscriptSerializer(variant_transcript).data
        #    }
        #    data_out.append(data)
        for variant_consequence in variants_consequences:
            data = {
                "variant_consequence": VariantConsequenceSerializer(variant_consequence).data
            }
            data_out.append(data)
        for variant_annotation in variants_annotations:
            data = {
                "variant_annotation": VariantAnnotationSerializer(variant_annotation).data
            }
            data_out.append(data)

        if json:
            return JsonResponse(data_out)
        else:
            return Response(data_out)
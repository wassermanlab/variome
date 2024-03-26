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
    except Variant.DoesNotExist:
        raise Http404
    except VariantTranscript.DoesNotExist:
        # TODO: Change this to return no transcripts instead of throwing an error
        raise Http404

    if request.method == 'GET':
        data_out = {}
        for variant_consequence in variants_consequences:
            # TODO: Sort transcripts by transcript type
            severity = variant_consequence.severity.consequence

            try:
                annotation = VariantAnnotation.objects.get(variant_transcript=variant_consequence.variant_transcript)
                annotation = VariantAnnotationSerializer(annotation).data
            except VariantAnnotation.DoesNotExist:
                annotation = {}

            severity_dict = {
                "severity_number": variant_consequence.severity.severity_number,
                "transcript": VariantConsequenceSerializer(variant_consequence).data,
                "annotations": annotation
            }
            
            try:
                data_out[severity].append(severity_dict)
            except KeyError:
                data_out[severity] = [severity_dict]

        if json:
            return JsonResponse(data_out)
        else:
            return Response(data_out)
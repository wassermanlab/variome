from rest_framework import viewsets
from interface.models import (
    Variant,
    GenomicGnomadFrequency,
    GenomicIBVLFrequency
)
from interface.serializers import (
    GenomicGnomadFrequencySerializer,
    GenomicIBVLFrequencySerializer
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.http import Http404
from django.http.response import JsonResponse

@api_view(['GET'])
def genomic_population_frequencies(request, variant_id, **kwargs):
    """
    """

    json = kwargs.get('JSON', False)

    try:
        # Get all relevant information from the database 
        variant = Variant.objects.get(variant_id=variant_id)
        gen_gnomad_freqs = GenomicGnomadFrequency.objects.filter(variant_id=variant.id)
        gen_ibvl_freqs = GenomicIBVLFrequency.objects.filter(variant_id=variant.id)
    except Variant.DoesNotExist:
        raise Http404
    except VariantTranscript.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        data_out = []
        for gen_gnomad_freq in gen_gnomad_freqs:
            data = {
                "genomic_gnomad_freq": GenomicGnomadFrequencySerializer(gen_gnomad_freq).data
            }
            data_out.append(data)
        for gen_ibvl_freq in gen_ibvl_freqs:
            data = {
                "genomic_ibvl_freq": GenomicIBVLFrequencySerializer(gen_ibvl_freq).data
            }
            data_out.append(data)

        if json:
            return JsonResponse(data_out)
        else:
            return Response(data_out)
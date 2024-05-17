from rest_framework import viewsets
from ibvl.models import (
    Variant,
    GenomicGnomadFrequency,
    GenomicVariomeFrequency
)
from ibvl.serializers import (
    GenomicGnomadFrequencySerializer,
    GenomicVariomeFrequencySerializer
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
        gen_gnomad_freq = GenomicGnomadFrequency.objects.get(variant_id=variant.id)
        gen_ibvl_freq = GenomicVariomeFrequency.objects.get(variant_id=variant.id)
    except Variant.DoesNotExist:
        return JsonResponse({"errors":["variant_id not found"]}, status=404)
    except GenomicGnomadFrequency.DoesNotExist:
        return JsonResponse({"errors":["genomic gnomad frequency not found for this variant"]}, status=404)
    except GenomicVariomeFrequency.DoesNotExist:
        return JsonResponse({"errors":["genomic variome frequency not found for this variant"]}, status=404)

    if request.method == 'GET':
        data_out = {
            "genomic_gnomad_freq": GenomicGnomadFrequencySerializer(gen_gnomad_freq).data,
            "genomic_ibvl_freq": GenomicVariomeFrequencySerializer(gen_ibvl_freq).data
        }
        #data_out = []
        #for gen_gnomad_freq in gen_gnomad_freqs:
        #    data = {
        #        "genomic_gnomad_freq": GenomicGnomadFrequencySerializer(gen_gnomad_freq).data
        #    }
        #    data_out.append(data)
        #for gen_ibvl_freq in gen_ibvl_freqs:
        #    data = {
        #        "genomic_ibvl_freq": GenomicVariomeFrequencySerializer(gen_ibvl_freq).data
        #    }
        #    data_out.append(data)

        if json:
            return JsonResponse(data_out)
        else:
            return Response(data_out)
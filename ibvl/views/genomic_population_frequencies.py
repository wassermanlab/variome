from rest_framework import viewsets
from django.contrib.auth.decorators import login_required

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
@login_required
def genomic_population_frequencies(request, variant_id, **kwargs):
    """
    """

    json = kwargs.get('JSON', False)

    data_out = {}
    try:
        # Get all relevant information from the database 
        errors = []
        variant = Variant.objects.get(variant_id=variant_id)
    except Variant.DoesNotExist:
        errors.append("variant_id not found")
        return JsonResponse({"errors":errors}, status=404)
    
    try:
        gen_gnomad_freq = GenomicGnomadFrequency.objects.get(variant_id=variant.id)
        data_out["genomic_gnomad_freq"] = GenomicGnomadFrequencySerializer(gen_gnomad_freq).data
    except GenomicGnomadFrequency.DoesNotExist:
        errors.append("genomic gnomad frequency not found for this variant")
#        return JsonResponse({"errors":["genomic gnomad frequency not found for this variant"]}, status=404)
    
    try:
        gen_ibvl_freq = GenomicVariomeFrequency.objects.get(variant_id=variant.id)
        data_out["genomic_ibvl_freq"] = GenomicVariomeFrequencySerializer(gen_ibvl_freq).data
    except GenomicVariomeFrequency.DoesNotExist:
        errors.append("genomic variome frequency not found for this variant")
#        return JsonResponse({"errors":["genomic variome frequency not found for this variant"]}, status=404)

    if request.method == 'GET':
        data_out["errors"] = errors
        

        if json:
            return JsonResponse(data_out)
        else:
            return Response(data_out)
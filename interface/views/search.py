import json
from rest_framework import viewsets
from interface.models import (
    Variant,
)
from interface.serializers import (
    VariantSerializer,
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.http import Http404
from django.http.response import JsonResponse

@api_view(['POST'])
def snv_search(request, **kwargs):
    """
    """
    json_content = kwargs.get('JSON', False)
    variant_id = json.loads(request.body)["variant_id"]

    try:
        # Get all relevant information from the database 
        #variant = Variant.objects.get(variant_id=variant_id)
        variants = Variant.objects.filter(variant_id__startswith=variant_id).values_list('variant_id', flat=True)
    except Variant.DoesNotExist:
        variants = None

    if request.method == 'POST':
        if variants:
            # Only send at most 10 variants
            data_out = {
                "variants": list(variants)[:10],
            }
        else:
            data_out = {
                "variants": [],
            }

        if json_content:
            return JsonResponse(data_out)
        else:
            return Response(data_out)
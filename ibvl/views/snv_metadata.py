from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from ibvl.models import (
    Variant,
    SNV
)
from ibvl.serializers import (
    SNVSerializer
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.http import Http404
from django.http.response import JsonResponse

@api_view(['GET'])
@login_required
def snv_metadata(request, variant_id, **kwargs):
    """
    """

    json = kwargs.get('JSON', False)

    try:
        variant = Variant.objects.get(variant_id=variant_id)
        snv = SNV.objects.get(variant=variant)
    except Variant.DoesNotExist:
        raise Http404
    except SNV.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = SNVSerializer(snv)

        if json:
            return JsonResponse(serializer.data)
        else:
            return Response(serializer.data)
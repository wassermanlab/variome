


from ..models import Variant, SNV
from ..serializers import SNVSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import Http404
from django.http.response import JsonResponse
from django.views.decorators.cache import never_cache


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@never_cache
def snv_metadata(request, variant_id, **kwargs):
    """ """

    json = kwargs.get("JSON", False)

    try:
        variant = Variant.objects.get(variant_id=variant_id)
        snv = SNV.objects.get(variant=variant)
    except Variant.DoesNotExist:
        raise Http404
    except SNV.DoesNotExist:
        raise Http404

    if request.method == "GET":
        serializer = SNVSerializer(snv)

        if json:
            return JsonResponse(serializer.data)
        else:
            return Response(serializer.data)

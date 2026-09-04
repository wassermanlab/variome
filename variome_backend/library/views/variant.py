from ..models import (
    Variant,
    SNV,
    GenomicGnomadFrequency,
    GenomicVariomeFrequency,
    VariantAnnotation,
)
from datetime import datetime

from ..serializers import (
    VariantSerializer,
    GenomicGnomadFrequencySerializer,
    GenomicVariomeFrequencySerializer,
    VariantAnnotationSerializer,
    SNVSerializer,
)

from .snv_annotations import snv_annotations

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from django.http import Http404
from rest_framework.response import Response
from django.views.decorators.cache import never_cache

from variome_backend.library_access.decorators import access_count_gate


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@access_count_gate()
@never_cache
def variant(request, id):
    """_summary_

    Args:
        request (_type_): the request, might not be needed
        id (_type_): the variant id (db id / primary key)

    Returns:
        _type_: the variant object. Depending on the var_type, could
        have different fields
    """

    now = datetime.now()
    errors = []

    try:
        variant = Variant.objects.get(id=id)
    except Variant.DoesNotExist:
        return Response({"errors": ["Variant not found"]}, status=404)

    #    print(f"variant_type: {variant.var_type}")

    snv = None
    gnomadFrequences = None
    bvlFrequencies = None
    annotations = None

    try:
        snv = SNV.objects.get(variant=variant)
        snv = SNVSerializer(snv).data
    except SNV.DoesNotExist:
        errors.append(f"SNV for variant {variant} not found")
        snv = None
    try:
        annotationsResult = snv_annotations(variant.variant_id)
        annotations = annotationsResult["annotations"]
        errors.append(annotationsResult["errors"])

    except Exception:
        errors.append("Error getting annotations")

    try:
        gnomadFrequenciesObject = GenomicGnomadFrequency.objects.get(
            variant_id=variant.id
        )
        gnomadFrequences = GenomicGnomadFrequencySerializer(
            gnomadFrequenciesObject
        ).data
    except GenomicGnomadFrequency.DoesNotExist:
        errors.append("genomic gnomad frequency not found for this variant")

    try:
        variomeFrequenciesObject = GenomicVariomeFrequency.objects.get(
            variant_id=variant.id
        )
        bvlFrequencies = GenomicVariomeFrequencySerializer(
            variomeFrequenciesObject
        ).data
    except GenomicVariomeFrequency.DoesNotExist:
        errors.append("genomic variome frequency not found for this variant")

    duration = datetime.now() - now
    return Response(
        {
            "variant": VariantSerializer(variant).data,
            "snv": snv,
            "gnomadFrequencies": gnomadFrequences,
            "bvlFrequencies": bvlFrequencies,
            "annotations": annotations,
            "errors": errors,
            "duration_ms": int(duration.total_seconds() * 1000),
        }
    )

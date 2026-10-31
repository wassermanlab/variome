from ..models import (
    Variant,
    SNV,
    GenomicGnomadFrequency,
    GenomicVariomeFrequency,
    MT,
    MtGnomadFrequency,
    MtVariomeFrequency,
)
from datetime import datetime

from ..serializers import (
    VariantSerializer,
    GenomicGnomadFrequencySerializer,
    GenomicVariomeFrequencySerializer,
    SNVSerializer,
    MTSerializer,
    MtGnomadFrequencySerializer,
    MtVariomeFrequencySerializer,
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
    mt = None
    gnomadFrequences = None
    bvlFrequencies = None
    annotations = None

    is_mt = variant.var_type == "M"
    variant_model = MT if is_mt else SNV
    variant_serializer = MTSerializer if is_mt else SNVSerializer
    try:
        detail = variant_serializer(variant_model.objects.get(variant=variant)).data
        if is_mt:
            mt = detail
        else:
            snv = detail
    except variant_model.DoesNotExist:
        errors.append(f"{'MT' if is_mt else 'SNV'} for variant {variant} not found")
    try:
        annotationsResult = snv_annotations(variant.variant_id)
        annotations = annotationsResult["annotations"]
        errors.append(annotationsResult["errors"])

    except Exception:
        errors.append("Error getting annotations")

    gnomad_model = MtGnomadFrequency if is_mt else GenomicGnomadFrequency
    gnomad_serializer = (
        MtGnomadFrequencySerializer if is_mt else GenomicGnomadFrequencySerializer
    )
    variome_model = MtVariomeFrequency if is_mt else GenomicVariomeFrequency
    variome_serializer = (
        MtVariomeFrequencySerializer if is_mt else GenomicVariomeFrequencySerializer
    )

    try:
        gnomadFrequenciesObject = gnomad_model.objects.get(
            variant_id=variant.id
        )
        gnomadFrequences = gnomad_serializer(
            gnomadFrequenciesObject
        ).data
    except gnomad_model.DoesNotExist:
        errors.append(
            f"{'mitochondrial' if is_mt else 'genomic'} gnomad frequency not found for this variant"
        )

    try:
        variomeFrequenciesObject = variome_model.objects.get(
            variant_id=variant.id
        )
        bvlFrequencies = variome_serializer(
            variomeFrequenciesObject
        ).data
    except variome_model.DoesNotExist:
        errors.append(
            f"{'mitochondrial' if is_mt else 'genomic'} variome frequency not found for this variant"
        )

    duration = datetime.now() - now
    return Response(
        {
            "variant": VariantSerializer(variant).data,
            "snv": snv,
            "mt": mt,
            "gnomadFrequencies": gnomadFrequences,
            "bvlFrequencies": bvlFrequencies,
            "annotations": annotations,
            "errors": errors,
            "duration_ms": int(duration.total_seconds() * 1000),
        }
    )

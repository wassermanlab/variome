from ..models import (
    Variant,
    SNV,
    GenomicGnomadFrequency,
    GenomicVariomeFrequency,
    VariantAnnotation,
)
from datetime import datetime
import logging
from threading import Lock

import hail as hl
from hail.utils.java import FatalError
from gnomad_toolbox.filtering.variant import get_single_variant

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

logger = logging.getLogger(__name__)
hail_initialization_lock = Lock()


class GnomadToolboxError(Exception):
    """Raised when gnomAD Toolbox cannot provide variant frequencies."""


def get_gnomad_toolbox_frequencies(variant_id):
    """Return v4.1 joint gnomAD frequencies, initializing Hail once per process.

    Raises:
        GnomadToolboxError: If Hail or the gnomAD Toolbox cannot provide data.
    """
    try:
        with hail_initialization_lock:
            try:
                hl.current_backend()
            except RuntimeError:
                hl.init(quiet=True)

        rows = get_single_variant(
            variant=variant_id,
            data_type="joint",
            version="4.1",
        ).take(1)
    except (FatalError, OSError, RuntimeError, ValueError) as error:
        raise GnomadToolboxError("Unable to retrieve gnomAD data") from error

    if not rows:
        raise GnomadToolboxError("Variant not found in gnomAD")

    frequency = rows[0]["freq"][0]
    fields = {
        "af_tot": "AF",
        "ac_tot": "AC",
        "an_tot": "AN",
        "hom_tot": "homozygote_count",
        "hemi_tot": "hemizygote_count",
    }
    missing_fields = [field for field in fields.values() if field not in frequency]
    if missing_fields:
        raise GnomadToolboxError(
            f"gnomAD frequency fields missing: {missing_fields}"
        )

    frequencies = {key: frequency[field] for key, field in fields.items()}
    if frequencies["af_tot"] is not None:
        frequencies["af_tot"] = f"{frequencies['af_tot']:.10f}"
    return frequencies


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@access_count_gate()
@never_cache
def gnomad_frequencies(request):
    variant_id = request.query_params.get("variant")
    if not variant_id:
        return Response({"errors": ["Variant parameter is required"]}, status=400)

    errors = []
    try:
        variant = Variant.objects.get(variant_id=variant_id)
    except Variant.DoesNotExist:
        return Response({"errors": ["Variant not found"]}, status=404)

    try:
        frequencies = {
            "id": variant.id,
            "variant": VariantSerializer(variant).data,
            **get_gnomad_toolbox_frequencies(variant_id),
        }
    except GnomadToolboxError:
        logger.exception("Unable to retrieve gnomAD frequencies from the toolbox")
        try:
            frequency = GenomicGnomadFrequency.objects.get(variant_id=variant.id)
            frequencies = GenomicGnomadFrequencySerializer(frequency).data
            errors.append(
                "gnomAD toolbox unavailable; using locally stored gnomAD frequencies"
            )
        except GenomicGnomadFrequency.DoesNotExist:
            errors.append("genomic gnomad frequency not found for this variant")
            frequencies = None

    return Response({"gnomadFrequencies": frequencies, "errors": errors})


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
            "bvlFrequencies": bvlFrequencies,
            "annotations": annotations,
            "errors": errors,
            "duration_ms": int(duration.total_seconds() * 1000),
        }
    )


from ..models import (
    Variant,
    SNV,
    GenomicGnomadFrequency,
    GenomicVariomeFrequency,
    VariantAnnotation,
)

from ..serializers import (
    VariantSerializer,
    GenomicGnomadFrequencySerializer,
    GenomicVariomeFrequencySerializer,
    VariantAnnotationSerializer,
    SNVSerializer
)

from .snv_annotations import snv_annotations

from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required

from django.http import Http404
from django.http.response import JsonResponse
    

@api_view(['GET'])
@login_required
def variant(request, id ):
    """_summary_

    Args:
        request (_type_): the request, might not be needed
        id (_type_): the variant id (db id / primary key)
        
    Returns:
        _type_: the variant object. Depending on the var_type, could
        have different fields
    """
    
    errors =[]
    
    try:
        variant = Variant.objects.get(id=id)
    except Variant.DoesNotExist:
        raise Http404
    
    print(f"variant_type: {variant.var_type}")
    
    snv = None
    gnomadFrequences = None
    variomeFrequencies = None
    annotations = None
    
    if variant.var_type == 'SNV':
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
            
        except Exception as e:
            errors.append(f"Error getting annotations: {e}")
    
    try:
        gnomadFrequenciesObject = GenomicGnomadFrequency.objects.get(variant_id=variant.id)
        gnomadFrequences = GenomicGnomadFrequencySerializer(gnomadFrequenciesObject).data
    except GenomicGnomadFrequency.DoesNotExist:
        errors.append("genomic gnomad frequency not found for this variant")
    
    try:
        variomeFrequenciesObject = GenomicVariomeFrequency.objects.get(variant_id=variant.id)
        variomeFrequencies = GenomicVariomeFrequencySerializer(variomeFrequenciesObject).data
    except GenomicVariomeFrequency.DoesNotExist:
        errors.append("genomic variome frequency not found for this variant")
    
    return JsonResponse({
        "variant": VariantSerializer(variant).data,
        "snv": snv,
        "gnomadFrequencies":gnomadFrequences,
        "ibvlFrequencies":variomeFrequencies,
        "annotations":annotations,
        "errors": errors
    })
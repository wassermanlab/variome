import json
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.http import Http404
from django.http.response import JsonResponse
from django.db.models import Q, F
from django.db.models.functions import Abs

from ..models import (
    Variant,
    SNV,
)
from ..serializers import (
    VariantSerializer,
)

@api_view(['GET'])
def snv_search(request):
    in_result_sets = request.GET.get('resultSets', None)
    in_query = request.GET.get('query', None)
    in_chr = request.GET.get('chr', None)
    in_pos = request.GET.get('pos', None)
    in_ref = request.GET.get('ref', None)
    in_alt = request.GET.get('alt', None)

    print(f"Parameters received: result_sets={in_result_sets}, query={in_query}, chr={in_chr}, pos={in_pos}, ref={in_ref}, alt={in_alt}")

    v_pos_limit = 10
    out_error = None

    # Validate input
    if 'position' not in in_result_sets and 'dbsnp' not in in_result_sets and 'clinvar' not in in_result_sets:
        out_error = f'Invalid result set: {in_result_sets}'
    elif not in_query:
        out_error = 'Query is null'
    elif 'position' in in_result_sets:
        if not in_chr:
            out_error = 'Chromosome is null'
        elif in_chr.upper() not in ['M', 'X', 'Y'] and not (1 <= int(in_chr) <= 22):
            out_error = f'Invalid chromosome: {in_chr}'
        elif not in_pos:
            out_error = 'Position is null'
        elif int(in_pos) < 0:
            out_error = f'Invalid position: {in_pos}'
        try:
            in_pos = int(in_pos)
        except ValueError:
            out_error = f'Invalid position (must be numeric): {in_pos}'

    if out_error:
        print(f"Error: {out_error}")
        return Response({'errors': [out_error]}, status=400)

    in_chr = in_chr.upper()
    in_ref = in_ref.upper() if in_ref else None
    in_alt = in_alt.upper() if in_alt else None

    response_data = {
        'term': in_query,
        'results': {}
    }
    
    snv_values_to_set = ['snv__pos', 'snv__chr','snv__ref', 'snv__alt']

    if 'position' in in_result_sets:
        v_pos_upper = in_pos + 499
        v_pos_lower = in_pos - 499
        
        position_filter = {
            'snv__chr': in_chr,
            'snv__pos': in_pos,
        }
        if in_ref:
            position_filter['snv__ref'] = in_ref
        if in_alt:
            position_filter['snv__alt'] = in_alt

        position_results = Variant.objects.filter(
            **position_filter
        ).values('variant_id', 'var_type', 'id', *snv_values_to_set)[:v_pos_limit]

        nearby_results = Variant.objects.filter(
            snv__chr=in_chr,
            snv__pos__range=(v_pos_lower, v_pos_upper)
        ).exclude(
            snv__pos=in_pos
        ).annotate(
            bp_distance=Abs(F('snv__pos') - in_pos)
        ).order_by('bp_distance').values(
            'variant_id', 'var_type', 'id', *snv_values_to_set,'bp_distance'
        )[:v_pos_limit]

        response_data['results']['position'] = list(position_results)
        response_data['results']['nearby'] = list(nearby_results)
        
        print(json.dumps(response_data['results'], indent=2))

    if 'dbsnp' in in_result_sets:
        print("Processing dbsnp result set")
        dbsnp_results = Variant.objects.filter(
            Q(snv__dbsnp_id=in_query)
        ).values( 'variant_id',  'var_type', 'id', *snv_values_to_set, 'snv__dbsnp_id')
        
        response_data['results']['dbsnp'] = list(dbsnp_results)
        print(f"dbSNP results: {response_data['results']['dbsnp']}")

    if 'clinvar' in in_result_sets:
        print("Processing clinvar result set")
        clinvar_results = Variant.objects.filter(
            Q(snv__clinvar_vcv=in_query)
        ).values('variant_id','var_type', 'id', *snv_values_to_set, 'snv__clinvar_vcv')
            
        response_data['results']['clinvar'] = list(clinvar_results)
        print(f"ClinVar results: {response_data['results']['clinvar']}")

    return Response(response_data)



@api_view(['GET'])
@login_required
def snv_search_old(request, **kwargs):
    """
    """
    json_content = kwargs.get('JSON', False)
    query_params = request.query_params
    if 'query' in query_params:
        variant_id = query_params['query']
    else:
        return Response({"errors":["missing variant_id parameter"]})
#    variant_id = json.loads(request.body)["variant_id"]

    try:
        # Get all relevant information from the database 
        #variant = Variant.objects.get(variant_id=variant_id)
        variants = Variant.objects.filter(variant_id__startswith=variant_id).values('variant_id','id')
    except Variant.DoesNotExist:
        variants = None

    if request.method == 'GET':
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
        

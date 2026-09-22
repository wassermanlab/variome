import json

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.cache import never_cache

from django.db.models import Q, F
from django.db.models.functions import Abs

from datetime import datetime

from variome_backend.settings import IS_DEVELOPMENT

from ..models import Variant


v_pos_limit = 10
snv_values_to_set = ["snv__pos", "snv__chr", "snv__ref", "snv__alt"]

def standard_search(in_chr, in_pos, in_ref = None, in_alt = None):
    
    in_pos = int(in_pos)
    v_pos_upper = in_pos + 499
    v_pos_lower = in_pos - 499

    position_filter_ref_alt = {
        "snv__chr": in_chr,
        "snv__pos": in_pos,
    }

    if in_ref:
        position_filter_ref_alt["snv__ref"] = in_ref
    if in_alt:
        position_filter_ref_alt["snv__alt"] = in_alt

    position_results = list(Variant.objects.filter(**position_filter_ref_alt).values(
        "variant_id", "var_type", "id", *snv_values_to_set
    )[:v_pos_limit])

    n_ref_alt_matches = len(position_results)

    print(position_results)
    ids_to_exclude = [v["variant_id"] for v in position_results]
    print("exclude:")
    print(ids_to_exclude)

    id_not_in_clause = ~Q(variant_id__in=ids_to_exclude)

    additional_position_results = list(
      Variant.objects.filter(
        snv__chr = in_chr,
        snv__pos = in_pos,
    ).filter(id_not_in_clause).values(
        "variant_id", "var_type", "id", *snv_values_to_set
    )[:v_pos_limit - n_ref_alt_matches])

    print("additional position")
    print(additional_position_results)

    if len(additional_position_results) > 0:
        position_results.extend(additional_position_results)


    print(position_results)

    nearby_results = (
        Variant.objects.filter(
            snv__chr=in_chr, snv__pos__range=(v_pos_lower, v_pos_upper)
        )
        .exclude(snv__pos=in_pos)
        .annotate(bp_distance=Abs(F("snv__pos") - in_pos))
        .order_by("bp_distance")
        .values("variant_id", "var_type", "id", *snv_values_to_set, "bp_distance")[
            :v_pos_limit
        ]
    )

    nearby_results = list(nearby_results)

    print(nearby_results)
    print("pos")
    print(position_results)
    return (position_results, nearby_results)


def standard_validate(chr, pos, ref = None, alt = None):
    out_error = None

    try:
        chr_int_cast = int(chr)
    except:
        chr_int_cast = None

    try:
        pos_int_cast = int(pos)
    except ValueError:
        pos_int_cast = None
        return f"Invalid position (must be numeric): {pos}"
    except:
        return f"Invalid position (must be numeric)"


    if not chr:
        out_error = "Chromosome is null"
    elif chr.upper() not in ["M", "X", "Y"] and ( chr_int_cast is None or chr_int_cast < 1 or chr_int_cast > 22):
        out_error = f"Invalid chromosome: {str(chr)}"
    elif not pos:
        out_error = "Position is null"
    elif int(pos_int_cast) < 0:
        out_error = f"Invalid position: {pos}"

    return out_error


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@never_cache
def snv_search(request):
    now = datetime.now()
    in_result_sets = request.GET.get("resultSets", None)
    in_query = request.GET.get("query", None)
    in_chr = request.GET.get("chr", None)
    in_pos = request.GET.get("pos", None)
    in_ref = request.GET.get("ref", None)
    in_alt = request.GET.get("alt", None)

    #    print(
    #        f"Parameters received: result_sets={in_result_sets}, query={in_query}, chr={in_chr}, pos={in_pos}, ref={in_ref}, alt={in_alt}"
    #    )

    out_error = None

    # Validate input
    if (
        "position" not in in_result_sets
        and "dbsnp" not in in_result_sets
        and "clinvar" not in in_result_sets
    ):
        out_error = f"Invalid result set: {in_result_sets}"
    elif not in_query:
        out_error = "Query is null"
    elif "position" in in_result_sets:
        out_error = standard_validate(in_chr, in_pos, in_ref, in_alt)
    if out_error:
        print(f"Error: {out_error}")
        if IS_DEVELOPMENT:
            return Response(
                {"errors": [out_error]}, status=int(request.GET.get("r", 400))
            )
        else:
            return Response({"errors": [out_error]}, status=400)

    in_chr = in_chr.upper() if in_chr else None
    in_ref = in_ref.upper() if in_ref else None
    in_alt = in_alt.upper() if in_alt else None

    response_data = {"term": in_query, "results": {}}


    if "position" in in_result_sets:
        (position, nearby) = standard_search(in_chr, in_pos, in_ref, in_alt)
        response_data["results"]["position"] = position
        response_data["results"]["nearby"] = nearby

    #        print(json.dumps(response_data["results"], indent=2))

    if "dbsnp" in in_result_sets:
        #        print("Processing dbsnp result set")
        dbsnp_results = Variant.objects.filter(Q(snv__dbsnp_id=in_query)).values(
            "variant_id", "var_type", "id", *snv_values_to_set, "snv__dbsnp_id"
        )

        response_data["results"]["dbsnp"] = list(dbsnp_results)
    #        print(f"dbSNP results: {response_data['results']['dbsnp']}")

    if "clinvar" in in_result_sets:
        #        print("Processing clinvar result set")
        clinvar_results = Variant.objects.filter(Q(snv__clinvar_vcv=in_query)).values(
            "variant_id", "var_type", "id", *snv_values_to_set, "snv__clinvar_vcv"
        )

        response_data["results"]["clinvar"] = list(clinvar_results)
    #        print(f"ClinVar results: {response_data['results']['clinvar']}")

    duration = datetime.now() - now
    response_data["duration_ms"] = int(duration.total_seconds() * 1000)
    if IS_DEVELOPMENT:
        return Response(response_data, status=int(request.GET.get("r", 200)))
    else:
        return Response(response_data)

from django import forms
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import SearchQueryAction
from ..serializers import InvalidSearchQuerySerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@never_cache
def invalid_search_query(request):
    serializer = InvalidSearchQuerySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    SearchQueryAction.objects.create(
        query=serializer.validated_data["query"],
        reference_genome=serializer.validated_data["selectedAssembly"],
        is_valid=False,
    )
    return Response({"tracked": True}, status=201)


class SearchQueryFilterForm(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)
    is_valid = forms.ChoiceField(
        required=False, choices=[("", "All"), ("true", "Valid"), ("false", "Invalid")]
    )
    chromosome = forms.ChoiceField(
        required=False,
        choices=[("", "All")]
        + [(str(chromosome), str(chromosome)) for chromosome in range(1, 23)]
        + [("X", "X"), ("Y", "Y"), ("M", "M")],
    )
    query = forms.CharField(required=False, strip=False)
    min_results = forms.IntegerField(required=False, min_value=0)
    max_results = forms.IntegerField(required=False, min_value=0)
    page = forms.IntegerField(required=False, min_value=1)
    page_size = forms.IntegerField(required=False, min_value=1, max_value=200)
    sort = forms.ChoiceField(
        required=False, choices=[("newest", "Newest first"), ("oldest", "Oldest first")]
    )

    def clean(self):
        data = super().clean()
        if data.get("start") and data.get("end") and data["start"] > data["end"]:
            raise forms.ValidationError("Start date must not be after end date.")
        if (
            data.get("min_results") is not None
            and data.get("max_results") is not None
            and data["min_results"] > data["max_results"]
        ):
            raise forms.ValidationError("Minimum results must not exceed maximum results.")
        return data


@permission_required("library_access.view_tracking_dashboard", raise_exception=True)
@require_GET
@never_cache
def search_query_actions(request):
    form = SearchQueryFilterForm(request.GET)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    filters = form.cleaned_data
    actions = SearchQueryAction.objects.all()
    if filters["start"]:
        actions = actions.filter(created_at__date__gte=filters["start"])
    if filters["end"]:
        actions = actions.filter(created_at__date__lte=filters["end"])
    if filters["is_valid"]:
        actions = actions.filter(is_valid=filters["is_valid"] == "true")
    if filters["chromosome"]:
        actions = actions.filter(chromosome=filters["chromosome"])
    if filters["query"]:
        actions = actions.filter(query__icontains=filters["query"])
    if filters["min_results"] is not None:
        actions = actions.filter(result_count__gte=filters["min_results"])
    if filters["max_results"] is not None:
        actions = actions.filter(result_count__lte=filters["max_results"])
    ordering = (
        ("created_at", "id") if filters["sort"] == "oldest" else ("-created_at", "-id")
    )
    actions = actions.order_by(*ordering)
    paginator = Paginator(actions, filters["page_size"] or 50)
    page_number = filters["page"] or 1
    if page_number > paginator.num_pages:
        return JsonResponse({"errors": {"page": ["Page does not exist."]}}, status=400)
    page = paginator.page(page_number)
    return JsonResponse(
        {
            "results": list(
                page.object_list.values(
                    "query",
                    "created_at",
                    "reference_genome",
                    "result_count",
                    "is_valid",
                    "chromosome",
                    "position",
                )
            ),
            "count": paginator.count,
            "page": page.number,
            "pages": paginator.num_pages,
            "page_size": paginator.per_page,
        }
    )

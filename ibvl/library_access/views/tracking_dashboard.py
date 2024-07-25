import logging
from datetime import timedelta
from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now
from django.conf import settings
from tracking.models import Visitor, Pageview
from tracking.settings import TRACK_PAGEVIEWS
from ibvl.library.models import Variant
from ibvl.library_access.models import LibraryUser
import json

log = logging.getLogger(__file__)

# tracking wants to accept more formats than default, here they are
input_formats = [
    '%Y-%m-%d',  # '2006-10-25'
]


class DashboardForm(forms.Form):
    start = forms.DateTimeField(required=True, input_formats=input_formats, widget=forms.DateTimeInput(attrs={'type': 'date'}))
    end = forms.DateTimeField(required=True, input_formats=input_formats, widget=forms.DateTimeInput(attrs={'type': 'date'}))
    variant = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'text'}))
    user = forms.ModelMultipleChoiceField(queryset=LibraryUser.objects.all(), required=False)

@permission_required('library_access.view_tracking_dashboard')
def tracking_dashboard(request):
    "Counts, aggregations and more!"
    end_time = now()
    start_time = end_time - timedelta(days=7)
    defaults = {
        'start': start_time.strftime('%Y-%m-%d'), 
        'end': end_time.strftime('%Y-%m-%d'), 
        'user': None,
        'variant': ''
        }

    form = DashboardForm(data=request.GET or defaults)
    if form.is_valid():
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']
        
        # add one day to end_time
        end_time += timedelta(days=1)

    selected_users = form.cleaned_data['user'] if form.cleaned_data['user'] else LibraryUser.objects.all()
    
    target_variant_id = form.cleaned_data['variant']
    variant_filter = {'url__contains': f'api/variant/{target_variant_id}'} if target_variant_id else {'url__contains': 'api/variant'}
    
    variant_pageviews = Pageview.objects.filter(
        view_time__range=(start_time, end_time), 
        **variant_filter,
        visitor__user__in=selected_users).order_by('-view_time')
    
    for pageview in variant_pageviews:
        id = pageview.url.split('/')[-1]
        pageview.variant = Variant.objects.get(id=id).variant_id
        pageview.variant_url = f"{settings.SITE_URL}/variant/{id}"

    user_stats = Visitor.objects.user_stats(start_time, end_time)
    for u in user_stats:
        print("this is a user:", u)
        print("the type is", type(u))
        print("this is the user's email", u.email)
    user_stats = [u for u in user_stats if u in selected_users]

    enriched_user_stats = []
    for user_stat in user_stats:
        user = user_stat
        UserHitsInTimeFrame = Pageview.objects.filter(visitor__user=user, view_time__gte=start_time)
        page_views = UserHitsInTimeFrame.count()
        time_on_site = user_stat.time_on_site
        page_views_unique = UserHitsInTimeFrame.values('url').distinct().count()

        enriched_user_stats.append({
            'user': user,
            'page_views': page_views,
            'time_on_site': time_on_site,
            'page_views_unique': page_views_unique
        })

    variant_access_details = []
    variants = Pageview.objects.filter(**variant_filter).values('url').distinct()
    for variant in variants:
        variant_name = variant['url'].split('/')[-1]
        user_list = Pageview.objects.filter(url=variant['url']).values('visitor__user__first_name', 'visitor__user__last_name', 'visitor__user__email').order_by('visitor__user__email').distinct('visitor__user__email')
        #print("user_list", user_list)
        user_count = user_list.count()
        users = [{'get_full_name': f"{u['visitor__user__first_name']} {u['visitor__user__last_name']}", 'email': u['visitor__user__email']} for u in user_list]

        variant_access_details.append({
            'name': variant_name,
            'user_count': user_count,
            'users': users
        })

    # Prepare data for charts
    user_labels = json.dumps([stat['user'].get_full_name() for stat in enriched_user_stats])
    
    timedeltas = [stat['time_on_site'].total_seconds() for stat in enriched_user_stats]
    print("timedeltas", timedeltas)
    time_on_site_data = json.dumps(timedeltas)
    variants_queried_data = json.dumps([stat['page_views_unique'] for stat in enriched_user_stats])

    context = {
        'form': form,
        'variant_pageviews': variant_pageviews,
        'warning': None,
        'user_stats': enriched_user_stats,
        'variant_access_details': variant_access_details,
        'user_labels': user_labels,
        'time_on_site_data': time_on_site_data,
        'variants_queried_data': variants_queried_data,
        
    }

    return render(request, 'tracking/dashboard.html', context)

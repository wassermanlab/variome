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

log = logging.getLogger(__file__)

# tracking wants to accept more formats than default, here they are
input_formats = [
#    '%Y-%m-%d %H:%M:%S',    # '2006-10-25 14:30:59'
#    '%Y-%m-%d %H:%M',       # '2006-10-25 14:30'
    '%Y-%m-%d',             # '2006-10-25'
#    '%Y-%m',                # '2006-10'
#    '%Y',                   # '2006'
]


class DashboardForm(forms.Form):
    start = forms.DateTimeField(required=True, input_formats=input_formats, widget=forms.DateTimeInput(attrs={'type': 'date'}))
    end = forms.DateTimeField(required=True, input_formats=input_formats, widget=forms.DateTimeInput(attrs={'type': 'date'}))
    user = forms.ModelMultipleChoiceField(queryset=LibraryUser.objects.all(), required=False)


@permission_required('library_access.view_tracking_dashboard')
def tracking_dashboard(request):
    "Counts, aggregations and more!"
    end_time = now()
    start_time = end_time - timedelta(days=7)
    defaults = {'start': start_time, 'end': end_time, 'user': None  }

    form = DashboardForm(data=request.GET or defaults)
    if form.is_valid():
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']
        
        # add one day to end_time
        end_time += timedelta(days=1)

    # determine when tracking began
    try:
        obj = Visitor.objects.order_by('start_time')[0]
        track_start_time = obj.start_time
    except (IndexError, Visitor.DoesNotExist):
        track_start_time = now()

    selected_users = form.cleaned_data['user']

    # queries take `date` objects (for now)
    user_stats = Visitor.objects.user_stats(start_time, end_time)
    filtered_user_stats = []
    for u in user_stats:
#        print('u', u.id, u.profile.access_count)
#        print('selected_users', selected_users)
        if u.id in selected_users.values_list('id', flat=True):
            filtered_user_stats.append(u)
    user_stats = filtered_user_stats
    
    for u in user_stats:
        lu = LibraryUser.objects.get(id=u.id)
        print(lu)
        print(lu.profile.access_count)
    visitor_stats = Visitor.objects.stats(start_time, end_time)
    if TRACK_PAGEVIEWS:
        pageview_stats = Pageview.objects.stats(start_time, end_time)
    else:
        pageview_stats = None
        
        
    pageviews = Pageview.objects.filter(
        view_time__range=(start_time, end_time), 
        url__contains='api/variant',
        visitor__user__in=selected_users).order_by('-view_time')
    
    for pageview in pageviews:
        id = pageview.url.split('/')[-1]
        pageview.variant = Variant.objects.get(id=id).variant_id
        pageview.variant_url = f"{settings.SITE_URL}/variant/{id}"

    context = {
        'form': form,
        'pageviews': pageviews,
        'track_start_time': track_start_time,
        'warning': None,
        'user_stats': user_stats,
        'visitor_stats': visitor_stats,
        'pageview_stats': pageview_stats,
    }
    return render(request, 'tracking/dashboard.html', context)

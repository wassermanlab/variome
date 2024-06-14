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
    variant = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'text'}))
    user = forms.ModelMultipleChoiceField(queryset=LibraryUser.objects.all(), required=False)

@permission_required('library_access.view_tracking_dashboard')
def tracking_dashboard(request):
    "Counts, aggregations and more!"
    end_time = now()
    start_time = end_time - timedelta(days=7)
    defaults = {'start': start_time.strftime('%Y-%m-%d'), 'end': end_time.strftime('%Y-%m-%d'), 'user': None  }

    form = DashboardForm(data=request.GET or defaults)
    if form.is_valid():
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']
        
        # add one day to end_time
        end_time += timedelta(days=1)

    selected_users = form.cleaned_data['user']
    
    # Stephanie TODO
    # if selected_users is empty or None, don't filter the user_stats at all
    # because we want to show ALL users that accessed any variant (or one particular variant if specified)

    user_stats = Visitor.objects.user_stats(start_time, end_time)
    filtered_user_stats = []
    for u in user_stats:
        if u.id in selected_users.values_list('id', flat=True):
            filtered_user_stats.append(u)
    user_stats = filtered_user_stats
    
    # Stephanie TODO
    # use Variant model to find the variant object using target_variant_id (it is the variant_id property)
    # find the id (pk) of that object
    # IF found, then add it to the filter query for variant_pageviews 
    #    hint: (change url__contains='api/variant' to url__contains='api/variant/{id}')
    # then, Variant Views in the page should only be ones that match this variant.
    target_variant_id = form.cleaned_data['variant']
    print("find the variant with variant_id = ", target_variant_id)
    
    variant_pageviews = Pageview.objects.filter(
        view_time__range=(start_time, end_time), 
        url__contains='api/variant',
        visitor__user__in=selected_users).order_by('-view_time')
    
    for pageview in variant_pageviews:
        id = pageview.url.split('/')[-1]
        pageview.variant = Variant.objects.get(id=id).variant_id
        pageview.variant_url = f"{settings.SITE_URL}/variant/{id}"
        
    # Stephanie TODO
    # user_stats is kind of a black box from the tracking library
    # you could calculate more stats (eg, counting how many pageviews in variant_pageviews, by user and total)
    # you can add that data to a new object on this context dictionary and add it to the table under Statistics in tracking/dashboard.html
    # or add a new table below that one
    # charts:
    # I added the "getting started" chart for charts.js to the bottom of the template, so that can be a starting point
    # https://www.chartjs.org/docs/latest/getting-started/
    # you can access the data from context below or add your own, and set it up under data.datasets as in the example
    
    context = {
        'form': form,
        'variant_pageviews': variant_pageviews,
        'warning': None,
        'user_stats': user_stats,
    }
    return render(request, 'tracking/dashboard.html', context)

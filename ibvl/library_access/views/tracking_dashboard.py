import logging
from datetime import timedelta, datetime
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
    "Filterable Variant Views, User Details, Variant Details"
    end_time = now()
    start_time = end_time - timedelta(days=7)
    defaults = {
        'start': start_time.strftime('%Y-%m-%d'), 
        'end': end_time.strftime('%Y-%m-%d'), 
        'user': None,
        'variant': ''
        }
    
    def variant_from_url(url):
        id = url.split('/')[-1]
        return Variant.objects.filter(id=id).first()

    form = DashboardForm(data=request.GET or defaults)
    if form.is_valid():
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']
        
        # add one day to end_time so it goes until midnight end of day
        end_time += timedelta(days=1)

    target_variant = Variant.objects.filter(variant_id=form.cleaned_data['variant']).first()
    target_variant_id = target_variant.id if target_variant else None
    variant_filter = {'url__endswith': f'variant/{target_variant_id}'} if target_variant_id else {'url__contains': 'api/variant'}

    user_stats = Visitor.objects.user_stats(start_time, end_time)
    selected_users = form.cleaned_data['user'] if form.cleaned_data['user'] else LibraryUser.objects.all()
    user_stats = [u for u in user_stats if u in selected_users]

    user_details = []
    for user in user_stats:
        UserHitsInTimeFrame = Pageview.objects.filter(visitor__user=user, view_time__gte=start_time)
        page_views_unique = UserHitsInTimeFrame.values('url').distinct().count()

        user_details.append({
            'name': user.get_full_name(),
            'page_views_unique': page_views_unique,
            'views_24_hrs': user.profile.access_count,
            'time_on_site': user.time_on_site.seconds,
        })

    variant_access_details = []
    variant_urls = Pageview.objects.filter(**variant_filter).values('url').distinct()
    # TODO: please make this variants list unique
    # as a result, every variant_name should appear only once in the Variant Details list)
    for variant_url in variant_urls:
        
        variant = variant_from_url(variant_url['url'])
        
        if variant:
            user_list = Pageview.objects.filter(url=variant_url['url']).values('visitor__user__first_name', 'visitor__user__last_name', 'visitor__user__email').order_by('visitor__user__email').distinct('visitor__user__email')
            users = [{'get_full_name': f"{u['visitor__user__first_name']} {u['visitor__user__last_name']}", 'email': u['visitor__user__email']} for u in user_list]

            variant_access_details.append({
                'name': variant.variant_id,
                'user_count': user_list.count(),
                'users': users
            })
            
#            print("variant_name", variant_name)
#            print("user_list", user_list)
    variant_access_details.sort(key=lambda x: x['user_count'], reverse=True)

    # Prepare data for charts
    
    variant_pageviews = []
    
    for pageview in Pageview.objects.filter(
                view_time__range=(start_time, end_time), 
                **variant_filter,
                visitor__user__in=selected_users).order_by('-view_time'):
        
        variant = variant_from_url(pageview.url)
        if variant:
            pageview.variant = variant.variant_id
            pageview.variant_url = f"{settings.SITE_URL}/variant/{variant.id}"
        else:
            pageview.variant = "Unknown"
            pageview.variant_url = "Unknown"
            
        variant_pageviews.append({
            'time': pageview.view_time.isoformat(),
            'user': pageview.visitor.user.get_full_name(),
            'variant': pageview.variant,
            'variant_url': pageview.variant_url
        })
        
    # Data for the display charts (daily, weekly and monthly)
    chart_data = {}
    
    # Helper functions for creating data for chart views
    def create_daily_views(start_date, end_date, data):
        
        current_date = start_date
        views_data = {}
        
        while current_date <= end_date:
            
            counter = sum(1 for view in data if view['time'].split("T")[0] == current_date)

            views_data[current_date.strftime('%Y-%m-%d')] = counter
            
            current_date += timedelta(days=1)
        
        return views_data

    # weekly (Monday to Sunday) Assuming that weeks start with sunday
    def create_weekly_views(start_date, end_date, data):
        
        views_data = {}
                
        current_date = start_date
        
        while current_date <= end_date:
            end_week_date = current_date + timedelta(days=6)
            
            # if it doesn't equal to monday 
            if current_date.weekday() != 0: # essentially the first iteration where the week might not be complete 7 days
                starting_weekday = current_date.weekday()
                difference_to_sunday = 6 - starting_weekday
                end_week_date = current_date + timedelta(days=difference_to_sunday)
            elif current_date + timedelta(days=7) > end_date: # last iteration set up
                end_week_date = end_date
        
            
            week_range = current_date.strftime('%Y') + " " + current_date.strftime('%m-%d') + ":" + end_week_date.strftime('%m-%d')
            
            views_data[week_range] = sum(1 for view in data if current_date <= datetime.fromisoformat(view["time"]) <= end_week_date)
            
            current_date = end_week_date + timedelta(days=1)
            
        return views_data
    
    
    def create_monthly_views(start_date, end_date, data):
        
        # turn it to the first of the month        
        current_date = start_date.replace(day=1)
        views_data = {}
        
        while current_date <= end_date:
            
            year_month_date = current_date.strftime('%Y-%m')
            
            counter = sum(1 for view in data if view['time'][0:7] == year_month_date)

            views_data[year_month_date] = counter
            
            current_date += timedelta(days=32) # add 32 days to ensure moves onto next month 
            current_date = current_date.replace(day=1) # replaces it back to day 1
        
        return views_data


    # chart views data
    chart_data['daily'] = create_daily_views(start_time, end_time, variant_pageviews)
    chart_data['weekly'] = create_weekly_views(start_time, end_time, variant_pageviews)
    chart_data['monthly'] = create_monthly_views(start_time, end_time, variant_pageviews)
        

    context = {
        'form': form,
        'data':json.dumps({
            'user_details':user_details,
            'variant_pageviews': variant_pageviews,
            'chart_data': chart_data,
            'warning': None,
            'variant_access_details': variant_access_details,
            })
    }

    return render(request, 'tracking_dashboard.html', context)

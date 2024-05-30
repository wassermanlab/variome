from django.contrib.auth.models import User
from tracking.models import Visitor
from django.db import models
from django.utils import timezone
import datetime
import time

import os

#default limit for how many variants a user can access in a 24 hr period
ACCESSES_PER_DAY = os.getenv('ACCESSES_PER_DAY', 100)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    accesses_per_day = models.IntegerField(default=ACCESSES_PER_DAY)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def access_count(self):
        timestamp_now = timezone.now()
        one_day_ago = timestamp_now - timezone.timedelta(days=1)
        total_page_views = 0
        for visitor in self.user.visit_history.all():
            pageViews = visitor.pageviews.filter(url__contains='/api/variant/', view_time__gte=one_day_ago)
            total_page_views += len(pageViews)
        return total_page_views

    @property
    def can_access_variants(self):
        return self.access_count <= self.accesses_per_day
    
    class Meta:
        verbose_name_plural = 'Profiles'
        db_table = 'user_profile'
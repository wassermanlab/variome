from django.contrib.auth.models import User, Group
from tracking.models import Visitor, Pageview
from django.db import models
from django.utils import timezone
import pghistory

import os

# default limit for how many variants a user can access in a 24 hr period
ACCESSES_PER_DAY = os.getenv("ACCESSES_PER_DAY", 100)


@pghistory.track()
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    accesses_per_day = models.IntegerField(default=ACCESSES_PER_DAY)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def access_count(self):
        timestamp_now = timezone.now()
        one_day_ago = timestamp_now - timezone.timedelta(days=1)
        total_page_views = 0
        for visitor in self.user.visit_history.all():
            pageViews = visitor.pageviews.filter(
                url__contains="/api/variant/", view_time__gte=one_day_ago
            )
            total_page_views += len(pageViews)
        return total_page_views

    @property
    def can_access_variants(self):
        return self.access_count <= self.accesses_per_day

    def __str__(self):
        return f"Access for {self.user.username}"

    class Meta:
        verbose_name = "User Access Configuration"
        verbose_name_plural = "User Access Configurations"
        db_table = "user_profile"


# Proxy models so that the models appear under Library Access in the admin dashboard
@pghistory.track()
class LibraryUser(User):
    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            UserProfile.objects.create(user=self)
        else:
            super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"


@pghistory.track()
class LibraryGroup(Group):
    class Meta:
        proxy = True
        verbose_name = "User Group"
        verbose_name_plural = "User Groups"


class LibraryPageview(Pageview):
    class Meta:
        proxy = True
        verbose_name = "Pageview"
        verbose_name_plural = "Pageviews"
        permissions = [
            ("view_tracking_dashboard", "Can view tracking dashboard"),
        ]
        default_permissions = ()


class LibrarySession(Visitor):
    class Meta:
        proxy = True
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        default_permissions = ()

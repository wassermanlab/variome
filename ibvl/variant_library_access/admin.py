
from .models import UserProfile

from django.contrib import admin

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'accesses_per_day', 'created_at')
    list_display_links = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user',)
    ordering = ('created_at',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('user', 'accesses_per_day')}),
    )   

admin.site.register(UserProfile, UserProfileAdmin)
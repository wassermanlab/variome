
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.http import HttpRequest
from .models import UserProfile, LibraryUser
from tracking.models import Visitor, Pageview
from tracking.admin import VisitorAdmin, PageviewAdmin

admin.site.unregister(User) 
# groups are likely not needed, remove to simplify admin dashboard
admin.site.unregister(Group)
admin.site.unregister(Visitor)
admin.site.unregister(Pageview)


@admin.register(UserProfile)
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
    def has_add_permission(self, request):
        return False

@admin.register(LibraryUser)
class LibraryUserAdmin(UserAdmin):
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    
@admin.register(Visitor)
class VisitorAdmin(VisitorAdmin):
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Pageview)
class PageviewAdmin(PageviewAdmin):
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
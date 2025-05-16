from django.contrib.auth.admin import UserAdmin, GroupAdmin
from tracking.admin import VisitorAdmin, PageviewAdmin
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q
from .models import (
    UserProfile,
    LibraryUser,
    LibraryGroup,
    LibraryPageview,
    LibrarySession,
)
from django.contrib import admin
from django.http import HttpRequest
from tracking.models import Visitor, Pageview

from django.conf import settings


# UserProfile model is a one-to-one extension of the User model
# verbose name is "Library Access Configuration"
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "accesses_per_day", "created_at")
    list_display_links = ("user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email")
    ordering = ("created_at",)
    filter_horizontal = ()
    fieldsets = ((None, {"fields": ("user", "accesses_per_day")}),)

    #prevents changing the associated user on the UserProfile object
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ("user",)
        return self.readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# models from parent app "variome_backend" or dependency apps like tracking2
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Visitor)
admin.site.unregister(Pageview)

# move them under library_access for organization, using proxy models

@admin.register(LibraryUser)
class LibraryUserAdmin(UserAdmin):
    
    readonly_fields = [
        'date_joined',
        'last_login',
        'username',
        'email',
        'password',
        'first_name',
        'last_name',
        'user_permissions', #enforces using groups only to manage perms
    ]
    if (settings.IS_DEVELOPMENT):
        
        readonly_fields = [
            'date_joined',
            'last_login',
            'user_permissions', 
        ]
            
    def has_add_permission(self, request):
        if (settings.IS_DEVELOPMENT):
            return True
        else :
            return False
    
    def get_form(self, request, obj=None, **kwargs):
        is_superuser = request.user.is_superuser
        form = super().get_form(request, obj, **kwargs)
        disabled_fields = set()
            
        # Prevent non-superusers from elevating to superuser
        if not is_superuser:
            disabled_fields |= {
                'is_superuser'
            }

        # Prevent non-superusers and non-staff from editing their own permissions (in case of intrusion)
        if (
            not is_superuser
            and obj == request.user
        ):
            disabled_fields |= {
                'is_staff',
                'groups',
            }            

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
                
        return form
    pass

@admin.register(LibraryGroup)
class LibraryGroupAdmin(GroupAdmin):
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['permissions'].queryset = Permission.objects.exclude(
            Q(content_type__app_label__in=['auth','admin', 'contenttypes', 'sessions', 'tracking']) |
            Q(content_type__app_label='library_access', content_type__model__in=['librarygroupevent', 'libraryuserevent','userprofileevent', 'librarysession']) |
            Q(content_type__app_label='pghistory', content_type__model__in=['context', 'middlewareevents'])
        )
        return form

@admin.register(LibrarySession)
class LibrarySessionAdmin(VisitorAdmin):
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(LibraryPageview)
class LibraryPageviewAdmin(PageviewAdmin):
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

from django.contrib import admin
from ..models.variome_settings import VariomeSettings

class VariomeSettingsAdmin(admin.ModelAdmin):
    """Admin definition for VariomeSettings."""
    def has_add_permission(self, request):
        return not VariomeSettings.objects.exists()
    
    def has_delete_permission(self, request,obj=None):
        return False
    
    autocomplete_fields = ['example_snv']
    
admin.site.register(VariomeSettings, VariomeSettingsAdmin)
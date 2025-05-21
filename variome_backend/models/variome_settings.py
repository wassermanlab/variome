from django.db import models
from variome_backend.library.models.variant import Variant


class VariomeSettings(models.Model):
    """Singleton container for user-editable (Admin) settings and config."""

    #    site_title = models.CharField(max_length=255)
    home_page_message = models.TextField(blank=True, default="")
    example_snv = models.ForeignKey(
        Variant, on_delete=models.SET_NULL, null=True, blank=True
    )
    #    example_mt = models.ForeignKey('library.snv', on_delete=models.CASCADE, blank=True, null=True)
    #    example_sv = models.ForeignKey('library.snv', on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(VariomeSettings, self).save(*args, **kwargs)

    class Meta:
        """Meta definition for VariomeSettings."""

        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def __str__(self):
        return """⚙️ Settings Editor ⚙️"""

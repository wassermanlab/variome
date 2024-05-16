from django.db import models


class Severity(models.Model):
    severity_number = models.IntegerField(unique=True)
    consequence = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "severities"
        verbose_name_plural = 'Severities'

    def __str__(self):
        return self.consequence
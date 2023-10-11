from django.db import models


class Gene(models.Model):
    short_name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = "gene"

    def __str__(self):
        return self.short_name
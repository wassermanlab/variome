from django.urls import path

from . import views

urlpatterns = [
    path('snv/<str:variant_id>', views.snv_metadata, name='snv_metadata'),
    path('annotations/<str:variant_id>', views.snv_annotations, name='snv_annotations'),
    path('genomic_population_frequencies/<str:variant_id>', views.genomic_population_frequencies, name='genomic_population_frequencies'),
    path('search', views.snv_search, name='search'),
]
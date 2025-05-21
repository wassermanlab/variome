from django.contrib import admin
from django.contrib.auth.models import User, Group

admin.site.site_header = "BVL Dashboard"

from .gene import GeneAdmin
from .severity import SeverityAdmin
from .transcript import TranscriptAdmin
from .variant_transcript import VariantTranscriptAdmin
from .variant_annotation import VariantAnnotationAdmin
from .variant_consequence import VariantConsequenceAdmin
from .genomic_gnomad_frequency import GenomicGnomadFrequencyAdmin
from .genomic_variome_frequency import GenomicVariomeFrequencyAdmin

from .variant import VariantAdmin
from .snv import SNVAdmin

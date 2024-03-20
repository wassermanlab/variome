import os
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps
import os
import datetime
from django.core.management import call_command
import data.import_script.orchestrate as import_orchestrate
from interface.models import Gene, GenomicGnomadFrequency, GenomicIBVLFrequency, Severity, SNV, Transcript, VariantAnnotation, VariantConsequence, VariantTranscript, Variant

class Command(BaseCommand):
    help = 'deletes everything, then imports background variant data as per .env config'
    
    

    def handle(self, *args, **options):
        
        Gene.objects.all().delete()
        GenomicGnomadFrequency.objects.all().delete()
        GenomicIBVLFrequency.objects.all().delete()
        Severity.objects.all().delete()
        SNV.objects.all().delete()
        Transcript.objects.all().delete()
        VariantAnnotation.objects.all().delete()
        VariantConsequence.objects.all().delete()
        VariantTranscript.objects.all().delete()
        Variant.objects.all().delete()
        
        import_orchestrate.setup_and_run()
        print("done ")
        

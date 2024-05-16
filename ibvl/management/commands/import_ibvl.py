import os
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps
import os
import datetime
from django.db import connection
from django.core.management import call_command
import data.import_script.orchestrate as import_orchestrate
from ibvl.models import Gene, GenomicGnomadFrequency, GenomicVariomeFrequency, Severity, SNV, Transcript, VariantAnnotation, VariantConsequence, VariantTranscript, Variant

class Command(BaseCommand):
    help = 'deletes everything, then imports background variant data as per .env config'
    
        

    def handle(self, *args, **options):
            
        def truncate_table(model):
            print("truncating table: ", model._meta.db_table)
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE {} CASCADE'.format(model._meta.db_table))
                
        truncate_table(Gene)
        truncate_table(GenomicGnomadFrequency)
        truncate_table(GenomicVariomeFrequency)
        truncate_table(Severity)
        truncate_table(SNV)
        truncate_table(Transcript)
        truncate_table(VariantAnnotation)
        truncate_table(VariantConsequence)
        truncate_table(VariantTranscript)
        truncate_table(Variant)
        
        print("tables are empty. Now will import new data...")
        import_orchestrate.setup_and_run()
        print("done ")
        

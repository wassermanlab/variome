import os
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps
import os
import datetime
import data.import_script.orchestrate as import_orchestrate

class Command(BaseCommand):
    help = 'import background variant data as per .env config'

    def handle(self, *args, **options):
        import_orchestrate.setup_and_run()
        print("done ")


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    
    dependencies: [
        ('ibvl','0003_alter_genomicgnomadfrequency_options_and_more')
    ]
    
    replaces = [
        ('ibvl', '0001_initial'),
        ('ibvl', '0002_genomicgnomadfrequency_af_popmax_variant_filter'),
        ('ibvl', '0003_alter_genomicgnomadfrequency_options_and_more')
    ]
    
    operations = []
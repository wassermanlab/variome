import os
from django.core.management.base import BaseCommand
from django.db import connection
from io import StringIO
import pandas as pd

import data.import_script.orchestrate as import_orchestrate
from ibvl.library.models import (
    Gene,
    GenomicGnomadFrequency,
    GenomicVariomeFrequency,
    Severity,
    SNV,
    Transcript,
    VariantAnnotation,
    VariantConsequence,
    VariantTranscript,
    Variant,
)


class Command(BaseCommand):
    help = "deletes the variant library tables, then imports from tsv files as per .env config"

    def handle(self, *args, **options):

        def truncate_table(model):
            print("truncating table: ", model._meta.db_table)
            with connection.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE {} CASCADE".format(model._meta.db_table))

        start_at_model = os.getenv("START_AT_MODEL")

        if isinstance(start_at_model, str) and start_at_model != "":
            print(
                f"starting at model {start_at_model}. likely resuming a failed migration so do not delete tables first"
            )
        else:
            truncate_table(Gene)
            truncate_table(GenomicGnomadFrequency)
            truncate_table(GenomicVariomeFrequency)
            truncate_table(SNV)
            truncate_table(Transcript)
            truncate_table(VariantAnnotation)
            truncate_table(VariantConsequence)
            truncate_table(VariantTranscript)
            truncate_table(Variant)
            print("tables are empty. Now will import new data...")

        truncate_table(Severity)
        severities_csv = """1,1,transcript_ablation
                            2,2,splice_acceptor_variant
                            3,3,splice_donor_variant
                            4,4,stop_gained
                            5,5,frameshift_variant
                            6,6,stop_lost
                            7,7,start_lost
                            8,8,transcript_amplification
                            9,9,inframe_insertion
                            10,10,inframe_deletion
                            11,11,missense_variant
                            12,12,protein_altering_variant
                            13,13,regulatory_region_ablation
                            14,14,splice_region_variant
                            15,15,incomplete_terminal_codon_variant
                            16,16,start_retained_variant
                            17,17,stop_retained_variant
                            18,18,synonymous_variant
                            19,19,coding_sequence_variant
                            20,20,mature_miRNA_variant
                            21,21,5_prime_UTR_variant
                            22,22,3_prime_UTR_variant
                            23,23,non_coding_transcript_exon_variant
                            24,24,intron_variant
                            25,25,NMD_transcript_variant
                            26,26,non_coding_transcript_variant
                            27,27,upstream_gene_variant
                            28,28,downstream_gene_variant
                            29,29,TFBS_ablation
                            30,30,TFBS_amplification
                            31,31,TF_binding_site_variant
                            32,32,regulatory_region_amplification
                            33,33,feature_elongation
                            34,34,regulatory_region_variant
                            35,35,feature_truncation
                            36,36,intergenic_variant
                            """

        severities_df = pd.read_csv(
            StringIO(severities_csv), names=["id", "severity_number", "consequence"]
        )

        for severity in severities_df.iterrows():
            Severity.objects.create(
                id=severity[1]["id"],
                severity_number=severity[1]["severity_number"],
                consequence=severity[1]["consequence"],
            )
        print("re-imported severities")

        import_orchestrate.setup_and_run()
        print("done ")

from django.db import models
from .gene import Gene

# TODO: Add transcript choices here
TRANSCRIPT_CHOICES = [('E', 'Ensembl'),('R','Refseq')]
BIOTYPE_CHOICES = [
('protein_coding','protein_coding'),
('protein_coding_CDS_not_defined','protein_coding_CDS_not_defined'),
('protein_coding_LoF','protein_coding_LoF'),
('nonsense_mediated_decay','nonsense_mediated_decay'),
('non_stop_decay','non_stop_decay'),
('retained_intron','retained_intron'),
('processed_transcript','processed_transcript'),
('processed_pseudogene','processed_pseudogene'),
('pseudogene','pseudogene'),
('transcribed_processed_pseudogene','transcribed_processed_pseudogene'),
('transcribed_unitary_pseudogene','transcribed_unitary_pseudogene'),
('transcribed_unprocessed_pseudogene','transcribed_unprocessed_pseudogene'),
('translated_processed_pseudogene','translated_processed_pseudogene'),
('TR_C_gene','TR_C_gene'),
('TR_D_gene','TR_D_gene'),
('TR_J_gene','TR_J_gene'),
('TR_J_pseudogene','TR_J_pseudogene'),
('TR_V_gene','TR_V_gene'),
('TR_V_pseudogene','TR_V_pseudogene'),
('unitary_pseudogene','unitary_pseudogene'),
('unprocessed_pseudogene','unprocessed_pseudogene'),
('IG_C_gene','IG_C_gene'),
('IG_C_pseudogene','IG_C_pseudogene'),
('IG_D_gene','IG_D_gene'),
('IG_J_gene','IG_J_gene'),
('IG_J_pseudogene','IG_J_pseudogene'),
('IG_pseudogene','IG_pseudogene'),
('IG_V_gene','IG_V_gene'),
('IG_V_pseudogene','IG_V_pseudogene'),
('lncRNA','lncRNA'),
('miRNA','miRNA'),
('misc_RNA','misc_RNA'),
('Mt_rRNA','Mt_rRNA'),
('Mt_tRNA','Mt_tRNA'),
('ribozyme','ribozyme'),
('rRNA','rRNA'),
('rRNA_pseudogene','rRNA_pseudogene'),
('scaRNA','scaRNA'),
('scRNA','scRNA'),
('snoRNA','snoRNA'),
('snRNA','snRNA'),
('sRNA','sRNA'),
('vault_RNA','vault_RNA'),
('TEC','TEC'),
('artifact','artifact'),
('','(unknown)'),
]

class Transcript(models.Model):
    transcript_id = models.CharField(max_length=100, unique=True)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, db_column='gene')
    transcript_type = models.CharField(max_length=1, choices=TRANSCRIPT_CHOICES)
    tsl = models.CharField(max_length=255, blank=True, default='')
    biotype = models.CharField(max_length=60, blank=True, default='', choices=BIOTYPE_CHOICES)

    class Meta:
        db_table = "transcripts"

    def __str__(self):
        return self.transcript_id
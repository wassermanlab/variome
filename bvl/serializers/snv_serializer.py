from rest_framework import serializers

from bvl.models import (
    SNV,
    Variant
)
from bvl.serializers import (
    VariantSerializer
)

class SNVSerializer(serializers.ModelSerializer):
    """
    """
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = SNV
        fields = [
            "id", "variant", "type", "length", "chr", "pos", "ref", "alt",
            "cadd_intr", "cadd_score", "dbsnp_id", "dbsnp_url",
            "ucsc_url", "ensembl_url", "clinvar_vcv", 
            "clinvar_url", "gnomad_url", "splice_ai"
        ]
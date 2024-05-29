import React from 'react';
import _ from 'lodash';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';


export default function References({variant, variantMetadata}) {
    const referencesList = variantMetadata ? [
        {
            ref: 'dbSNP',
            val: (variantMetadata.dbsnp_id === "nan" || typeof variantMetadata.dbsnp_id == 'undefined') ? "Search dbSNP" : variantMetadata.dbsnp_id,
            link: (variantMetadata.dbsnp_url === "nan" || typeof variantMetadata.dbsnp_url == 'undefined') ?  "https://www.ncbi.nlm.nih.gov/snp/" : variantMetadata.dbsnp_url,
        },
        {
            ref: 'UCSC',
            val: 'Search UCSC',
            link: (variantMetadata.ucsc_url === "nan" || typeof variantMetadata.ucsc_url == 'undefined') ?  "https://asia.ensembl.org/Homo_sapiens/Info/Index" : variantMetadata.ucsc_url,
        },
        {
            ref: 'Ensembl',
            val: 'Search Ensembl',
            link: (variantMetadata.ensembl_url === "nan" || typeof variantMetadata.ensembl_url == 'undefined') ?  "https://asia.ensembl.org/Homo_sapiens/Info/Index" : variantMetadata.ensemble_url,
        },
        {
            ref: 'ClinVar',
            val: (variantMetadata.clinvar_vcv === "nan" || typeof variantMetadata.clinvar_vcv == 'undefined') ? "Search ClinVar" : Math.trunc(variantMetadata.clinvar_vcv),
            link: (variantMetadata.clinvar_url === "nan" || typeof variantMetadata.clinvar_url == 'undefined') ?  "https://www.ncbi.nlm.nih.gov/clinvar/" : variantMetadata.clinvar_url,
        },
        {
            ref: 'gnomAD',
            val: (variantMetadata.gnomad_url === "nan" || typeof variantMetadata.gnomad_url == 'undefined') ? "Search gnomAD" : variantMetadata.variant.variant_id,
            link: (variantMetadata.gnomad_url === "nan" || typeof variantMetadata.gnomad_url == 'undefined') ?  "https://gnomad.broadinstitute.org/" : variantMetadata.gnomad_url,
        }
    ] : [];
    if (_.isArray(referencesList) && _.size(referencesList) > 0){

        return (
            <React.Fragment>
            <Card sx={{ height: '235px' }}>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '2%' }}>
                                References
                            </Typography>
                        </Grid>
                        {referencesList.map((item, index) => (
                            <Grid container key={index} alignItems="center">
                                <Grid item xs={3}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                        {item.ref}
                                    </Typography>
                                </Grid>
                                <Grid item xs={9}>
                                    <Typography variant="subtitle1">
                                        <Link color="primary" href={item.link} target="_blank">{item.val}</Link>
                                    </Typography>
                                </Grid>
                            </Grid>
                        ))}
                    </Grid>
                </CardContent>
            </Card>
        </React.Fragment>
    )
} else {
    return null;
}
}
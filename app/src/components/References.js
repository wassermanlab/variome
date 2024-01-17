import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';


export default function References(props) {
    const referencesList = [
        {
            ref: 'dbSNP',
            val: (props.variantMetadata.dbsnp_id === "nan" || typeof props.variantMetadata.dbsnp_id == 'undefined') ? "Search dbSNP" : props.variantMetadata.dbsnp_id,
            link: (props.variantMetadata.dbsnp_url === "nan" || typeof props.variantMetadata.dbsnp_url == 'undefined') ?  "https://www.ncbi.nlm.nih.gov/snp/" : props.variantMetadata.dbsnp_url,
        },
        {
            ref: 'UCSC',
            val: 'Search UCSC',
            link: (props.variantMetadata.ucsc_url === "nan" || typeof props.variantMetadata.ucsc_url == 'undefined') ?  "https://asia.ensembl.org/Homo_sapiens/Info/Index" : props.variantMetadata.ucsc_url,
        },
        {
            ref: 'Ensembl',
            val: 'Search Ensembl',
            link: (props.variantMetadata.ensembl_url === "nan" || typeof props.variantMetadata.ensembl_url == 'undefined') ?  "https://asia.ensembl.org/Homo_sapiens/Info/Index" : props.variantMetadata.ensemble_url,
        },
        {
            ref: 'ClinVar',
            val: (props.variantMetadata.clinvar_vcv === "nan" || typeof props.variantMetadata.clinvar_vcv == 'undefined') ? "Search ClinVar" : Math.trunc(props.variantMetadata.clinvar_vcv),
            link: (props.variantMetadata.clinvar_url === "nan" || typeof props.variantMetadata.clinvar_url == 'undefined') ?  "https://www.ncbi.nlm.nih.gov/clinvar/" : props.variantMetadata.clinvar_url,
        },
        {
            ref: 'gnomAD',
            val: (props.variantMetadata.gnomad_url === "nan" || typeof props.variantMetadata.gnomad_url == 'undefined') ? "Search gnomAD" : props.variantMetadata.variant.variant_id,
            link: (props.variantMetadata.gnomad_url === "nan" || typeof props.variantMetadata.gnomad_url == 'undefined') ?  "https://gnomad.broadinstitute.org/" : props.variantMetadata.gnomad_url,
        }
    ]

    return (
        <React.Fragment>
            <Card>
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
}
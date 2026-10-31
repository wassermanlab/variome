import React from 'react';
import _ from 'lodash';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import { OpenInNew as LinkIcon } from '@mui/icons-material';


export default function References({variant, variantMetadata}) {
    const referencesList = variantMetadata ? [
        {
            ref: 'dbSNP',
            val: _.isEmpty(variantMetadata.dbsnp_id) ? "(Search)" : variantMetadata.dbsnp_id,
            link: _.isEmpty(variantMetadata.dbsnp_url) ?  "https://www.ncbi.nlm.nih.gov/snp/" : variantMetadata.dbsnp_url,
        },
        {
            ref: 'UCSC',
            val: _.isEmpty(variantMetadata.ucsc_url) ? 'Search UCSC': <LinkIcon/>,
            link: _.isEmpty(variantMetadata.ucsc_url) ? (variant?.var_type === 'M' ? "https://genome.ucsc.edu/" : "https://asia.ensembl.org/Homo_sapiens/Info/Index") : variantMetadata.ucsc_url,
        },
        {
            ref: variant?.var_type === 'M' ? 'MITOMAP' : 'Ensembl',
            val: _.isEmpty(variant?.var_type === 'M' ? variantMetadata.mitomap_url : variantMetadata.ensembl_url) ? '(Search)' : <LinkIcon/>,
            link: variant?.var_type === 'M'
                ? (variantMetadata.mitomap_url || "https://www.mitomap.org/")
                : (variantMetadata.ensembl_url || "https://asia.ensembl.org/Homo_sapiens/Info/Index"),
        },
        {
            ref: 'ClinVar',
            val: variantMetadata.clinvar_vcv == null || variantMetadata.clinvar_vcv === "" ? "(Search)" : <><LinkIcon/> {_.round(variantMetadata.clinvar_vcv)}</>,
            link: _.isEmpty(variantMetadata.clinvar_url) ?  "https://www.ncbi.nlm.nih.gov/clinvar/" : variantMetadata.clinvar_url,
        },
        {
            ref: 'gnomAD',
            val: _.isEmpty(variantMetadata.gnomad_url) ? "(Search)" : <><LinkIcon/> {variant?.variant_id} </>,
            link: (!variantMetadata.gnomad_url || variantMetadata.gnomad_url === "nan") ?  "https://gnomad.broadinstitute.org/" : variantMetadata.gnomad_url,
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
                                External Resources
                            </Typography>
                        </Grid>
                        {referencesList.map((item, index) => (
                            <Grid container key={index} alignItems="center" sx={{margin:"2px"}}>
                                <Grid item xs={3}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                        {item.ref}
                                    </Typography>
                                </Grid>
                                <Grid item xs={9}>
                                    <Typography variant="subtitle1">
                                        <Link color="primary" href={item.link} target="_blank" sx={{display:"flex", gap:"4px"}}>{item.val}</Link>
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
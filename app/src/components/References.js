import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';


export default function References(props) {
    // BH TODO: Add conditional formatting for what is disaplyed based on which
    //          data is found in the database (i.e. no clinvar VCV means there 
    //          should be something that says "Search ClinVar" instead)
    // BH TODO: Add functional URL links for these, as well as the conditional
    //          formatting for if the link does not exist (i.e. no url in the
    //          database for gnomAD means it just brings you to the gnomAD home
    //          page instead etc.)
    const referencesList = [
        {
            ref: 'dbSNP',
            val: props.variantMetadata["dbsnp_id"],
            link: props.variantMetadata["dbsnp_url"],
        },
        {
            ref: 'UCSC',
            val: 'Search UCSC',
            link: props.variantMetadata["ucsc_url"],
        },
        {
            ref: 'Ensembl',
            val: 'Search Ensembl',
            link: props.variantMetadata["ensembl_url"],
        },
        {
            ref: 'ClinVar',
            val: props.variantMetadata["clinvar_vcv"],
            link: props.variantMetadata["clinvar_url"],
        },
        {
            ref: 'gnomAD',
            val: 'Search gnomAD',
            link: props.variantMetadata["gnomad_url"],
        }
    ]

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
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
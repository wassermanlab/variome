import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';


export default function VariantDetails({variantMetadata, ibvlFrequencies, varId}) {
    console.log({variantMetadata, ibvlFrequencies, varId})
    const variantDetailsList = [
        {
            title: 'Type',
            val: variantMetadata["var_type"],
        },
        {
            title: 'Position',
            val: variantMetadata["pos"],
        },
        {
            title: 'Site Quality',
            val: ibvlFrequencies?.quality,
        },
        {
            title: 'Allele Frequency',
            val: Number(ibvlFrequencies?.af_tot).toFixed(4)
        },
        {
            title: 'Filter',
            val: '-'
        }
    ]

    return (
        <React.Fragment>
            <Card sx={{ height: '235px' }}>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light'}}>
                                {/* TODO: Get the reference genome information from the database based 
                                    on which version of the database is currently being used -- need to
                                    figure this out a little bit more, as we will have a separate database
                                    for each reference genome */}
                                { varId } (hg38)
                            </Typography>
                        </Grid>
                        {variantDetailsList.map((item, index) => (
                            <Grid container key={index}>
                                <Grid item xs={3}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                        {item.title}
                                    </Typography>
                                </Grid>
                                <Grid item xs={9}>
                                    <Typography variant="subtitle1">
                                        {item.val}
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
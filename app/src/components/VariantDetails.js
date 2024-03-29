import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';


export default function VariantDetails(props) {
    console.log(props)
    const variantDetailsList = [
        {
            title: 'Type',
            val: props.variantMetadata["var_type"],
        },
        {
            title: 'Position',
            val: props.variantMetadata["pos"],
        },
        {
            title: 'Site Quality',
            val: props.ibvlFrequencies["quality"],
        },
        {
            title: 'Allele Frequency',
            val: Number(props.ibvlFrequencies["af_tot"]).toFixed(4)
        },
        {
            title: 'Filter',
            val: '-'
        }
    ]

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '2%' }}>
                                {/* TODO: Get the reference genome information from the database based 
                                    on which version of the database is currently being used -- need to
                                    figure this out a little bit more, as we will have a separate database
                                    for each reference genome */}
                                { props.varId } (hg38)
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
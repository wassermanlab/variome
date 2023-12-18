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
            //val: 'qual'
        },
        {
            title: 'Allele Frequency',
            val: props.ibvlFrequencies["af_tot"],
            //val: 'af'
        }
    ]

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
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
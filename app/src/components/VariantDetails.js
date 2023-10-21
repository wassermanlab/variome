import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';


export default function VariantDetails() {
    const variantDetailsList = [
        {
            title: 'Type',
            val: 'SNV',
        },
        {
            title: 'Position',
            val: '27107251',
        },
        {
            title: 'Site Quality',
            val: '447',
        },
        {
            title: 'Reference Genome',
            val: 'hg37',
        }
    ]

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        {variantDetailsList.map((item, index) => (
                            <Grid container>
                                <Grid item xs={3} key={index}>
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
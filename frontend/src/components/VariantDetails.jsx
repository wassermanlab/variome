import React from 'react';
import _ from "lodash";

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

const DECIMALS = 4;

export default function VariantDetails({ variantMetadata, ibvlFrequencies, variant }) {
    //    console.log({variantMetadata, ibvlFrequencies, varId})

    if (!variant){
        return null;
    }
    var alleleFrequency = "--";
    if (!_.isEmpty(_.get(ibvlFrequencies, 'af_tot'))){
        alleleFrequency = _.round(_.get(ibvlFrequencies, 'af_tot'), DECIMALS);
    }

    const variantDetailsList = [
        {
            title: 'Type',
            val: _.get(variant,"var_type", "-"),
        },
        {
            title: 'Site Quality',
            val: _.get(ibvlFrequencies, 'quality', '-'),
        },
        {
            title: 'Filter',
            val: _.get(variant, 'filter', '-')
        }
    ]

    return (
        <React.Fragment>
            <Card sx={{ height: '235px' }}>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light' }}>
                                {variant.variant_id} (hg38)
                            </Typography>
                        </Grid>
                        {variant? variantDetailsList.map((item, index) => (
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
                        )) : <>
                        </>}
                    </Grid>
                </CardContent>
            </Card>
        </React.Fragment>
    )
}
import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';


export default function Variant(props) {

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        <Grid item xs={7}>
                            <Typography variant="h4" sx={{ fontWeight: 'light' }}>
                                {/* TODO: Get the reference genome information from the database based 
                                    on which version of the database is currently being used -- need to
                                    figure this out a little bit more, as we will have a separate database
                                    for each reference genome */}
                                { props.varId } (hg38)
                            </Typography>
                            {/* BH TODO: Add "Copy variant ID" here */}
                        </Grid>
                        {/*
                        <Grid item xs={2}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'light' }}>
                                Alternate Allele
                            </Typography>
                            <Typography variant="subtitle1">
                                { props.variantMetadata["alt"] }
                            </Typography>
                        </Grid>
                        */}
                        {/*
                        <Grid item xs={2}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'light' }}>
                                Allele Frequency
                            </Typography>
                            <Typography variant="subtitle1">
                                1.156 E-02
                            </Typography>
                        </Grid>
                        */}
                    </Grid>
                </CardContent>
            </Card>
        </React.Fragment>
    )
}
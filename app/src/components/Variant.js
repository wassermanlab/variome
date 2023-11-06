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
                                { props.varId }
                            </Typography>
                            {/* BH TODO: Add "Copy variant ID" here */}
                        </Grid>
                        <Grid item xs={2}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'light' }}>
                                Alternate Allele
                            </Typography>
                            <Typography variant="subtitle1">
                                { props.variantMetadata["alt"] }
                            </Typography>
                        </Grid>
                        <Grid item xs={2}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'light' }}>
                                Allele Frequency
                            </Typography>
                            <Typography variant="subtitle1">
                                1.156 E-02
                            </Typography>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </React.Fragment>
    )
}
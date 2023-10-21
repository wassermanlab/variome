import React from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid'
import Container from '@mui/material/Container';

import Variant from '../components/Variant';
import VariantDetails from '../components/VariantDetails';
import References from '../components/References';
import PopFrequencies from '../components/PopFrequencies';
import Annotations from '../components/Annotations';


export default function SNV() {

    return (
        <Container maxWidth="xl">
            <Box sx={{ display: 'flex'}}>  
                <Grid container direction="row" justifyContent="center" alignItems="top" spacing={2}>
                    <Grid item xs={8}>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <Variant />
                            </Grid>
                            <Grid item xs={12}>
                                <VariantDetails />
                            </Grid>
                        </Grid> 
                    </Grid>
                    {/* BH TODO: Make the references box as tall as the Variant and Variant Details boxes together */}
                    <Grid item xs={4}>
                        <References />
                    </Grid>
                    <Grid item xs={12}>
                        <PopFrequencies />
                    </Grid>
                    <Grid item xs={12}>
                        <Annotations />
                    </Grid>
                </Grid>
            </Box> 
        </Container>
        
        
  )
}

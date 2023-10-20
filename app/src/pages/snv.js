import React from 'react';
import { styled } from '@mui/material/styles';

import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid'
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';

const PREFIX = 'Home';
const classes = {
    root: `${PREFIX}-root`,
    cta: `${PREFIX}-cta`,
}
const Root = styled('div')(({ theme }) => ({
    [`&.${classes.root}`]: {
        display: 'flex',
        alignItems: 'center',
        backgroundColor: theme.palette.primary.main
    },
    [`& .${classes.cta}`]: {
        borderRadius: theme.shape.radius
    },
}))


export default function SNV() {

    return (
        <Container maxWidth="xl">
            <Box sx={{ display: 'flex'}}>  
                <Grid container direction="row" justifyContent="center" alignItems="center" spacing={2}>
                    <Grid item xs={7}>
                        <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                            SNV
                        </Typography>
                    </Grid>
                    <Grid item xs={5}>
                        <Alert severity="warning">
                            <AlertTitle sx={{ fontWeight: 'bold' }}>Disclaimer</AlertTitle>
                            This is a test database. All data used is open source and does
                            not include Indigenous data.
                        </Alert>
                    </Grid>
                </Grid>
            </Box> 
        </Container>
        
        
  )
}

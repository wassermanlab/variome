import React from 'react';
import { styled } from '@mui/material/styles';

import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import Link from '@mui/material/Link';
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

/*const Item = styled(Card)(({ theme }) => ({
    backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
    ...theme.typography.body2,
    padding: theme.spacing(1),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  }));

const SecondItem = styled('div')(({ theme }) => ({
    textAlign: 'left',
}))*/

const Item = styled('div')(({ theme }) => ({
    backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
    border: '1px solid',
    borderColor: theme.palette.mode === 'dark' ? '#444d58' : '#ced7e0',
    padding: theme.spacing(1),
    borderRadius: '4px',
    textAlign: 'center',
  }));

export default function Home() {

    return (
        <Container maxWidth="xl">
            <Box sx={{ display: 'flex'}}>  
                <Grid container direction="row" justifyContent="center" alignItems="center" spacing={2}>
                    <Grid item xs={7}>
                        {/* BH TODO: Pick a better font for this */}
                        <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                            Welcome to the Variome Database
                        </Typography>
                    </Grid>
                    <Grid item xs={5}>
                        <Alert severity="warning">
                            <AlertTitle sx={{ fontWeight: 'bold' }}>Disclaimer</AlertTitle>
                            This is a test database. All data used is open source and does
                            not include Indigenous data.
                        </Alert>
                    </Grid>
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Grid container>
                                    <Grid item xs={6}>
                                        <Typography variant="h5" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
                                            Variant Search
                                        </Typography>
                                        <TextField id="variant-search" label="Search variants" fullWidth />
                                    </Grid>
                                    <Grid item xs={1} container direction="row" justifyContent="center" alignItems="center">
                                        <Divider orientation="vertical" variant="middle"/>
                                    </Grid>
                                    <Grid item xs={5}>
                                        <Typography variant="h5" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
                                            Examples
                                        </Typography>
                                        <Grid container>
                                            <Grid item xs={2}>
                                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>SNV:</Typography>
                                            </Grid>
                                            <Grid item xs={10}>
                                                <Typography variant="body1"><Link href="/snv/21-27099567-A-C" color="primary">21-27099567-A-C</Link></Typography>
                                            </Grid>
                                            <Grid item xs={2}>
                                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Mt:</Typography>
                                            </Grid>
                                            <Grid item xs={10}>
                                                <Typography variant="body1">Mt example</Typography>
                                            </Grid>
                                            <Grid item xs={2}>
                                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Sv:</Typography>
                                            </Grid>
                                            <Grid item xs={10}>
                                                <Typography variant="body1">SV example</Typography>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Grid container>
                                    <Grid item xs={6}>
                                        <Typography variant="h4" sx={{ fontWeight: 'bold', paddingBottom: '5%' }}>
                                            The Project
                                        </Typography>
                                        <Typography variant="h5" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
                                            "The Indigenous Background Variant Library (IBVL) is a database of the genetic
                                            diversity of Indigenous populations from Canada. It is one of the results of 
                                            the 4 phase Silent Genomes Project. The main objective of the project is to 
                                            reduce health care disparities and improve diagnostic success for children with
                                            genetic diseases from Indigenous populations"
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'light' }}>
                                            <b>Laura Arbour</b>, MD, MSc, FRCPC, FCCMG (Project Lead)
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'light' }}>
                                            <b>Nadine R. Caron</b>, MD, MPH, FRCSC (Co-Lead)
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'light' }}>
                                            <b>Wyeth W. Wasserman</b>, PhD (Co-Lead)
                                        </Typography>
                                        {/* SQ TODO: Add "Learn More" button here that links to the SGP home page */}
                                    </Grid>
                                    <Grid item xs={6}>
                                        {/* SQ TODO: Make this work with the image */}
                                        <Box
                                            component="img"
                                            alt="Temporary Logo"
                                            src="/assets/temp-logo.svg"
                                        />
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Box> 
        </Container>
        
        
  )
}

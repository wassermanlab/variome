import React, { useEffect, useState } from 'react';
import { styled } from '@mui/material/styles';
import _ from 'lodash';

import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import {Link as MuiLink} from '@mui/material';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import Search from '../components/Search';
import Link from '../components/Link';
import Api from '../Api';

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


const Item = styled('div')(({ theme }) => ({
    backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
    border: '1px solid',
    borderColor: theme.palette.mode === 'dark' ? '#444d58' : '#ced7e0',
    padding: theme.spacing(1),
    borderRadius: '4px',
    textAlign: 'center',
  }));

export default function Home({user, pageTitle, setPageTitle, message, examples}) {

    return (
        <Container maxWidth="xl">
            <Box sx={{ display: 'flex'}}>  
                <Grid container direction="row" justifyContent="center" alignItems="center" spacing={2}>
                    <Grid item xs={7}>
                        {/* BH TODO: Pick a better font for this */}
                        <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                            Welcome to {pageTitle ? pageTitle : 'Variome'}
                        </Typography>
                    </Grid>
                    <Grid item xs={5}>
                    {!_.isEmpty(message) &&
                        <Alert severity="info">
                            {message}
                        </Alert>
                    }
                    </Grid>
                    <Grid item xs={12}>
                        {user ? <Card>
                            <CardContent>
                                <Grid container>
                                    <Grid item xs={6}>
                                        <Typography variant="h5" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
                                            Variant Search
                                        </Typography>
                                        {/* TODO: Remove the arrow in the dropdown bar before anything has been typed */}
                                        <Search inputElementId="home-variant-search" variant="outlined" width="100%" marginLeft="0px"/>
                                    </Grid>
                                    <Grid item xs={1} container direction="row" justifyContent="center" alignItems="center">
                                        <Divider orientation="vertical" variant="middle"/>
                                    </Grid>
                                    { examples && 
                                    <Grid item xs={5} >
                                        <Typography variant="h5" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
                                            Example
                                        </Typography>
                                        <Grid container>
                                    { examples.snv?
                                        <>
                                            <Grid item xs={2}>
                                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>SNV:</Typography>
                                            </Grid>
                                            <Grid item xs={10}>
                                                <Typography variant="body1"><Link to={`/variant/${examples.snv.id}`} color="primary">{examples.snv.var_id}</Link></Typography>
                                            </Grid>
                                        </>
                                        : "..."
                                       }
                                       { examples.mt?
                                       <>
                                            <Grid item xs={2}>
                                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Mt:</Typography>
                                            </Grid>
                                            <Grid item xs={10}>
                                                <Typography variant="body1">Mt example</Typography>
                                            </Grid>
                                        </>
                                        : null}
                                        { examples.sv?
                                        <>
                                            <Grid item xs={2}>
                                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Sv:</Typography>
                                            </Grid>
                                            <Grid item xs={10}>
                                                <Typography variant="body1">SV example</Typography>
                                            </Grid>
                                        </>
                                        : null}
                                        </Grid>
                                    </Grid>
            }
                                </Grid>
                            </CardContent>
                        </Card> : null }

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
                                            
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'light' }}>
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'light' }}>
                                        </Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'light' }}>
                                        </Typography>
                                        
                                        <Link href="/" target="_blank" rel="noopener noreferrer">
                                            <Button size="large" sx={{ marginTop: '20px', fontWeight: 'bold', border: '1px solid grey' }}>
                                                Learn More
                                            </Button>
                                        </Link>
                                        
                                    </Grid>
                                    <Grid item xs={6}>
                                        
                                        <Box
                                            component="img"
                                            alt="Temporary Logo"
                                            src="/temp-logo.svg"
                                            style={{ width: '200px', marginLeft: '80px', marginTop: '20px', opacity:'0.2'  }}
                                        />
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Box> 

            <Box
            sx={{
                width: '100%', 
                bgcolor: '#0F3057',
                zIndex: 1000,
                marginTop: '30px', 
                padding: '20px', 
            }}
        >
            <Box sx={{ display: 'flex', justifyContent:'center', alignItems: 'center', p: 2, flexWrap:'wrap', gap:'30px'}}>
                    
                <Box
                    component="img"
                    alt="Temporary Logo"
                    src="/temp-logo.svg"
                    style={{ width: '200px', opacity:'0.2'  }}
                />
                <Typography variant="h5" component="div" sx={{ color: 'white' }}>
                    <Link href="/about" color="inherit">
                        About
                    </Link>
                </Typography>
                <Typography variant="h5" component="div" sx={{ color: 'white' }}>
                    <Link href="/terms" color="inherit">
                        Terms of Use
                    </Link>
                </Typography>
                <Typography variant="h5" component="div" sx={{ color: 'white' }}>
                    <Link href="/contact" color="inherit">
                        Contact
                    </Link>
                </Typography>
                </Box>
        

            </Box>

        </Container>
        
        
  )
}

import React from 'react';
import { styled } from '@mui/material/styles';

//import { ClassNames } from '@emotion/react';
import Grid from '@mui/material/Grid'
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

export default function Home() {

    return (     
            <Grid container direction="row" justify="center" alignItems="center" alignContent="flex-end" spacing={3}>
                <Grid container direction="column" spacing={2}>
                    <Grid item xs={12}>
                        <Typography variant="h2" gutterBottom>
                            Welcome to the IBVL Database
                        </Typography>
                    </Grid>
                </Grid>
                <Grid container direction="column" spacing={2}>
                    <Grid item xs={12}>
                        <Typography variant="h4" gutterBottom>
                            Search Bar
                        </Typography>
                    </Grid>
                </Grid>
                <Grid container direction="column" spacing={2}>
                    <Grid item xs={12}>
                        <Typography variant="h4" gutterBottom>
                            Project Overview
                        </Typography>
                    </Grid>
                </Grid>
                <Grid container direction="column" spacing={2}>
                    <Grid item xs={12}>
                        <Typography variant="h4" gutterBottom>
                            Collaborators
                        </Typography>
                    </Grid>
                </Grid>
            </Grid>
        
  )
}

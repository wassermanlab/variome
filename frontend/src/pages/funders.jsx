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
import Link from '@mui/material/Link';

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


export default function Funders() {

  return (
    <Container maxWidth="xl" >
      <Grid container direction="row" >
        <Grid item xs={12}>
          <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
            Funders
          </Typography>
        </Grid>
      </Grid>

      <Grid item xs={12} sx={{ marginTop: 2 }}>
        <Card>
          <CardContent>
          Special acknowledgement to the funders of this project which include <Link color="inherit" href="https://www.genomics-aotearoa.org.nz/" target="_blank" rel="noopener noreferrer">Genomics Aotearoa </Link> and <Link href="https://www.curekids.org.nz/" color="inherit" target="_blank" rel="noopener noreferrer">Curekids</Link>. 
          </CardContent>
        </Card>
      </Grid>




    </Container>


  )
}


import React from 'react';
import { styled } from '@mui/material/styles';

import Box from '@mui/material/Box';
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

export default function Profile({user}) {

  console.log("user", user);

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex' }}>
        <Grid container direction="row" justifyContent="center" alignItems="center" spacing={2}>
          <Grid item xs={7}>
            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
              Profile
            </Typography>
          </Grid>
        </Grid>
      </Box>

      <p>&nbsp;</p>
      <Grid container spacing={7}>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label='Username'
            placeholder='Username'
            value={user.username} 
            InputProps={{
              readOnly: true,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label='Name'
            placeholder='Full Name'
            value={user.name} 
            InputProps={{
              readOnly: true, 
            }}
          />
        </Grid>
      </Grid>
    </Container>


  )
}


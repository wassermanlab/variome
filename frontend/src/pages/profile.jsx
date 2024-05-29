
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

  return (
    <Container maxWidth="xl">
      <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
        Profile
      </Typography>

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
            label='email'
            value={user.email} 
            InputProps={{
              readOnly: true, 
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label='First Name'
            value={user.first_name} 
            InputProps={{
              readOnly: true, 
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label='Last Name'
            value={user.last_name} 
            InputProps={{
              readOnly: true, 
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label='Variant Access Count'
            value={user.variant_access_count} 
            InputProps={{
              readOnly: true, 
            }}
          />
        </Grid>
      </Grid>
    </Container>


  )
}


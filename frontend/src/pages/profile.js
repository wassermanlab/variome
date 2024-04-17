
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
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';

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

export default function Profile() {

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex' }}>
        <Grid container direction="row" justifyContent="center" alignItems="center" spacing={2}>
          <Grid item xs={7}>
            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
              Profile
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

      <p>&nbsp;</p>
      <Grid container spacing={7}>

        <Grid item xs={12} sm={6}>
          <TextField fullWidth label='Username' placeholder='username' defaultValue='username' />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField fullWidth label='Name' placeholder='Full Name' defaultValue='Full Name' />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            type='email'
            label='Email'
            placeholder='nameexample.com'
            defaultValue='name@example.com'
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select label='Role' defaultValue='admin'>
              <MenuItem value='admin'>Admin</MenuItem>
              <MenuItem value='viewer'>Viewer</MenuItem>
              <MenuItem value='editor'>Editor</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <Button variant='contained' sx={{ marginRight: 3.5 }}>
            Save Changes
          </Button>
        </Grid>
      </Grid>
    </Container>


  )
}


import React from 'react';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import Typography from '@mui/material/Typography';
import CardContent from '@mui/material/CardContent';

const referencesList = [
  {
    title: 'dbSNP',
    value: 'rs7164960',
  },
  {
    title: 'UCSC',
    value: 'Search UCSC',
  },
  {
    title: 'Esembl',
    value: 'Search Esembl',
  },
  {
    title: 'ClinVar',
    value: 'Search ClinVar ()',
  },
  {
    title: 'gnomAD',
    value: 'Search gnomAD',
  }
];

const renderReferences = () => {
  return referencesList.map((item, index) => (
    <Grid item xs={6} key={index}>
      <Typography variant='subtitle1' sx={{ fontWeight: 'bold' }}>
        {item.title}
      </Typography>
      <Typography variant='body1'>{item.value}</Typography>
    </Grid>
  ));
};

const References = () => {
  return (
    <Card>
      <CardHeader
        title='References'
        titleTypographyProps={{
          sx: {
            lineHeight: '2rem !important',
            letterSpacing: '0.15px !important',
          },
        }}
      />
      <CardContent sx={{ pt: (theme) => `${theme.spacing(3)} !important` }}>
        <Grid container spacing={2}>
          {renderReferences()}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default References
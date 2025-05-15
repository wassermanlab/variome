import React from 'react';
import {
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  CircularProgress
} from '@mui/material';
import { alpha } from '@mui/system';
import _ from 'lodash';

const DECIMALS = 4;

function createData(name, total, xx, xy, gnomad) {
  if (_.isNumber(gnomad)) {
    if (!_.isInteger(gnomad)) {
      gnomad = gnomad.toFixed(DECIMALS);
    }
  } else if (!_.isString(gnomad)) {
    gnomad = '...'
  }
  //^ gnomad is treated differently because it is fetched from the gnomad API
  // the values being set here are a default fallback

  if (!_.isEmpty(total)) {
    total = _.round(total, DECIMALS);
  }
  if (!_.isEmpty(xx)) {
    xx = _.round(xx, DECIMALS);
  }
  if (!_.isEmpty(xy)) {
    xy = _.round(xy, DECIMALS);
  }

  return { name, total, xx, xy, gnomad };
}


export default function PopFrequencies({ bvlFrequencies, gnomadFrequencies, pageTitle, gnomadLoading }) {
  var rows = []

  console.log("bvl", bvlFrequencies);
  console.log("gnomad", gnomadFrequencies);

  rows = [
    createData(
      'Allele Count',
      _.get(bvlFrequencies, "ac_tot", "-"),
      _.get(bvlFrequencies, "ac_xx", "-"),
      _.get(bvlFrequencies, "ac_xy", "-"),
      _.get(gnomadFrequencies, "ac_tot", "-"),
    ),
    createData(
      'Allele Number',
      _.get(bvlFrequencies, "an_tot", "-"),
      _.get(bvlFrequencies, "an_xx", "-"),
      _.get(bvlFrequencies, "an_xy", "-"),
      _.get(gnomadFrequencies, "an_tot", "-"),
    ),
    createData(
      'Allele Frequency',
      _.get(bvlFrequencies, "af_tot", "-"),
      _.get(bvlFrequencies, "af_xx", "-"),
      _.get(bvlFrequencies, "af_xy", "-"),
      _.get(gnomadFrequencies, "af_tot", "-"),
    ),
    createData(
      'No. of Homozygotes',
      _.get(bvlFrequencies, "hom_tot", "-"),
      _.get(bvlFrequencies, "hom_xx", "-"),
      _.get(bvlFrequencies, "hom_xy", "-"),
      _.get(gnomadFrequencies, "hom_tot", "-"),
    ),
  ];


  return (
    <React.Fragment>
      <Card>
        <CardContent>
          <Grid container>
            <Grid item xs={12}>
              <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '2%' }}>
                {pageTitle} Frequencies
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <TableContainer>
                <Table aria-label="simple table">
                  <colgroup>
                    <col style={{ width: '20%' }} />
                    <col style={{ width: '20%' }} />
                    <col style={{ width: '20%' }} />
                    <col style={{ width: '20%' }} />
                    <col style={{ width: '20%' }} />
                  </colgroup>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ borderBottom: 'none' }} />
                      <TableCell colSpan={3} align="center" sx={{ borderBottom: 'none', backgroundColor: alpha('#b3eca4', 0.25) }}>{pageTitle}</TableCell>
                      <TableCell colSpan={1} align="center" sx={{ borderBottom: 'none', backgroundColor: alpha('#ffbcbc', 0.25) }}>gnomAD v4</TableCell>
                    </TableRow>
                    {/* BH TODO: Change the font of the headings in this table */}
                    <TableRow>
                      <TableCell sx={{ borderBottom: 'none' }}></TableCell>
                      <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Total</TableCell>
                      <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>XX</TableCell>
                      <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>XY</TableCell>
                      <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((row, i) => (
                      <TableRow
                        key={row.name}
                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                      >
                        <TableCell component="th" scope="row">
                          {row.name}
                        </TableCell>
                        <TableCell align="center">{row.total}</TableCell>
                        <TableCell align="center">{row.xx}</TableCell>
                        <TableCell align="center">{row.xy}</TableCell>
                        {i === 0 && gnomadLoading ?
                          <TableCell rowSpan={4} align="center" sx={{ borderBottom: 'none' }}>
                            <CircularProgress />
                          </TableCell>
                          : <>
                            {gnomadLoading ? <></> :
                              <TableCell align="center" >{row.gnomad}</TableCell>
                            }</>
                        }
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </React.Fragment>
  )
}
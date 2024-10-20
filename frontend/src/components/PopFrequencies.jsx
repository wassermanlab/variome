import React from 'react';

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import { alpha } from '@mui/system';
import _ from 'lodash';

const DECIMALS = 4;

function createData(name, total, xx, xy, af_popmax, gnomad) {
    if (_.isNumber(gnomad)) {
        if ( !_.isInteger(gnomad) ) {
            gnomad = gnomad.toFixed(DECIMALS);
        }
    } else if (!_.isString(gnomad)) {
        gnomad = '...'
    }
    //^ gnomad is treated differently because it is fetched from the gnomad API
    // the values being set here are a default fallback
    
    if (!_.isEmpty(total)){
        total = _.round(total, DECIMALS);
    }
    if (!_.isEmpty(xx)){
        xx = _.round(xx, DECIMALS);
    }
    if (!_.isEmpty(xy)){
        xy = _.round(xy, DECIMALS);
    }

    return { name, total, xx, xy, af_popmax, gnomad };
}


export default function PopFrequencies({ibvlFrequencies, gnomadFrequencies}) {
    var rows = []

    if (!ibvlFrequencies && !gnomadFrequencies) {
        return null;
    }
    console.log("ibvl", ibvlFrequencies);
    console.log("gnomad", gnomadFrequencies);
    
    if (ibvlFrequencies && gnomadFrequencies) {
        rows = [
            createData(
                'Allele Number', 
                ibvlFrequencies["an_tot"], 
                ibvlFrequencies["an_xx"],  
                ibvlFrequencies["an_xy"],  
                '-',
                gnomadFrequencies["an_tot"], 
            ),
            createData(
                'Allele Count', 
                ibvlFrequencies["ac_tot"], 
                ibvlFrequencies["ac_xx"],  
                ibvlFrequencies["ac_xy"],  
                '-',
                gnomadFrequencies["ac_tot"],
            ),
            createData(
                'Allele Frequency',
                ibvlFrequencies["af_tot"], 
                ibvlFrequencies["af_xx"],  
                ibvlFrequencies["af_xy"], 
                '-', 
                gnomadFrequencies["af_tot"],
            ),/*
            // hidden because unable to determine how to format
            // does not belong in "IBVL" columns
            createData(
                'Allele Frequency Popmax',
                '-', 
                '-',  
                '-', 
                '-', 
                '-',
            ),*/
            createData(
                'No. of Homozygotes',
                ibvlFrequencies["hom_tot"], 
                ibvlFrequencies["hom_xx"],  
                ibvlFrequencies["hom_xy"], 
                '-', 
                gnomadFrequencies["hom_tot"],
            ),
        ];
    }
    

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '2%' }}>
                                IBVL Frequencies
                            </Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <TableContainer>
                                <Table aria-label="simple table">
                                    <colgroup>
                                        <col style={{ width: '20%'}}/>
                                        <col style={{ width: '20%'}}/>
                                        <col style={{ width: '20%'}}/>
                                        <col style={{ width: '20%'}}/>
                                        <col style={{ width: '20%'}}/>
                                    </colgroup>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell sx={{ borderBottom: 'none' }}/>
                                            <TableCell colSpan={3} align="center" sx={{ borderBottom: 'none', backgroundColor: alpha('#b3eca4', 0.25) }}>IBVL</TableCell>
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
                                        {rows.map((row) => (
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
                                                <TableCell align="center">{row.gnomad}</TableCell>
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
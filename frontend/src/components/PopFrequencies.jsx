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

function createData(name, total, xx, xy, af_popmax, gnomad) {
    if (_.isNumber(gnomad)) {
        if ( !_.isInteger(gnomad) ) {
            gnomad = gnomad.toFixed(4);
        }
    } else if (!_.isString(gnomad)) {
        gnomad = '...'
    }
    return { name, total, xx, xy, af_popmax, gnomad };
}


export default function PopFrequencies({ibvlFrequencies, gnomadFrequencies}) {
    var rows = []

    if (!ibvlFrequencies && !gnomadFrequencies) {
        return null;
    }
    
    if (ibvlFrequencies && gnomadFrequencies) {
        rows = [
            createData(
                'Allele Number', 
                Math.trunc(ibvlFrequencies["an_tot"]), 
                Math.trunc(ibvlFrequencies["an_xx"]),  
                Math.trunc(ibvlFrequencies["an_xy"]),  
                '-',
                gnomadFrequencies["an_tot"], 
            ),
            createData(
                'Allele Count', 
                Math.trunc(ibvlFrequencies["ac_tot"]), 
                Math.trunc(ibvlFrequencies["ac_xx"]),  
                Math.trunc(ibvlFrequencies["ac_xy"]),  
                '-',
                gnomadFrequencies["ac_tot"],
            ),
            createData(
                'Allele Frequency',
                Number(ibvlFrequencies["af_tot"]).toFixed(4), 
                Number(ibvlFrequencies["af_xx"]).toFixed(4),  
                Number(ibvlFrequencies["af_xy"]).toFixed(4), 
                '-', 
                gnomadFrequencies["af_tot"],
            ),
            createData(
                'Allele Frequency Popmax',
                '-', 
                '-',  
                '-', 
                '-', 
                '-',
            ),
            createData(
                'No. of Homozygotes',
                Math.trunc(ibvlFrequencies["hom_tot"]), 
                Math.trunc(ibvlFrequencies["hom_xx"]),  
                Math.trunc(ibvlFrequencies["hom_xy"]), 
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
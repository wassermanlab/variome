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

function createData(name, total, xx, xy, gnomad) {
    return { name, total, xx, xy, gnomad };
}


export default function PopFrequencies(props) {
    console.log(props.popFrequencies)
    const ibvlFreq = props.popFrequencies.genomic_ibvl_freq;
    const gnomadFreq = props.popFrequencies.genomic_gnomad_freq;
    var rows = []
    
    // BH TODO: Format decimals to appropriate scientific notation
    if (ibvlFreq && gnomadFreq) {
        rows = [
            createData(
                'Allele Number', 
                ibvlFreq["an_tot"], 
                ibvlFreq["an_xx"],  
                ibvlFreq["an_xy"],  
                gnomadFreq["an_tot"], 
            ),
            createData(
                'Allele Count', 
                ibvlFreq["ac_tot"], 
                ibvlFreq["ac_xx"],  
                ibvlFreq["ac_xy"],  
                gnomadFreq["ac_tot"],
            ),
            createData(
                'Allele Frequency',
                ibvlFreq["af_tot"], 
                ibvlFreq["af_xx"],  
                ibvlFreq["af_xy"],  
                gnomadFreq["af_tot"],
            ),
            createData(
                'No. of Homozygotes',
                ibvlFreq["hom_tot"], 
                ibvlFreq["hom_xx"],  
                ibvlFreq["hom_xy"],  
                gnomadFreq["hom_tot"],
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
                                            <TableCell colSpan={1} align="center" sx={{ borderBottom: 'none', backgroundColor: alpha('#ffbcbc', 0.25) }}>gnomAD</TableCell>
                                        </TableRow>
                                        {/* BH TODO: Change the font of the headings in this table */}
                                        <TableRow>
                                            <TableCell sx={{ borderBottom: 'none' }}></TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Total</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>xx</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>xy</TableCell>
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
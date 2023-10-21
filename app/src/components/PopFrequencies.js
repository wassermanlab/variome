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

const rows = [
    createData('Allele Number', 159, 6.0, 24, 4.0),
    createData('Allele Count', 237, 9.0, 37, 4.3),
    createData('Allele Frequency', 262, 16.0, 24, 6.0),
    createData('No. of Homozygotes', 305, 3.7, 67, 4.3),
];


export default function PopFrequencies() {

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
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
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>Total</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>xx</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>xy</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>Total</TableCell>
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
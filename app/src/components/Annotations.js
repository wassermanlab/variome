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

function createData(gene, transcript, hgvsc, hgvsp, other, polyphen, sift, cadd, splice) {
    return { gene, transcript, hgvsc, hgvsp, other, polyphen, sift, cadd, splice };
}

const rows = [
    createData('ATP5J', 159, 6.0, 24, 4.0, 1, 1, 1, 1),
    createData('ATP5J', 237, 9.0, 37, 4.3, 2, 2, 2, 2),
    createData('GABPA', 262, 16.0, 24, 6.0, 3, 3, 3, 3),
    createData('ATP5J', 305, 3.7, 67, 4.34, 4, 4, 4, 4),
];


export default function Annotations() {

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '5%' }}>
                                Annotations
                            </Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <TableContainer>
                                <Table aria-label="simple table">
                                    <colgroup>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                        <col style={{ width: '10%'}}/>
                                    </colgroup>
                                    <TableHead>
                                        {/* BH TODO: Change the font of the headings in this table */}
                                        <TableRow>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>Gene</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>Transcript</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>HGVSc</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>HGVSp</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>Other Annotations</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>Polyphen</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>SIFT</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>CADD</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none' }}>SpliceAI</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {rows.map((row) => (
                                            <TableRow
                                            key={row.name}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                            >
                                                <TableCell align="center">{row.gene}</TableCell>
                                                <TableCell align="center">{row.transcript}</TableCell>
                                                <TableCell align="center">{row.hgvsc}</TableCell>
                                                <TableCell align="center">{row.hgvsp}</TableCell>
                                                <TableCell align="center">{row.other}</TableCell>
                                                <TableCell align="center">{row.polyphen}</TableCell>
                                                <TableCell align="center">{row.sift}</TableCell>
                                                <TableCell align="center">{row.cadd}</TableCell>
                                                <TableCell align="center">{row.splice}</TableCell>
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
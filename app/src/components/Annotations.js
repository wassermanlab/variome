import React, { useState } from 'react';
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
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';


export default function Annotations(props) {

    const [selectedTranscript, setSelectedTranscript] = useState('Ensembl');

    const handleTranscriptChange = (event) => {
        setSelectedTranscript(event.target.value);
    };

    return (
        <React.Fragment>
            <Card>
                <CardContent>
                    <Grid container>
                        <Grid item xs={12}>
                            <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '2%' }}>
                                Annotations
                            </Typography>
                        </Grid>
                        <Grid item xs={12}>
                            {/* SQ TODO: Make this table scrollable for when it is larger than the screen */}
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
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Gene</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Transcript</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>HGVSc</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>HGVSp</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Other Annotations</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Polyphen</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>SIFT</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>CADD</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>SpliceAI</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    {Object.keys(props.variantAnnotations).map((key, index) => (
                                        <TableBody key={index}>
                                            <TableRow key={key}>
                                                <TableCell 
                                                    colSpan={9} 
                                                    sx={{ fontWeight: 'bold', borderBottom: 'none' }}
                                                >
                                                    {(key.charAt(0).toUpperCase() + key.slice(1)).split("_variant")}
                                                </TableCell>
                                            </TableRow>
                                            {props.variantAnnotations[key].map((transcript, index) => (
                                                /* BH TODO: Add error checking here for when there is no annotation data */
                                                <TableRow key={index}>
                                                    <TableCell align="center">{transcript.transcript.variant_transcript.transcript.gene.short_name}</TableCell>
                                                    <TableCell align="center">{transcript.transcript.variant_transcript.transcript.transcript_id}</TableCell>
                                                    <TableCell align="center">{transcript.transcript.variant_transcript.hgvsc}</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    ))}
                                </Table>
                            </TableContainer>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            <div style={{ marginTop: '20px' }} />
            
            <Card>
                <CardContent>
                    <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '2%' }}>
                        Transcripts
                    </Typography>
                    <RadioGroup
                        row
                        aria-label="transcripts"
                        name="transcripts"
                        value={selectedTranscript}
                        onChange={handleTranscriptChange}
                    >
                        <FormControlLabel value="Ensembl" control={<Radio />} label="Ensembl" />
                        <FormControlLabel value="Refseq" control={<Radio />} label="Refseq" />
                    </RadioGroup>
                </CardContent>
            </Card>

        </React.Fragment>
    )
}
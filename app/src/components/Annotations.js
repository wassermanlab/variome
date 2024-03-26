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
import _ from 'lodash';

export default function Annotations({ variantAnnotations, gene, filter }) {

    function TranscriptsAnnotationsTable({ transcripts: filteredTranscripts, gene }) {

        var impactColors = {
            'HIGH': 'red',
            'MODERATE': 'orange',
            'LOW': 'yellow',
            'MODIFIER': 'green'
        }
        filteredTranscripts = _.filter(filteredTranscripts, filter)

        
        var columns = _.without(_.keys(filteredTranscripts[0]), 'gene', 'database');
        return (
            <Box sx={{ overflowX: 'scroll', maxWidth: '100vw' }} >

                <Table aria-label={"annotations for gene " + gene}  >
                    <TableHead>
                        <TableRow>
                            {columns.map((column, index) => (
                                <TableCell key={index} align="center" sx={{ borderBottom: 'none', fontWeight: 'bold', padding: '0em 0.5em', textTransform: 'capitalize' }}>{column}</TableCell>
                            ))}
                        </TableRow>

                    </TableHead>
                    <TableBody>
                        {filteredTranscripts.map((transcript, index) => {
                            var color = impactColors[_.get(transcript,'impact')];
                            var coloredDot = <></>
                            if (color){
                                coloredDot = <span style={{ cursor:'default',fontSize:'8px', verticalAlign:'middle', padding:'0.5em', color }}>&#11044;</span>
                            }
                            return (
                                <TableRow key={index}>
                                    {columns.map((column, index) => (
                                        <TableCell align="center" key={index}>
                                            {column === 'consequence'? coloredDot : ''}
                                            {transcript[column]}
                                        </TableCell>
                                    ))}
                                </TableRow>

                            )
                        })}
                    </TableBody>
                </Table>
            </Box>
        );
    }

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
                            <div style={{ overflowX: 'auto' }}>
                            <TableContainer sx={{ overflowX: 'auto' }}>
                                <Table aria-label="simple table" sx={{ minWidth: 800 }}>
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
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Impact</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Biotype</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>HGVSc</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>HGVSp</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Polyphen</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>SIFT</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>CADD</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>SpliceAI</TableCell>
                                            <TableCell align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>Other Annotations</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    {Object.keys(variantAnnotations).map((key, index) => (
                                        <TableBody key={index}>
                                            <TableRow key={key}>
                                                <TableCell 
                                                    colSpan={9} 
                                                    sx={{ fontWeight: 'bold', borderBottom: 'none' }}
                                                >
                                                    {(key.charAt(0).toUpperCase() + key.slice(1)).split("_variant").join("").replace(/_/g, ' ')}
                                                </TableCell>
                                            </TableRow>
                                            {variantAnnotations[key].map((annotation, index) => (
                                                /* BH TODO: Add error checking here for when there is no annotation data */
                                                /* BH TODO: Add CADD and SpliceAI to API endpoint */
                                                /* BH TODO: What falls under "Other Annotations" ? */
                                                <TableRow key={index}>
                                                    <TableCell align="center">{annotation.transcript.variant_transcript.transcript.gene.short_name}</TableCell>
                                                    <TableCell align="center">{annotation.transcript.variant_transcript.transcript.transcript_id}</TableCell>
                                                    <TableCell align="center">{annotation.transcript.variant_transcript.transcript.impact}</TableCell>
                                                    <TableCell align="center">{annotation.transcript.variant_transcript.transcript.biotype}</TableCell>
                                                    <TableCell align="center">{annotation.transcript.variant_transcript.hgvsc}</TableCell>
                                                    <TableCell align="center">{(annotation.annotations.hgvsp === "nan" || typeof annotation.annotations.hgvsp == 'undefined') ? "-" : annotation.annotations.hgvsp}</TableCell>
                                                    <TableCell align="center">{(annotation.annotations.polyphen === "nan" || typeof annotation.annotations.polyphen == 'undefined') ? "-" : annotation.annotations.polyphen}</TableCell>
                                                    <TableCell align="center">{(annotation.annotations.sift === "nan" || typeof annotation.annotations.sift == 'undefined') ? "-" : annotation.annotations.sift}</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                    <TableCell align="center">-</TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    ))}
                                </Table>
                            </TableContainer>
                            </div>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            <div style={{ marginTop: '20px' }} />
            
            <Card>
                <CardContent>
                    <Typography variant="h4" sx={{ fontWeight: 'light', paddingBottom: '2%' }}>
                        Database
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

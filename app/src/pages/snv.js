import React, { useEffect, useState } from 'react';
import _ from 'lodash';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid'
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import { useParams } from 'react-router-dom'
import './styles.css'; // Import CSS file

import VariantDetails from '../components/VariantDetails';
import References from '../components/References';
import PopFrequencies from '../components/PopFrequencies';
import Annotations from '../components/Annotations';

import Api from '../Api';

export default function SNV() {
    let params = useParams();
    const varId = params.varId

    const defaultTranscriptFilter = { biotype: 'protein_coding' };
    const config = require("../config.json")
    const [loading, setLoading] = useState(true);
    const [variantMetadata, setVariantMetadata] = useState({});
    const [popFrequencies, setPopFrequencies] = useState({ genomic_gnomad_freq: {}, genomic_ibvl_freq: {} });
    const [variantAnnotations, setVariantAnnotations] = useState([]);
    const [error, setError] = useState(null);
    const [transcriptsFilter, setTranscriptsFilter] = useState(defaultTranscriptFilter);

    const [transcriptDatabase, setTranscriptDatabase] = useState('E');

    // Get Variant metadata
    useEffect(() => {
        const fetchSNVData = async () => {
            const json = await Api.get("snv/" + varId);
            setVariantMetadata(json);
            console.log('snv data', json);
        }

        const fetchFreqData = async () => {
            const json = await Api.get("genomic_population_frequencies/" + varId);
            setPopFrequencies(json);
            console.log('freq data', json);

        }


        setLoading(true);
        Promise.all([fetchSNVData(), fetchFreqData()]).then(() => {
            setLoading(false);
        });


    }, [varId])

    useEffect(() => {

        const fetchAnnData = async () => {
            const { annotations, errors } = await Api.get("annotations/" + varId, {  });
            if (errors && errors.length > 0) {
                setError(errors[0]);
                return;
            }
            setVariantAnnotations(annotations);
            console.log('annotations data', annotations);
        }

        fetchAnnData();

    }, [varId, transcriptDatabase])

    function ProteinCodingBiotypeFilterCheckbox() {

        function isChecked(){
            var iss = _.isEqual(transcriptsFilter, defaultTranscriptFilter);
            console.log(_.toPairs(transcriptsFilter), _.toPairs(defaultTranscriptFilter));
            return iss;
        }

        return <Checkbox checked={isChecked()}
            onChange={(event) => {
                if (event.target.checked) {
                    setTranscriptsFilter(defaultTranscriptFilter);
                } else {
                    setTranscriptsFilter({});
                }
            }} />
    }
    return (
        <Container maxWidth="xl">

            {error && (
                <Paper elevation={3} sx={{ p: 2, textAlign: 'center', marginTop: 2, marginBottom: 2, color: 'red' }}>
                    <strong>{error}</strong>
                </Paper>
            )}

{/*             {loading ? (
                <Dialog
                    disableEscapeKeyDown={true}
                    open={loading}
                    sx={{ textAlign: "center" }}
                >
                    <DialogTitle id="LoadingBarTitle">Loading...</DialogTitle>
                    <DialogContent><CircularProgress /></DialogContent>
                </Dialog>
            ) : (
                <Box sx={{ display: 'flex', flexDirection:'column' }}> */}
         <Grid container spacing={2} className="flex-container">
                {/* Variant ID Block */}
                <Grid item xs={12} md={6} className="flex-item ">
                    <VariantDetails varId={varId} variantMetadata={variantMetadata} ibvlFrequencies={popFrequencies.genomic_ibvl_freq} />
                </Grid>

                {/* Reference Box */}
                <Grid item xs={12} md={6} className="flex-item">
                    <References varId={varId} variantMetadata={variantMetadata} />
                </Grid>

                {/* Pop Frequencies Box */}
                <Grid item xs={12} className="gridItem">
                    <PopFrequencies varId={varId} popFrequencies={popFrequencies} />
                </Grid>

                {/* Annotations Box */}
                <Grid item xs={12} className="gridItem">
                <Paper sx={{ overflowY: 'auto', padding: 2 }} >
                            <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                                <Typography variant="h4" sx={{ marginRight: '1em' }}>Transcript Annotations</Typography>

                                <FormControlLabel
                                    sx={{ marginLeft: '0.5em', padding: '0.5em', border: '1px dotted rgba(0,0,0,0.2)' }}
                                    control={<ProteinCodingBiotypeFilterCheckbox />}
                                    label="Only Protein-coding Biotypes" />
                            </Box>
                            <Annotations
                                varId={varId}
                                variantAnnotations={variantAnnotations}
                                filter={transcriptsFilter} />
                        </Paper>
                </Grid>
            </Grid>

{/*                 </Box>
            )} */}
        </Container>
    )
}

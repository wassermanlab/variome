import React, { useEffect, useState } from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid'
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import Paper from '@mui/material/Paper';
import { useParams } from 'react-router-dom'

import VariantDetails from '../components/VariantDetails';
import References from '../components/References';
import PopFrequencies from '../components/PopFrequencies';
import Annotations from '../components/Annotations';

import Api from '../Api';

export default function SNV() {
    let params = useParams();
    const varId = params.varId
    const config = require("../config.json")
    const [loading, setLoading] = useState(true);
    const [variantMetadata, setVariantMetadata] = useState({});
    const [popFrequencies, setPopFrequencies] = useState({ genomic_gnomad_freq: {}, genomic_ibvl_freq: {} });
    const [variantAnnotations, setVariantAnnotations] = useState({});
    const [error, setError] = useState(null);

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

        const fetchAnnData = async () => {
            const json = await Api.get("annotations/" + varId);
            setVariantAnnotations(json);
            console.log('annotations data', json);

        }

        setLoading(true);
        Promise.all([fetchSNVData(), fetchFreqData(), fetchAnnData()]).then(() => {
            setLoading(false);
        });


    }, [varId])

    return (
        <Container maxWidth="xl">

            {error && (
                <Paper elevation={3} sx={{ p: 2, textAlign: 'center', marginTop: 2, marginBottom: 2, color: 'red' }}>
                    <strong>{error}</strong>
                </Paper>
            )}

            {loading ? (
                <Dialog
                    disableEscapeKeyDown={true}
                    open={loading}
                    sx={{ textAlign: "center" }}
                >
                    <DialogTitle id="LoadingBarTitle">Loading...</DialogTitle>
                    <DialogContent><CircularProgress /></DialogContent>
                </Dialog>
            ) : (
                <Box sx={{ display: 'flex', flexDirection:'column' }}>

                    <Grid item xs={12}>
                        <VariantDetails varId={varId} variantMetadata={variantMetadata} ibvlFrequencies={popFrequencies.genomic_ibvl_freq} />
                    </Grid>
                    <Grid item xs={4}>
                        <References varId={varId} variantMetadata={variantMetadata} />
                    </Grid>
                    <Grid item xs={12}>
                        <PopFrequencies varId={varId} popFrequencies={popFrequencies} />
                    </Grid>
                    <Grid item xs={12}>
                        <Paper sx={{  overflowY: 'auto', padding: 2 }}>
                            <Annotations varId={varId} variantAnnotations={variantAnnotations} />
                        </Paper>

                    </Grid>
                </Box>
            )}
        </Container>
    )
}

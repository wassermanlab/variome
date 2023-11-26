import React, { useEffect, useState } from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid'
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import { Paper } from '@mui/material';
import { useParams } from 'react-router-dom'

import Variant from '../components/Variant';
import VariantDetails from '../components/VariantDetails';
import References from '../components/References';
import PopFrequencies from '../components/PopFrequencies';
import Annotations from '../components/Annotations';


export default function SNV() {
    let params = useParams();
    const varId = params.varId
    const [loading, setLoading] = useState(false);
    const [variantMetadata, setVariantMetadata] = useState({});
    const [popFrequencies, setPopFrequencies] = useState({});
    const [variantAnnotations, setVariantAnnotations] = useState({});
    const [error, setError] = useState(null); 

    // Get Variant metadata
    useEffect(() => {
        const fetchSNVData = async () => {
            setLoading(true);
            try {
                const response = await fetch("http://127.0.0.1:8000/api/snv/" + varId);
                const json = await response.json();
                setVariantMetadata(json);
                console.log(json);
            } catch (error) {
                setError("Error fetching variant metadata");
            } finally {
                setLoading(false);
            }
        }

        const fetchFreqData = async () => {
            setLoading(true);
            try {
                const response = await fetch("http://127.0.0.1:8000/api/genomic_population_frequencies/" + varId);
                const json = await response.json();
                setPopFrequencies(json);
                console.log(json);
            } catch (error) {
                setError("Error fetching population frequencies");
            } finally {
                setLoading(false);
            }
        }

        const fetchAnnData = async () => {
            setLoading(true);
            try {
                const response = await fetch("http://127.0.0.1:8000/api/annotations/" + varId);
                const json = await response.json();
                setVariantAnnotations(json);
                console.log(json);
            } catch (error) {
                setError("Error fetching annotations");
            } finally {
                setLoading(false);
            }
        }

        fetchSNVData();
        fetchFreqData();
        fetchAnnData();
        //setLoading(false);


    }, [varId])

    /*
    // Get Population frequencies data
    useEffect(() => {
        const fetchRefData = async () => {
            const response = await fetch("http://127.0.0.1:8000/api/genomic_population_frequencies/" + varId);
            const json = await response.json(); //TODO: Error check result
            setPopFrequencies(json[0]);
            console.log(json[0])
        }
        fetchRefData();
    }, [varId])

    // Get Variant annotation data
    useEffect(() => {
        const fetchRefData = async () => {
            const response = await fetch("http://127.0.0.1:8000/api/annotations/" + varId);
            const json = await response.json(); //TODO: Error check result
            setVariantAnnotations(json);
        }
        fetchRefData();
    }, [varId])
    */

    return (
        <Container maxWidth="xl">
            <Dialog
                disableEscapeKeyDown={true}
                open={loading}
                sx={{ textAlign: "center" }}
            >
                <DialogTitle id="LoadingBarTitle">Loading...</DialogTitle>
                <DialogContent><CircularProgress/></DialogContent>
            </Dialog>

            {error && (
                <Paper elevation={3} sx={{ p: 2, textAlign: 'center', marginTop: 2, marginBottom: 2, color: 'red' }}>
                    <strong>{error}</strong>
                </Paper>
            )}
            
            <Box sx={{ display: 'flex'}}>  
                <Grid container direction="row" justifyContent="center" alignItems="top" spacing={2}>
                    <Grid item xs={8}>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <Variant varId={varId} variantMetadata={variantMetadata}/>
                            </Grid>
                            <Grid item xs={12}>
                                <VariantDetails varId={varId} variantMetadata={variantMetadata}/>
                            </Grid>
                        </Grid> 
                    </Grid>
                    {/* BH TODO: Make the references box as tall as the Variant and Variant Details boxes together */}
                    <Grid item xs={4}>
                        <References varId={varId} variantMetadata={variantMetadata}/>
                    </Grid>
                    <Grid item xs={12}>
                        <PopFrequencies varId={varId} popFrequencies={popFrequencies}/>
                    </Grid>
                    <Grid item xs={12}>
                        <Annotations varId={varId} variantAnnotations={variantAnnotations}/>
                    </Grid>
                </Grid>
            </Box> 
        </Container>
  )
}

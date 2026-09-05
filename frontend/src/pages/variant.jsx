import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  Container,
  Dialog,
  DialogContent,
  DialogTitle,
  Grid,
  Paper,
  Radio,
  RadioGroup,
  Typography
} from "@mui/material";

import { useParams } from "react-router-dom";
import "./styles.css"; // Import CSS file

import VariantDetails from "../components/VariantDetails";
import References from "../components/References";
import PopFrequencies from "../components/PopFrequencies";
import Annotations from "../components/Annotations";

import Api from "../Api";

export default function Variant({pageTitle}) {
  let params = useParams();
  const varId = params.varId;

  const [loading, setLoading] = useState(true);
  const [gnomadLoading, setGnomadLoading] = useState(true);
  const [variant, setVariant] = useState({});
  const [variantMetadata, setVariantMetadata] = useState({});
  const [gnomadFrequencies, setGnomadFrequencies] = useState({});
  const [bvlFrequencies, setbvlFrequencies] = useState({});
  const [variantAnnotations, setVariantAnnotations] = useState([]);
  const [error, setError] = useState(null);

  // Get Variant metadata
  useEffect(() => {
    setError(null);
    setVariant(null);
    setVariantMetadata(null);
    setGnomadFrequencies(null);
    setbvlFrequencies(null);
    setVariantAnnotations(null);
    setLoading(true);
    setGnomadLoading(true);

    Api.get("variant/" + varId)
      .then(({ variant, snv, bvlFrequencies, annotations }) => {
//        console.log("variant", variant);
        setVariant(variant);
        setVariantMetadata(snv);
        setbvlFrequencies(bvlFrequencies);
        setVariantAnnotations(annotations);
        setLoading(false);
      })
      .catch((r) => {
        if (r.status == 429) {
          setError(
            "Variant requests are limited on a 24-hour basis. Please try again later"
          );
        } else if (r.status == 404){
          setError("Variant not found");
        } else if (r.status == 403) {
          setError("You are not logged in. Please refresh the page, and log in again.");
        } else {
          setError("Sorry, something went wrong");
        }
        setGnomadLoading(false);
        setLoading(false);
      });
  }, [varId]);

  useEffect(() => {
      if (!variant || !variant.variant_id) {
        return;
      }

      setGnomadLoading(true);
      Api.get("gnomad-frequencies", { variant: variant.variant_id })
        .then(({ gnomadFrequencies }) => {
          setGnomadFrequencies(gnomadFrequencies);
          setGnomadLoading(false);
        })
        .catch(() => {
          setGnomadFrequencies(null);
          setGnomadLoading(false);
        });
  }, [variant]);

  return (
    <Container maxWidth="xl">
      {error && (
        <Paper
          elevation={3}
          sx={{
            p: 2,
            textAlign: "center",
            marginTop: 2,
            marginBottom: 2,
            color: "red"
          }}
        >
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
          <DialogContent>
            <CircularProgress />
          </DialogContent>
        </Dialog>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column" }}>
          <Grid container spacing={2} className="flex-container">
            {/* Variant ID Block */}
            <Grid item xs={12} md={6} className="flex-item ">
              <VariantDetails
                variant={variant}
                variantMetadata={variantMetadata}
                bvlFrequencies={bvlFrequencies}
              />
            </Grid>

            {/* Reference Box */}
            <Grid item xs={12} md={6} className="flex-item">
              <References variant={variant} variantMetadata={variantMetadata} />
            </Grid>

            {/* Pop Frequencies Box */}
            <Grid item xs={12} className="gridItem">
              <PopFrequencies
                varId={varId}
                bvlFrequencies={bvlFrequencies}
                gnomadFrequencies={gnomadFrequencies}
                pageTitle={pageTitle}
                gnomadLoading={gnomadLoading}
                variantMetadata={variantMetadata}
              />
            </Grid>

            {/* Annotations Box */}

            <Annotations
              varId={varId}
              variantAnnotations={variantAnnotations}
            />
          </Grid>
        </Box>
      )}
    </Container>
  );
}

import React, { useEffect, useState } from "react";
import _ from "lodash";
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

export default function Variant() {
  let params = useParams();
  const varId = params.varId;

  const [loading, setLoading] = useState(true);
  const [variant, setVariant] = useState({});
  const [variantMetadata, setVariantMetadata] = useState({});
  const [gnomadFrequencies, setGnomadFrequencies] = useState({});
  const [ibvlFrequencies, setIbvlFrequencies] = useState({});
  const [variantAnnotations, setVariantAnnotations] = useState([]);
  const [error, setError] = useState(null);

  // Get Variant metadata
  useEffect(() => {
    setError(null);
    setVariant(null);
    setVariantMetadata(null);
    setGnomadFrequencies(null);
    setIbvlFrequencies(null);
    setVariantAnnotations(null);
    setLoading(true);

    Api.get("variant/" + varId)
      .then(({ variant, snv, ibvlFrequencies, annotations }) => {
//        console.log("variant", variant);
        setVariant(variant);
        setVariantMetadata(snv);
        //          setGnomadFrequencies(gnomadFrequencies);
        setIbvlFrequencies(ibvlFrequencies);
        setVariantAnnotations(annotations);
        setLoading(false);
      })
      .catch(({ status, statusText, errors, message }) => {
        console.log("variant fetch err", message);
        if (status == 429) {
          setError(
            "Variant requests are limited on a 24-hour basis. Please try again later"
          );
        } else {
          setError("Sorry, something went wrong");
        }
        setLoading(false);
      });
  }, [varId]);

  useEffect(() => {
    if (variant && variant.variant_id) {
      const QUERY = `
    query getVariant($variantId: String!) {
      variant(variantId: $variantId, dataset: gnomad_r4) {
        joint {
          ac
          an
          homozygote_count
        }
      }
    }
    `;
      //    console.log(QUERY);
      var body = JSON.stringify(
        {
          query: QUERY,
          variables: {
            variantId: variant.variant_id
          }
        },
        null,
        2
      );
      //    console.log(body);

      fetch("https://gnomad.broadinstitute.org/api", {
        method: "POST",
        body,
        headers: {
          "Content-Type": "application/json"
        }
      })
        .then((response) => response.json())
        .then((data) => {
          var variant = _.get(data, "data.variant", {});
          console.log("variant", variant);
          var ac_tot =
            _.get(variant, "joint.ac", 0);
          var an_tot =
            _.get(variant, "joint.an", 0);
            //handle 0??
          var af_tot = _.divide(ac_tot, an_tot);
          var hom_tot =
            _.get(variant, "joint.homozygote_count", 0)

          //          console.log("gnomad freqs", { ac_tot, an_tot, af_tot, hom_tot });
          setGnomadFrequencies({ ac_tot, an_tot, af_tot, hom_tot });
        });
    }
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
                ibvlFrequencies={ibvlFrequencies}
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
                ibvlFrequencies={ibvlFrequencies}
                gnomadFrequencies={gnomadFrequencies}
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

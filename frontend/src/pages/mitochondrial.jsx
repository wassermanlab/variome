import React from "react";
import { Box, Grid } from "@mui/material";
import VariantDetails from "../components/VariantDetails";
import References from "../components/References";
import Annotations from "../components/Annotations";
import MitochondrialFrequencies from "../components/MitochondrialFrequencies";

export default function MitochondrialVariant({
  variant, variantMetadata, bvlFrequencies, gnomadFrequencies,
  variantAnnotations, pageTitle, varId
}) {
  return (
    <Box sx={{ display: "flex", flexDirection: "column" }}>
      <Grid container spacing={2} className="flex-container">
        <Grid item xs={12} md={6} className="flex-item">
          <VariantDetails variant={variant} variantMetadata={variantMetadata} bvlFrequencies={bvlFrequencies} />
        </Grid>
        <Grid item xs={12} md={6} className="flex-item">
          <References variant={variant} variantMetadata={variantMetadata} />
        </Grid>
        <Grid item xs={12}>
          <MitochondrialFrequencies bvlFrequencies={bvlFrequencies}
            gnomadFrequencies={gnomadFrequencies} pageTitle={pageTitle} />
        </Grid>
        <Annotations varId={varId} variantAnnotations={variantAnnotations} />
      </Grid>
    </Box>
  );
}

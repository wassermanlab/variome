import React, { useId } from "react";
import {
  Box, Card, CardContent, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Typography
} from "@mui/material";

function displayNumber(value) {
  const numeric = typeof value === "string" && value.trim() !== "" ? Number(value) : value;
  return typeof numeric === "number" && Number.isFinite(numeric)
    ? numeric.toLocaleString("en-US", { maximumSignificantDigits: 6 })
    : "-";
}

function HeteroplasmyHistogram({ histogram }) {
  const titleId = useId();
  const descriptionId = useId();
  const bins = typeof histogram === "string" && histogram.trim()
    ? histogram.split(",").map(value => value.trim() === "" ? NaN : Number(value))
    : [];
  const valid = bins.length > 0 && bins.every(value => Number.isInteger(value) && value >= 0);

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h5">Heteroplasmy distribution</Typography>
      {!valid ? <Typography>No heteroplasmy histogram available.</Typography> : (
        <Box sx={{ maxWidth: 720 }}>
          <Typography variant="body2">Heteroplasmy level (%) · Count</Typography>
          <svg viewBox="0 0 640 230" role="img" aria-labelledby={titleId} aria-describedby={descriptionId}
            style={{ width: "100%", height: "auto", color: "inherit" }}>
            <title id={titleId}>Heteroplasmy histogram</title>
            <desc id={descriptionId}>
              {bins.map((count, i) =>
                `${Math.round(i * 100 / bins.length)}–${Math.round((i + 1) * 100 / bins.length)}%: ${count}`
              ).join("; ")}
            </desc>
            {bins.map((count, i) => {
              const width = 600 / bins.length;
              const height = count / Math.max(1, ...bins) * 160;
              const label = `${Math.round(i * 100 / bins.length)}–${Math.round((i + 1) * 100 / bins.length)}%`;
              return (
                <g key={i}>
                  <title>{label}: {count}</title>
                  <rect x={20 + i * width} y={185 - height}
                    width={Math.max(1, width - 3)} height={height} fill="#176b87" />
                  <text x={20 + (i + 0.5) * width} y={177 - height} textAnchor="middle"
                    fontSize="12" fill="currentColor">{count}</text>
                  <text x={20 + (i + 0.5) * width} y="205" textAnchor="middle"
                    fontSize={bins.length > 10 ? 8 : 11} fill="currentColor">{label}</text>
                </g>
              );
            })}
            <line x1="20" y1="185" x2="620" y2="185" stroke="currentColor" />
          </svg>
        </Box>
      )}
    </Box>
  );
}

export default function MitochondrialFrequencies({ bvlFrequencies, gnomadFrequencies, pageTitle }) {
  const rows = [
    ["Allele Number", "an", "an"],
    ["Allele Count", "ac_hom", "ac_het"],
    ["Allele Frequency", "af_hom", "af_het"],
    ["Maximum heteroplasmy level", "max_hl", "max_hl"],
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h4" sx={{ fontWeight: "light", mb: 2 }}>
          {pageTitle} Mitochondrial Frequencies
        </Typography>
        <TableContainer>
          <Table aria-label="Mitochondrial frequencies">
            <TableHead>
              <TableRow>
                <TableCell scope="col" rowSpan={2}>Metric</TableCell>
                <TableCell align="center" colSpan={2} scope="colgroup">{pageTitle || "Local cohort"}</TableCell>
                <TableCell align="center" colSpan={2} scope="colgroup">gnomAD mitochondrial</TableCell>
              </TableRow>
              <TableRow>
                {[0, 1].map(source => (
                  <React.Fragment key={source}>
                    <TableCell align="center" scope="col">Homoplasmic</TableCell>
                    <TableCell align="center" scope="col">Heteroplasmic</TableCell>
                  </React.Fragment>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map(([label, homKey, hetKey]) => (
                <TableRow key={label}>
                  <TableCell component="th" scope="row">{label}</TableCell>
                  {[bvlFrequencies, gnomadFrequencies].map((frequencies, i) =>
                    homKey === hetKey
                      ? <TableCell key={i} colSpan={2} align="center">{displayNumber(frequencies?.[homKey])}</TableCell>
                      : <React.Fragment key={i}>
                          <TableCell align="center">{displayNumber(frequencies?.[homKey])}</TableCell>
                          <TableCell align="center">{displayNumber(frequencies?.[hetKey])}</TableCell>
                        </React.Fragment>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Typography variant="body2" sx={{ mt: 1 }}>- indicates unavailable data. Heteroplasmy levels range from 0 to 1.</Typography>
        <HeteroplasmyHistogram histogram={bvlFrequencies?.hl_hist} />
      </CardContent>
    </Card>
  );
}

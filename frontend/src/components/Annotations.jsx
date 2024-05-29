import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Checkbox,
  Radio,
  RadioGroup,
  FormControlLabel,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import _ from "lodash";

export default function Annotations({ variantAnnotations, gene }) {

  const FILTER_KEY = "transcript-filter";

  var defaultTranscriptFilter = { biotype: "protein_coding" };
  var startingTranscriptFilter = defaultTranscriptFilter;

  try {
    var savedFilter = JSON.parse(localStorage.getItem(FILTER_KEY));
    if (_.isObject(savedFilter)) {
      startingTranscriptFilter = savedFilter;
    }
  } catch (e) {}

  const [filter, setFilter] = useState(
    startingTranscriptFilter
  );

  useEffect(() => {
    localStorage.setItem(FILTER_KEY, JSON.stringify(filter));
  }, [filter]);

  function ProteinCodingBiotypeFilterCheckbox() {
    function isChecked() {
      var iss = _.isEqual(filter, defaultTranscriptFilter);
      console.log(
        _.toPairs(filter),
        _.toPairs(defaultTranscriptFilter)
      );
      return iss;
    }

    return (
      <Checkbox
        checked={isChecked()}
        onChange={(event) => {
          if (event.target.checked) {
            setFilter(defaultTranscriptFilter);
          } else {
            setFilter({});
          }
        }}
      />
    );
  }

  function TranscriptsAnnotationsTable({
    transcripts: filteredTranscripts,
    gene
  }) {
    var impactColors = {
      HIGH: "red",
      MODERATE: "yellow",
      LOW: "green",
      MODIFIER: "black"
    };
    filteredTranscripts = _.filter(filteredTranscripts, filter);

    var columns = _.without(_.keys(filteredTranscripts[0]), "gene", "database");
    return (
      <Box sx={{ overflowX: "scroll", maxWidth: "100vw" }}>
        <Table aria-label={"annotations for gene " + gene}>
          <TableHead>
            <TableRow>
              {columns.map((column, index) => (
                <TableCell
                  key={index}
                  align="center"
                  sx={{
                    borderBottom: "none",
                    fontWeight: "bold",
                    padding: "0em 0.5em",
                    textTransform: "capitalize"
                  }}
                >
                  {column}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredTranscripts.map((transcript, index) => {
              var color = impactColors[_.get(transcript, "impact")];
              var coloredDot = <></>;
              if (color) {
                coloredDot = (
                  <span
                    style={{
                      cursor: "default",
                      fontSize: "8px",
                      verticalAlign: "middle",
                      padding: "0.5em",
                      color
                    }}
                  >
                    &#11044;
                  </span>
                );
              }
              return (
                <TableRow key={index}>
                  {columns.map((column, index) => (
                    <TableCell align="center" key={index}>
                      {column === "consequence" ? coloredDot : ""}
                      {transcript[column]}
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Box>
    );
  }

  return _.size(variantAnnotations) > 0 ? (
    <Grid item xs={12} className="gridItem">
      <Paper sx={{ overflowY: "auto", padding: 2 }}>
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center"
          }}
        >
          <Typography variant="h4" sx={{ marginRight: "1em" }}>
            Transcript Annotations
          </Typography>

          <FormControlLabel
            sx={{
              marginLeft: "0.5em",
              padding: "0.5em",
              border: "1px dotted rgba(0,0,0,0.2)"
            }}
            control={<ProteinCodingBiotypeFilterCheckbox />}
            label="Only Protein-coding Biotypes"
          />
        </Box>
        <Grid container>
          <Grid item xs={12}>
            <TableContainer>
              {variantAnnotations.map((geneAnnotations) => {
                return (
                  <Card key={geneAnnotations.gene}>
                    <h3>{geneAnnotations.gene}</h3>
                    {geneAnnotations.transcripts &&
                    geneAnnotations.transcripts.length > 0 ? (
                      <TranscriptsAnnotationsTable
                        transcripts={geneAnnotations.transcripts}
                        gene={geneAnnotations.gene}
                      />
                    ) : (
                      <></>
                    )}
                  </Card>
                );
              })}
            </TableContainer>
          </Grid>
        </Grid>
      </Paper>
    </Grid>
  ) : null;
}

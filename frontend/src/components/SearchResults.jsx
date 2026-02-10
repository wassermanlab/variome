
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SearchContext } from './SearchProvider';
import { Box, List, ListItem, ListItemText, useTheme } from "@mui/material"
import { alpha } from '@mui/system';

import LoadingSpinner from "./LoadingSpinner";

export default function SearchResults({ sx, overlay }) {

  const {palette} = useTheme();
  const navigate = useNavigate();

  const searchContext = useContext(SearchContext);


  function isExactMatch() {
    return _.size(searchContext.results) === 1 && _.size(searchContext.matchPairs) === 4; // if there are 4 match pairs, we matched on all 4 fields (chrom, pos, ref, alt)
  }

  function openVariant(variant) {
    searchContext.setHideResultsOverride(true)
    navigate(`/variant/${variant.id}`);
  }

  function shouldShowResults() {
    if (searchContext.hideResultsOverride) return false;
    if (_.isEmpty(searchContext.query)) return false;

    return searchContext.loading || _.size(searchContext.results) > 0 || _.size(searchContext.nearby) > 0 || searchContext.resultsMessage;
  }

  function renderSearchResult(variant, index) {
    
    return <ListItem style={{
      background:"transparent",
      border: isExactMatch() ? `1px solid ${palette.highlight.main}` : "none",
      }} key={index} button onClick={() => openVariant(variant)}>
      <ListItemText primary={variant.variant_id} secondary={variant.var_type} />
    </ListItem>
  }
  function renderNearbySearchResult(variant, index) {

    return <ListItem style={{background: "transparent"}} key={index} button onClick={() => openVariant(variant)}>
      <ListItemText primary={variant.variant_id} secondary={variant.var_type} />
    </ListItem>
    }
  return (shouldShowResults() &&
    <>
      {overlay && <Box sx={{ height: "100vh", width: "100vw", background: "rgba(0,0,0,0.35)", position: "fixed", top: 64, left: 0, right: 0 }}
        onClick={() => {
          searchContext.setHideResultsOverride(true);
        }}></Box>}
      <Box sx={{
        ...sx,
        height: "auto",
        padding: "1em",
        background: "white"
      }}>
        {searchContext.loading ? <LoadingSpinner/> : <>


          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", background: isExactMatch() ? alpha(palette.highlight.main, 0.25) : "transparent", padding: "8px" }}>
            <label>{isExactMatch() ? "Exact Match:": "Your search:"}</label>
            {searchContext.matchPairs.map(([key, val]) => {
              return (
                <span key={key}>
                  <span style={{ fontWeight: "bold" }}>
                    {" "}
                    {key}
                    {": "}
                  </span>
                  <span style={{}}>{val}</span>
                </span>
              );
            })}
            {isExactMatch() ? renderSearchResult(searchContext.results[0], 0) : null}
          </div>

          <List>
            {searchContext.warnings.map((warning, index) => (
              <ListItem key={index} style={{background: alpha(palette.warning.main, 0.15) }} button={!!warning.link} onClick={() => {
                if (warning.link) {
                  // TODO
//                  searchContext.setHideResultsOverride(true);
//                  navigate(warning.link);
                }
              }}>
                <ListItemText primary={warning.label} />
              </ListItem>
            ))}
            {isExactMatch() ? null : _.map(searchContext.results, renderSearchResult)}
          </List>
          {searchContext.resultsMessage}
          <List>
            {_.map(searchContext.nearby, renderNearbySearchResult)}
          </List>
          {/*}
        <pre>results...{JSON.stringify(searchContext.results, null, 2)}</pre>
        <pre>nearby...{JSON.stringify(searchContext.nearby, null, 2)}</pre> {*/}
        </>}
      </Box>
    </>
  )
}
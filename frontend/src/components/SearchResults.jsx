
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


  function isExactMatch(result) {
    var is = _.isObject(result) && _.size(searchContext.matchPairs) === 4;
    _.each(searchContext.groups, (val, key) => {
      if (_.get(result, `snv__${key}`) != val){
        is = false;
      }
    });
    return is;
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

  function DebugShowResults(){
    return <pre style={{height:"400px"}}> debugshowresults <br/>
      searchContext.hideResultsOverride<br/>
      {searchContext.hideResultsOverride?  "true" : "false"}<br/>
      searchContext.query <br/>
      "{searchContext.query}" <br/>
      searchContext.loading <br/>
      {searchContext.loading ?  "true" : "false"}
      </pre>
  }

  function renderSearchResult(variant, index, styleOverrides, postLabel) {
    
    return <ListItem 
      sx={{
        background:"transparent",
        cursor: "pointer",
        ...styleOverrides
        }} 
      key={index} 
      onClick={() => openVariant(variant)}>
      <ListItemText primary={<>{variant.variant_id} {postLabel}</>} secondary={variant.var_type} />
    </ListItem>
  }
  return (shouldShowResults() &&
    <>
    {/*}
    <pre>{JSON.stringify(searchContext.groups, null, 2)}</pre>{*/}
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
            {searchContext.matchPairs.length > 0 && <label>Your search:</label> }
            {searchContext.matchPairs.map(([key, val]) => {
              return (
                <span key={key}>
                  <span style={{ fontWeight: "bold" }}>
                    {" "}
                    {key}
                    {": "}
                  </span>
                  <span style={{wordBreak: "break-all"}}>{val}</span>
                </span>
              );
            })}
          </div>

          <List>
            {searchContext.warnings.map((warning, index) => (
              <ListItem 
                key={index} 
                style={{
                  background: alpha(palette.warning.main, 0.15),
                  wordBreak: "break-word" }} 
                onClick={() => {
                  if (warning.link) {
                    // TODO
  //                  searchContext.setHideResultsOverride(true);
  //                  navigate(warning.link);
                  }
                }}>
                <ListItemText primary={warning.label} />
              </ListItem>
            ))}
            {_.map(searchContext.results, (r,i) => {
                if (isExactMatch(r)){
                  return renderSearchResult(r, i, {
                    "&:hover":{
                      backgroundColor: alpha(palette.highlight.main, 0.45)
                    },
                    backgroundColor: alpha(palette.highlight.main, 0.25),
                    fontWeight:"bold",
                    border: `1px solid ${palette.highlight.main}`
                  },
                  <span style={{color:"green", paddingLeft:"0.5em"}}>(Exact match)</span>
                  )
                } else {
                  return renderSearchResult(r, i, {
                    "&:hover":{
                      backgroundColor: alpha(palette.grey[200], 0.6)
                    },
                    border: "none",
                  },
                  <span style={{color:"rgba(0, 0, 0, 0.54)", paddingLeft:"0.5em"}}>(Position match)</span>)
                }
              })}
          </List>
          {searchContext.nearbyMessage}
          {searchContext.resultsMessage}
          {searchContext.errorMessage ?  <p><span style={{color: palette.error.main}}>{searchContext.errorMessage}</span></p> : null}
          
          <List>
            {_.map(searchContext.nearby, (r,i) => {
                return renderSearchResult(r,i,{
                  "&:hover": {
                    backgroundColor: alpha(palette.grey[200], 0.6)
                  }
                });
              })}
          </List>
          {/*}
        <pre>results...{JSON.stringify(searchContext.results, null, 2)}</pre>
        <pre>nearby...{JSON.stringify(searchContext.nearby, null, 2)}</pre> {*/}
        </>}
      </Box>
    </>
  )
}
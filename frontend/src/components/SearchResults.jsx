
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SearchContext } from './SearchProvider';
import { Box, List, ListItem, ListItemText } from "@mui/material"

import LoadingSpinner from "./LoadingSpinner";

export default function SearchResults({ sx, overlay }) {

  const navigate = useNavigate();

  const searchContext = useContext(SearchContext);


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
    return <ListItem key={index} button onClick={() => openVariant(variant)}>
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

          {searchContext.summary}

          <List>
            {_.map(searchContext.results, renderSearchResult)}
          </List>
          {searchContext.resultsMessage}
          <List>
            {_.map(searchContext.nearby, renderSearchResult)}
          </List>
          {/*}
        <pre>results...{JSON.stringify(searchContext.results, null, 2)}</pre>
        <pre>nearby...{JSON.stringify(searchContext.nearby, null, 2)}</pre> {*/}
        </>}
      </Box>
    </>
  )
}
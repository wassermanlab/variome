import React from 'react';
import { useState, useEffect, useContext } from 'react';
import _ from 'lodash';

import { Button, TextField } from '@mui/material';
import { Search } from '@mui/icons-material';
import { SearchContext } from './SearchProvider';

export default function SearchInput({ marginLeft, inputElementId, variant, sx }) {

  const searchContext = useContext(SearchContext);

  const [inputQuery, setInputQuery] = useState("");



  useEffect(() => {
    if (_.trim(searchContext.query) != _.trim(inputQuery)) {
      setInputQuery(searchContext.query);
    } else {
      //      console.log("searchcontext q", searchContext.query, "inputQuery", inputQuery);
    }
  }, [searchContext.query]);

  // if url has ?q=... set inputQuery to that on initial load (and hmr refresh?)
  // primarily for dev aid, but also could be used to hyperlink to search results
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q');
    if (q && _.trim(q) != _.trim(inputQuery)) {
      setInputQuery(q);
      searchContext.submitSearch(q);
    }
  }, []);

  const handleSubmit = (event) => {
    event.preventDefault();
    searchContext.submitSearch(inputQuery);
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", alignItems: "center", marginLeft, ...sx }}>
      <TextField
      id={inputElementId} 
      placeholder="Search variants"
      variant={variant}
      value={inputQuery}
      onFocus={() => {
        if (_.isFunction(searchContext.onInputFocus)) {
          searchContext.onInputFocus();
        } else {
          console.log(searchContext.onInputFocus)
        }
      }}

      InputProps={{
        startAdornment: <Search sx={{ marginRight: "8px" }} />
      }}
      sx={{width: "100%"}}
      onChange={(event) => {
        setInputQuery(event.target.value);
      }}
      />
      <Button type="submit" disabled={searchContext.loading} >
        Submit
      </Button>
    </form>
  );
}
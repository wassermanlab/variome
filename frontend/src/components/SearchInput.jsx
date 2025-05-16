import React from 'react';
import { useState, useEffect, useContext } from 'react';
import _ from 'lodash';

import { TextField, List, ListItem, ListItemText, Divider, Box } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { SearchContext } from './SearchProvider';

import {
  styled,
  useTheme
}
  from "@mui/material/styles";

export default function SearchInput({ width, marginLeft, inputElementId, variant, sx }) {

  const searchContext = useContext(SearchContext);

  const [inputQuery, setInputQuery] = useState("");



  useEffect(() => {
    if (_.trim(searchContext.query) != _.trim(inputQuery)) {
      setInputQuery(searchContext.query);
    } else {
      //      console.log("searchcontext q", searchContext.query, "inputQuery", inputQuery);
    }
  }, [searchContext.query])


  return (<>

    <TextField
      id={inputElementId}
      placeholder="Search variants"
      variant={variant.variant_id}
      value={inputQuery}
      onFocus={() => {
        if (_.isFunction(searchContext.onInputFocus)) {
          searchContext.onInputFocus();
        } else {
          console.log(searchContext.onInputFocus)
        }
      }}
      InputProps={{
        startAdornment: (
          <SearchIcon />
        )
      }}
      sx={{ width, marginLeft, ...sx }}
      onChange={(event) => {
        setInputQuery(event.target.value);
        searchContext.debounceUpdateSearch(event.target.value);
      }
      }

    />
  </>
  );
}
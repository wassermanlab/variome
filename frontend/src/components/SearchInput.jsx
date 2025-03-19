import React from 'react';
import { useState, useRef, useContext } from 'react';
import _ from 'lodash';

import { TextField, List, ListItem, ListItemText, Divider, Box } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { SearchContext } from './SearchProvider';

import {
  styled,
  useTheme
}
  from "@mui/material/styles";

import config from '../config.json';




export default function SearchInput({ width, marginLeft, inputElementId, variant, sx }) {

  const searchContext = useContext(SearchContext);

  return (<>

    <TextField
      id={inputElementId}
      placeholder="Search variants"
      variant={variant.variant_id}
      InputProps={{
        startAdornment: (
          <SearchIcon />
        )
      }}
      sx={{ width, marginLeft, ...sx }}
      onChange={(event) => {
        searchContext.debounceUpdateSearch(event.target.value)
      }
      }


    />

  </>
  );
}
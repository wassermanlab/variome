import React from 'react';
import _ from 'lodash';
import { useNavigate } from 'react-router-dom';

import Autocomplete from '@mui/material/Autocomplete';
import SearchIcon from '@mui/icons-material/Search';
import TextField from '@mui/material/TextField';

import Api from '../Api';
import config from '../config.json';

export default function Search(props) {
    const [results, setResults] = React.useState([])

    const navigate = useNavigate();
    const getData = async (searchTerm) => {
        const response = await Api.get("search",
            {
                "query": searchTerm
            });
        setResults(_.get(response, "variants", []));
    };

    const onInputChange = (event, value, reason) => {
        if (value) {
            getData(value);
        } else {
            setResults([]);
        }
    }

    const onChange = (event, value, reason) => {
        // TODO: Add error checking here
        if (value && value.id){
            navigate("/variant/" + value.id)
        }
    }

    return (
        <React.Fragment>
            <Autocomplete
                id="navbar-search"
                options={results}
                onInputChange={onInputChange}
                getOptionLabel={(option) => option.variant_id}
                onChange={onChange}
                renderInput={(params) => {
                    console.log(params)
                    return <TextField
                        {...params}
                        //label="Search variants"
                        placeholder="Search variants"
                        variant={props.variant.variant_id}
                        InputProps={{
                            ...params.InputProps,
                            startAdornment: (
                                <SearchIcon />
                            )
                        }}
                    />}
                }
                sx={{ width: props.width, marginLeft: props.marginLeft }}
            />
        </React.Fragment>
    );
}
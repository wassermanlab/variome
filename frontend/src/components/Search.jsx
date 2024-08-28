import React from 'react';
import {useState, useRef} from 'react';
import _ from 'lodash';
import { useNavigate } from 'react-router-dom';

import Autocomplete from '@mui/material/Autocomplete';
import SearchIcon from '@mui/icons-material/Search';
import TextField from '@mui/material/TextField';

import Api from '../Api';
import config from '../config.json';

const DEBOUNCE_DELAY = 800;

export default function Search({width, marginLeft, inputElementId, variant, sx}) {
    const [results, setResults] = useState([])
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const cancelledQueriesRef = useRef([]);
    const searchTimeoutRef = useRef(null);

    const navigate = useNavigate();
    const searchVariants = async (query) => {
        // logic for parsing and appending query type params could go here
        const response = await Api.get("search",
            {
                query:_.toUpper(query),
            });
        return _.get(response, "variants", []);
    };
    

    const onInputChange = (event, newQuery, reason) => {
        if (!_.isEmpty(newQuery)) {

            if (_.includes(cancelledQueriesRef.current, newQuery)) {
//                console.log("uncancel", newQuery);
                cancelledQueriesRef.current = [..._.without(cancelledQueriesRef.current, newQuery)];
            }
            if (searchTimeoutRef.current) {
                clearTimeout(searchTimeoutRef.current);
                cancelledQueriesRef.current = [...cancelledQueriesRef.current, query];
            } 

            setQuery(newQuery);
            setResults([]);
            setLoading(true);
            searchTimeoutRef.current = setTimeout(async () => {

                if (_.includes(cancelledQueriesRef.current, newQuery)) {
//                    console.log("cancelledQueries", cancelledQueriesRef.current);
//                    console.log("abort", newQuery);
                } else {
                    var variants = [];
                    try {
                        variants = await searchVariants(newQuery);
                    } catch (error) {
                        console.error(error);
                        setLoading(()=> false);
                    }

                    if (_.includes(cancelledQueriesRef.current, newQuery)) {
//                        console.log("(2) abort", newQuery);
                    } else {   
                        setResults(()=> variants);
                        cancelledQueriesRef.current = [];
                        setLoading(()=> false);
                    }
                }
                
            }, DEBOUNCE_DELAY);
        

        } else {
            setResults([]);
            setQuery("");
            cancelledQueriesRef.current = [];
            setLoading(()=> false);
//            console.log("set empty");
//            console.log("cancelledQueries", cancelledQueriesRef.current);
        }
    }

    const onChange = (event, value, reason) => {
        // TODO: Add error checking here
        if (value && value.id){
            navigate("/variant/" + value.id)
        }
    }

    return (
            <Autocomplete
                id={inputElementId}
                options={results}
                onInputChange={onInputChange}
                getOptionLabel={(option) => option.variant_id}
                onChange={onChange}
                loading={loading}
                loadingText="Searching..."
                noOptionsText = "No variants found"
                renderInput={(params) => {
                    return <TextField
                        {...params}
                        //label="Search variants"
                        placeholder="Search variants"
                        variant={variant.variant_id}
                        InputProps={{
                            ...params.InputProps,
                            startAdornment: (
                                <SearchIcon />
                            )
                        }}
                    />}
                }
                sx={{ width, marginLeft, ...sx }}
            />
    );
}
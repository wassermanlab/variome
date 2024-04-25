import React from 'react';
import _ from 'lodash';
import { useNavigate } from 'react-router-dom';

import Autocomplete from '@mui/material/Autocomplete';
import SearchIcon from '@mui/icons-material/Search';
import TextField from '@mui/material/TextField';

import Api from '../Api';
import config from '../config.json';

export default function Search(props) {
    const [options, setOptions] = React.useState([])

    const navigate = useNavigate();
    const getData = async (searchTerm) => {
        const response = await Api.get("search",
            {
                "variant_id": searchTerm
            });
        setOptions(_.get(response, "variants", []));
    };

    const onInputChange = (event, value, reason) => {
        if (value) {
            getData(value);
        } else {
            setOptions([]);
        }
    }

    const onChange = (event, value, reason) => {
        // TODO: Add error checking here
        if (value){
            navigate("/snv/" + value)
        }
    }

    const [assembly, setAssembly] = React.useState('');

    const handleChange = (event) => {
        setAssembly(event.target.value);
    };

    return (
        <React.Fragment>
            {/*}
            <Select value={assembly} onChange={handleChange} variant="standard" sx={{ width: "25%"}}>
                <MenuItem value="" disabled>Select Assembly</MenuItem>
                <MenuItem value="GRCh37 – SNV and Mt">GRCh37 – SNV and Mt</MenuItem>
                <MenuItem value="GRCh38 – SNV and Mt">GRCh38 – SNV and Mt</MenuItem> 
            </Select>*/}
            <Autocomplete
                id="navbar-search"
                options={options}
                onInputChange={onInputChange}
                onChange={onChange}
                renderInput={(params) =>
                    <TextField
                        {...params}
                        //label="Search variants"
                        placeholder="Search variants"
                        variant={props.variant}
                        InputProps={{
                            ...params.InputProps,
                            startAdornment: (
                                <SearchIcon />
                            )
                        }}
                    />
                }
                sx={{ width: props.width, marginLeft: props.marginLeft }}
            />
        </React.Fragment>
    );
}
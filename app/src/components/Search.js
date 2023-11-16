import React from 'react';

import Autocomplete from '@mui/material/Autocomplete';
import MenuItem from '@mui/material/MenuItem';
import InputAdornment from '@mui/material/InputAdornment';
import SearchIcon from '@mui/icons-material/Search';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';


export default function Search(props) {
    const [options, setOptions] = React.useState([])

    const getData = async(searchTerm) => {
        const data = {
            "variant_id": searchTerm
        }
        const response = await fetch("http://127.0.0.1:8000/api/search", {
            method: 'POST',
            body:JSON.stringify(data),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });
        const json = await response.json();
        setOptions(json["variants"]);
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
        window.location.href = "http://localhost:3000/snv/" + value
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
                sx={{ width: props.width, marginLeft: props.marginLeft}}
            />
        </React.Fragment>
    );
}
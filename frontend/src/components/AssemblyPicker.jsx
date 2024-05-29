import { 
    MenuItem, 
    Select 
} from "@mui/material";

import React, { useState } from "react";

export default function AssemblyPicker() {

    const [assembly, setAssembly] = useState("GRCh38");

    const handleChange = (event) => {
        setAssembly(event.target.value);
    };

    return (
        <Select
            value={assembly}
            onChange={handleChange}
            displayEmpty
            inputProps={{ "aria-label": "Select Assembly" }}
            style={{ color: "black", marginLeft: "20px" }}
        //variant="standard"
        >
            {/* TODO: Update the choices for this select once we add SV and Mt */}
            {/* TODO: Make this functional -- currently only one SNV assembly so it does nothing */}
            <MenuItem value="" disabled>
                Select Assembly
            </MenuItem>
            <MenuItem value="GRCh38">GRCh38</MenuItem>
            {/*<MenuItem value="GRCh38 – SV">GRCh38 – SV</MenuItem>*/}
        </Select>
    );
};
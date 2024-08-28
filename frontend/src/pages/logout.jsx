
import React from "react";
import _ from "lodash";
import {
    Button
} from "@mui/material";

import { useNavigate } from "react-router-dom";

import Link from "../components/Link";
import config from "../config";
import Api from "../Api";

export default function Logout({user, setUser}){
    const navigate = useNavigate();


    var logoutUrl = "";

    var urlObj = new URL("accounts/logout", config.backend_root);
    logoutUrl = urlObj.toString();

    return (
        <div>
            <h1>Logout</h1>
            <p>Are you sure you want to logout?</p>
            <Link reloadDocument to={logoutUrl} underline="none"><Button >Yes</Button></Link>
            <Link to="/" underline="none"><Button>No</Button></Link>
        </div>
    )
}

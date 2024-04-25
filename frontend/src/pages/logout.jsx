
import React from "react";
import _ from "lodash";
import {
    Button
} from "@mui/material";

import { useNavigate } from "react-router-dom";

import Link from "../components/Link";
import Api from "../Api";

export default function Logout({user, setUser}){
    const navigate = useNavigate();

    return (
        <div>
            <h1>Logout</h1>
            <p>Are you sure you want to logout?</p>
            <Button onClick={()=>{
                Api.post('accounts/logout/').then((response) => {
                    setUser(null);
                    navigate('/');
                });
            }}>Yes</Button>
            <Link to="/" underline="none"><Button>No</Button></Link>
        </div>
    )
}
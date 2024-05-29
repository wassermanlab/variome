
import React, { useState, useRef } from "react";

import _ from "lodash";

import { 
  styled, 
  useTheme } 
from "@mui/material/styles";

import {
  Box,
  IconButton,
  Typography,
  Toolbar,
  Menu,
  MenuItem,
  Button
} from "@mui/material";

import {
  Menu as MenuIcon,
  Info,
  Login,
  Person
} from "@mui/icons-material";

import Search from "./Search";
import AssemblyPicker from "./AssemblyPicker";
import Link from "./Link";

import config from "../config";

export default function VariomeToolbar({ user, setNavDrawerOpen, navDrawerOpen }) {


  const accountMenuAnchorEl = useRef(null);
  const [accountMenuOpen, setAccountMenuOpen] = React.useState(false);

  const closeAccountMenu = () => {
    setAccountMenuOpen(false);
  };

  const FlexBox = styled(Box)({
    display: "flex",
    alignItems: "center",
    gap: "16px"
  });

  const PlainLink = (props) => (
    <Link {...props} color="inherit" underline="none" />
  );

  var loginUrl = "";
  if (_.isString(_.get(import.meta, "env.VITE_LOGIN_PATH"))) {
    var urlObj = new URL(import.meta.env.VITE_LOGIN_PATH, config.backend_root);
    loginUrl = urlObj.toString();
  }


  return <Toolbar>
    <IconButton
      aria-label="open drawer"
      onClick={() => setNavDrawerOpen(true)}
      edge="start"
      sx={{ mr: 2, ...(navDrawerOpen && { display: "none" }) }}
    >
      <MenuIcon />
    </IconButton>
    <Typography
      variant="h6"
      noWrap
      component="div"
      sx={{ display: { xs: "none", sm: "block" } }}
    >
      <PlainLink to="/">He Kākano</PlainLink>
    </Typography>

    <FlexBox sx={{ flexGrow: "1" }}>
      {user && (
        <>
          <AssemblyPicker />
          <Search variant="standard" width="200px" />
        </>
      )}
    </FlexBox>
    <FlexBox>
      <FlexBox >

        {user && <>
          <Button id="account-menu-button"
            onClick={() => setAccountMenuOpen(true)}
            ref={accountMenuAnchorEl}
          >
            <Person sx={{ margin: '10px' }} />
            {user ? user.email : ""}
          </Button></>}


        {!user && <PlainLink to={loginUrl} >
          Login
        </PlainLink>}

        <Menu
          id="basic-menu"
          anchorEl={() => accountMenuAnchorEl.current}
          open={accountMenuOpen}
          onClose={closeAccountMenu}
          MenuListProps={{
            "aria-labelledby": "account-menu-button"
          }}
        >
          <PlainLink to="/profile" ><MenuItem onClick={closeAccountMenu} >Profile</MenuItem></PlainLink>
          <PlainLink to="/logout"><MenuItem onClick={closeAccountMenu}>Logout </MenuItem> </PlainLink>
        </Menu>

      </FlexBox>
    </FlexBox>
  </Toolbar>
}
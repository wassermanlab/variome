
import React, { useState, useRef, useContext } from "react";

import _ from "lodash";

import {
  styled,
  useTheme
}
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


import SearchInput from "./SearchInput";
import SearchResults from "./SearchResults";
import SearchProvider, { SearchContext } from "./SearchProvider";
import AssemblyPicker from "./AssemblyPicker";
import Link from "./Link";

import config from "../config";


export default function VariomeToolbar({ user, setNavDrawerOpen, navDrawerOpen, pageTitle }) {

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

  var urlObj = new URL("accounts/login", config.backend_root);
  loginUrl = urlObj.toString();

  return (
    <>
      <Toolbar sx={{ justifyContent: "start" }} >
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
          sx={{ display: { xs: "none", sm: "block", overflow: "visible" } }}
        >
          <PlainLink to="/">{pageTitle}</PlainLink>
        </Typography>

        <FlexBox sx={{ flexGrow: "1" }}>
          {user && (
            <>
              <AssemblyPicker sx={{ flexShrink: "2" }} />
              <SearchProvider>
                <SearchInput inputElementId="navigation-bar-search" variant="standard" sx={{ minWidth: "30vw" }} />
                <Box sx={{
                  display: "block",
                  position: "relative",
                  left: "0",
                  marginLeft: "-30vw",
                  top: "33px",
                  height: "auto",
                }} >
                  <SearchResults
                    overlay
                    sx={{
                      position: "absolute",
                      height: "auto",
                      width: "50vw",
                      maxHeight: "calc(100vh - 70px)",
                      overflowY: "scroll",
                    }}
                  />
                </Box>
              </SearchProvider>
            </>
          )}
        </FlexBox>

        <FlexBox sx={{ justifyContent: "end", flexGrow: "1" }}>

          {user && <>
            <Button id="account-menu-button"
              onClick={() => setAccountMenuOpen(true)}
              ref={accountMenuAnchorEl}
            >
              <Person sx={{ margin: '10px' }} />
              {user ? user.email : ""}
            </Button></>}


          {!user && <PlainLink reloadDocument to={loginUrl} >
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
      </Toolbar>

    </>);
}

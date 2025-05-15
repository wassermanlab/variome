import * as React from "react";

import _ from "lodash";
import { useEffect, useState } from "react";
import { styled, useTheme } from "@mui/material/styles";
import {
  Box,
  Drawer,
  CssBaseline,
  Toolbar,
  AppBar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemIcon,
  ListItemText,
  Select,
  MenuItem,
  Button,
  Menu
  //    InputBase,
  //    Button,
  //   Autocomplete,
  //    TextField
} from "@mui/material";

import {
  Article,
  Email,
  HelpCenter,
  Home as HomeIcon,
  Info,
  Menu as MenuIcon,
  ChevronLeft,
  ChevronRight,
  Star,
  Login,
  Person
} from "@mui/icons-material";

import Link from "./components/Link";
import VariomeToolbar from "./components/VariomeToolbar"

const drawerWidth = 240;
import {Content} from "./ContentParsing";

const Main = styled("main", { shouldForwardProp: (prop) => prop !== "open" })(
  ({ theme, open }) => ({
    maxWidth: "100vw", //
    overflow: "hidden",
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    }),
    marginLeft: `-${drawerWidth}px`,
    ...(open && {
      transition: theme.transitions.create("margin", {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen
      }),
      marginLeft: 0
    })
  })
);

const TopBar = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== "open"
})(({ theme, open }) => ({
  transition: theme.transitions.create(["margin", "width"], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen
    })
  })
}));

const DrawerHeader = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  padding: theme.spacing(0, 1),
  //paddingTop: "2%",
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: "flex-end"
}));

export default function AppLayoutWithNavigation({ user, children, pageTitle }) {
  const theme = useTheme();
  const [navDrawerOpen, setNavDrawerOpen] = React.useState(true);

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <TopBar
        position="fixed"
        open={navDrawerOpen}
        sx={(theme) => ({
          bgcolor: theme.palette.common.white,
          color: theme.palette.text.primary
        })}
      >
        <VariomeToolbar
          user={user}
          navDrawerOpen={navDrawerOpen}
          setNavDrawerOpen={setNavDrawerOpen}
          pageTitle={pageTitle}
        ></VariomeToolbar>
      </TopBar>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box"
          }
        }}
        variant="persistent"
        anchor="left"
        open={navDrawerOpen}
      >
        <DrawerHeader>
          <IconButton onClick={() => setNavDrawerOpen(false)}>
            {theme.direction === "ltr" ? <ChevronLeft /> : <ChevronRight />}
          </IconButton>
        </DrawerHeader>
        <Divider />
        <List>
          <Link to="/" color="inherit" underline="none">
            <ListItem button key="home">
              <ListItemIcon>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText primary="Home" />
            </ListItem>
          </Link>
          {Content.map((section) => (
            <Link
              key={section.name}
              to={`/${section.urlPath}`}
              color="inherit"
              underline="none"
            >
              <ListItem button>
                <ListItemIcon>
                  {<section.icon/>}
                </ListItemIcon>
                <ListItemText primary={section.name} />
              </ListItem>
            </Link>
          ))}
        </List>
      </Drawer>
      <Main open={navDrawerOpen}>
        <DrawerHeader />
        {children}
      </Main>
    </Box>
  );
}

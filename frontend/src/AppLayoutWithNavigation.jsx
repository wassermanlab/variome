import * as React from "react";
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
  Login,
  Person
} from "@mui/icons-material";

import Link from "./components/Link";
import { useState, useRef } from "react";

import config from "./config";
import Search from "./components/Search";

const drawerWidth = 240;

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

const AssemblyPicker = () => {
  const [assembly, setAssembly] = useState("");

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
      <MenuItem value="GRCh37 – SNV and Mt">GRCh37 – SNV and Mt</MenuItem>
      {/*<MenuItem value="GRCh37 – SV">GRCh37 – SV</MenuItem>*/}
      <MenuItem value="GRCh38 – SNV and Mt">GRCh38 – SNV and Mt</MenuItem>
      {/*<MenuItem value="GRCh38 – SV">GRCh38 – SV</MenuItem>*/}
    </Select>
  );
};

export default function AppLayoutWithNavigation({ user, children }) {
  const theme = useTheme();
  const [navDrawerOpen, setNavDrawerOpen] = React.useState(false);

  const accountMenuAnchorEl = useRef(null);
  const [accountMenuOpen, setAccountMenuOpen] = React.useState(false);

  const openAccountMenu = (event) => {
    console.log(event.currentTarget);
    setAccountMenuAnchorEl(event.currentTarget);
    setTimeout(() => {
      setAccountMenuOpen(true);
    }, 2000);
  };
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
        <Toolbar>
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

              { user && <Button id="account-menu-button"
                onClick={() => setAccountMenuOpen(true)}
                ref={accountMenuAnchorEl}
              >
                <Person sx={{margin:'10px'}}/>
                {user ? user.email : ""}
              </Button>}

              {!user && <PlainLink to={config.backend_root + "accounts/microsoft/login/?process=login"} >
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
          {/* BH TODO: Add Logo here */}
          <IconButton onClick={() => setNavDrawerOpen(false)}>
            {theme.direction === "ltr" ? <ChevronLeft /> : <ChevronRight />}
          </IconButton>
        </DrawerHeader>
        <Divider />
        <List>
          <Link href="/" color="inherit" underline="none">
            <ListItem button key="home">
              <ListItemIcon>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText primary="Home" />
            </ListItem>
          </Link>
          <Link href="/" color="inherit" underline="none">
            <ListItem button key="about">
              <ListItemIcon>
                <Info />
              </ListItemIcon>
              <ListItemText primary="About" />
            </ListItem>
          </Link>
          <Link href="/" color="inherit" underline="none">
            <ListItem button key="terms">
              <ListItemIcon>
                <Article />
              </ListItemIcon>
              <ListItemText primary="Terms of Use" />
            </ListItem>
          </Link>
          <Divider />
          <Link href="/" color="inherit" underline="none">
            <ListItem button key="faq">
              <ListItemIcon>
                <HelpCenter />
              </ListItemIcon>
              <ListItemText primary="FAQ" />
            </ListItem>
          </Link>
          <Link href="/" color="inherit" underline="none">
            <ListItem button key="contact">
              <ListItemIcon>
                <Email />
              </ListItemIcon>
              <ListItemText primary="Contact Us" />
            </ListItem>
          </Link>
        </List>
      </Drawer>
      <Main open={navDrawerOpen}>
        <DrawerHeader />
        {children}
      </Main>
    </Box>
  );
}

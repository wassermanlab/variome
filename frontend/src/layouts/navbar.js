import * as React from 'react';
import { Routes, Route } from 'react-router-dom'
import { styled, useTheme } from '@mui/material/styles';
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
    Link,
    ListItem,
    ListItemIcon,
    ListItemText,
    Select,
    MenuItem,
//    InputBase,
//    Button,
 //   Autocomplete,
//    TextField
} from '@mui/material';

import {
    Article,
    Email,
    HelpCenter,
    Home as HomeIcon,
    Info,
    Menu,
    ChevronLeft,
    ChevronRight,
    Login,
    Person,
} from '@mui/icons-material';

import { useState } from 'react';

import Home from '../pages/home';
import SNV from '../pages/snv';
import About from '../pages/about';
import TermsOfUse from '../pages/terms';
import FAQ from '../pages/faq';
import Contact from '../pages/contact';
import Profile from '../pages/profile';
import Search from '../components/Search';
import config from '../config.json';
const drawerWidth = 240;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
    ({ theme, open }) => ({
        flexGrow: 1,
        padding: theme.spacing(3),
        transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
        marginLeft: `-${drawerWidth}px`,
        ...(open && {
            transition: theme.transitions.create('margin', {
                easing: theme.transitions.easing.easeOut,
                duration: theme.transitions.duration.enteringScreen,
            }),
            marginLeft: 0,
        }),
    }),
);

const VariomeAppBar = styled(AppBar, {
    shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
    transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    ...(open && {
        width: `calc(100% - ${drawerWidth}px)`,
        marginLeft: `${drawerWidth}px`,
        transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen,
        }),
    }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(0, 1),
    //paddingTop: "2%",
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: 'flex-end',
}));

const DropdownMenu = () => {
    const [assembly, setAssembly] = useState('');

    const handleChange = (event) => {
        setAssembly(event.target.value);
    };

    return (
        <Select
            value={assembly}
            onChange={handleChange}
            displayEmpty
            inputProps={{ 'aria-label': 'Assembly' }}
            style={{ color: 'black', marginLeft: '20px' }}
        //variant="standard"
        >
            {/* TODO: Update the choices for this select once we add SV and Mt */}
            {/* TODO: Make this functional -- currently only one SNV assembly so it does nothing */}
            <MenuItem value="" disabled>Select Assembly</MenuItem>
            <MenuItem value="GRCh37 – SNV and Mt">GRCh37 – SNV and Mt</MenuItem>
            {/*<MenuItem value="GRCh37 – SV">GRCh37 – SV</MenuItem>*/}
            <MenuItem value="GRCh38 – SNV and Mt">GRCh38 – SNV and Mt</MenuItem>
            {/*<MenuItem value="GRCh38 – SV">GRCh38 – SV</MenuItem>*/}
        </Select>
    );
};


export default function AppNavBar() {
    const theme = useTheme();
    const [open, setOpen] = React.useState(false);

    const handleDrawerOpen = () => {
        setOpen(true);
    };
    const handleDrawerClose = () => {
        setOpen(false);
    };

    const handleScroll = () => {
        const windowHeight = window.innerHeight;
        const documentHeight = document.body.offsetHeight;
        const scrollPosition = window.scrollY || window.pageYOffset;

        if (documentHeight - windowHeight <= scrollPosition) {
            // Cannot read properties of null (reading 'style')
            //            document.getElementById('footer').style.display = 'block';
        } else {
            //           document.getElementById('footer').style.display = 'none';
        }
    };

    React.useEffect(() => {
        window.addEventListener('scroll', handleScroll);

        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);


    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <VariomeAppBar position="fixed" open={open} sx={(theme) => ({
                bgcolor: theme.palette.common.white
            })}>
                <Toolbar>
                    <IconButton
                        color="textPrimary"
                        aria-label="open drawer"
                        onClick={handleDrawerOpen}
                        edge="start"
                        sx={{ mr: 2, ...(open && { display: 'none' }) }}
                    >
                        <Menu />
                    </IconButton>
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        color="textPrimary"
                        sx={{ display: { xs: 'none', sm: 'block' } }}
                    >
                        <Link href="/" color="textPrimary" underline="none">He Kākano</Link>
                    </Typography>
                    <DropdownMenu />
                    <Search variant="standard" width="25%" marginLeft="20px" />
                </Toolbar>
            </VariomeAppBar>
            <Drawer
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    '& .MuiDrawer-paper': {
                        width: drawerWidth,
                        boxSizing: 'border-box',
                    },
                }}
                variant="persistent"
                anchor="left"
                open={open}
            >
                <DrawerHeader>
                    {/* BH TODO: Add Logo here */}
                    <IconButton onClick={handleDrawerClose}>
                        {theme.direction === 'ltr' ? <ChevronLeft /> : <ChevronRight />}
                    </IconButton>
                </DrawerHeader>
                <Divider />
                <List>
                    <Link href="/" color="inherit" underline="none">
                        <ListItem button key="home">
                            <ListItemIcon><HomeIcon /></ListItemIcon>
                            <ListItemText primary="Home" />
                        </ListItem>
                    </Link>
                    <Link href="/" color="inherit" underline="none">
                        <ListItem button key="about">
                            <ListItemIcon><Info /></ListItemIcon>
                            <ListItemText primary="About" />
                        </ListItem>
                    </Link>
                    <Link href="/" color="inherit" underline="none">
                        <ListItem button key="terms">
                            <ListItemIcon><Article /></ListItemIcon>
                            <ListItemText primary="Terms of Use" />
                        </ListItem>
                    </Link>
                    <Divider />
                    <Link href="/" color="inherit" underline="none">
                        <ListItem button key="faq">
                            <ListItemIcon><HelpCenter /></ListItemIcon>
                            <ListItemText primary="FAQ" />
                        </ListItem>
                    </Link>
                    <Link href="/" color="inherit" underline="none">
                        <ListItem button key="contact">
                            <ListItemIcon><Email /></ListItemIcon>
                            <ListItemText primary="Contact Us" />
                        </ListItem>
                    </Link>
                    <Link href={config.backend_root + "accounts/microsoft/login/?process=login"}>
                        <ListItem button key="login">
                            <ListItemIcon><Login /></ListItemIcon>
                            <ListItemText primary="Login" />
                        </ListItem> 
                    </Link>
                </List>
            </Drawer>
            <Main open={open}>
                <DrawerHeader />
                <Routes>
                    <Route path="/" exact element={<Home />} />
                    <Route path="/snv/:varId" loader={({ params }) => { }} action={({ params }) => { }} element={<SNV />} />
                    <Route path="/about" exact element={<About />} />
                    <Route path="/terms" exact element={<TermsOfUse />} />
                    <Route path="/faq" exact element={<FAQ />} />
                    <Route path="/contact" exact element={<Contact />} />
                    <Route path="/profile" exact element={<Profile />} />
                </Routes>

            </Main>


        </Box>


    );
}
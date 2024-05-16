import './App.css';
import theme from './styles/theme.js';

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import Login from './pages/login.js'
import Signup from './pages/register.js'
import Profile from './pages/profile.js'

import NavBar from './layouts/navbar.js';


function AppRouter () {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
            <Routes>
                {/* SQ TODO: Pages that do not use navbar (like login/signup) go below*/}
                {/*<Route path="/login" exact element={<Login/>}/>*/}
                <Route path="/*" element={ <NavBar/> }/>
                <Route path="/login" exact element={<Login/>}/>
                <Route path="/signup" exact element={<Signup/>}/>
                <Route path="/profile" exact element={<Profile/>}/>
            </Routes>
        </BrowserRouter>
      </ThemeProvider>
    )
}

export default AppRouter;
import './App.css';
import theme from './styles/theme';

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {BrowserRouter, Routes, Route} from 'react-router-dom';


import NavBar from './layouts/navbar';


function AppRouter () {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
            <Routes>
                {/* SQ TODO: Pages that do not use navbar (like login/signup) go below*/}
                {/*<Route path="/login" exact element={<Login/>}/>*/}
                <Route path="/*" element={ <NavBar/> }/>
            </Routes>
        </BrowserRouter>
      </ThemeProvider>
    )
}

export default AppRouter;
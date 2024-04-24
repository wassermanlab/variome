import './App.css';
import theme from './styles/theme.js';

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/login.js'
import Signup from './pages/register.js'
import Profile from './pages/profile.js'


import Home from './pages/home';
import SNV from './pages/snv';
import About from './pages/about';
import TermsOfUse from './pages/terms';
import FAQ from './pages/faq';
import Contact from './pages/contact';

import AppLayoutWithNavigation from './AppLayoutWithNavigation.js';
import { useEffect } from 'react';


function AppRouter() {

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          {/* SQ TODO: Pages that do not use navbar (like login/signup) go below*/}
          {/*<Route path="/login" exact element={<Login/>}/>*/}
          <Route path="/*" element={
            <AppLayoutWithNavigation >
              <Routes>
                <Route path="/" exact element={<Home />} />
                <Route path="/snv/:varId" loader={({ params }) => { }} action={({ params }) => { }} element={<SNV />} />
                <Route path="/about" exact element={<About />} />
                <Route path="/terms" exact element={<TermsOfUse />} />
                <Route path="/faq" exact element={<FAQ />} />
                <Route path="/contact" exact element={<Contact />} />
              </Routes>
            </AppLayoutWithNavigation>
          } />

          <Route path="/login" exact element={<Login />} />
          <Route path="/signup" exact element={<Signup />} />
          <Route path="/profile" exact element={<Profile />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default AppRouter;

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import _ from 'lodash';

import './App.css';
import theme from './styles/theme.js';
import Api from './Api.js';

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



function AppRouter() {
//  const [user, setUser] = useState({email:"asdf@example.com"});
const [user, setUser] = useState(null);

  useEffect(() => {
    Api.get('user',{json:true}).then((response) => {
      var user = _.get(response, 'user');
      if (_.isObject(user) && _.has(user, 'email') && user.email) {
        setUser(user);
      }
    });
  },[]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          {/* SQ TODO: Pages that do not use navbar (like login/signup) go below*/}
          {/*<Route path="/login" exact element={<Login/>}/>*/}
          <Route path="/*" element={
            <AppLayoutWithNavigation user={user}>
              <Routes>
                <Route path="/" exact element={<Home user={user}/>} />
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
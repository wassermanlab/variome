
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import _ from 'lodash';
import {Container, Box} from '@mui/material';

import theme from './styles/theme.jsx';
import Api from './Api.jsx';
import Profile from './pages/profile.jsx'
import Logout from './pages/logout.jsx'
import Home from './pages/home.jsx';
import Variant from './pages/variant.jsx';

import AppLayoutWithNavigation from './AppLayoutWithNavigation.jsx';
import {Content} from './ContentParsing.jsx';


function AppRouter() {
  //  const [user, setUser] = useState({email:"asdf@example.com"});
  const [user, setUser] = useState(null);
  const [settingsFetched, setSettingsFetched] = useState(false);
  const [pageTitle, setPageTitle] = useState(null);
  const [homePageMessage, setHomePageMessage] = useState(null);

  const [exampleSnv, setExampleSnv] = useState(null);
  const [exampleMt, setExampleMt] = useState(null);
  const [exampleSv, setExampleSv] = useState(null);

  useEffect(() => {
      if (!settingsFetched ){

          Api.get('settings').then((data) => {
              console.log(data);
              setExampleSnv(_.get(data,'settings.example_snv'));
              setPageTitle(_.get(data,'settings.site_title'));
              setHomePageMessage(_.get(data,'settings.home_page_message'));
              setSettingsFetched(true);
          });
      }
  
  },[_.isEmpty(exampleSnv) && _.isEmpty(pageTitle)]);

  useEffect(() => {
    Api.get('user', { json: true }).then((response) => {
      var user = _.get(response, 'user');
      if (_.isObject(user) && _.has(user, 'email') && user.email) {
        setUser(user);
      } else if (_.isObject(user) && !_.has(user, 'email') ) {
        console.log("found a logged in user, except there is no email address. Please set it to enable authenticating")
      }
    });
  }, []);

  function PageWithContent(content){
    return (
    <Container maxWidth="xl">
      <Box>
        {content}
      </Box>
    </Container>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/*" element={
            <AppLayoutWithNavigation user={user} pageTitle={pageTitle}>
              <Routes>
                <Route path="/" exact element={<Home user={user} pageTitle={pageTitle} setPageTitle={setPageTitle} examples={{snv:exampleSnv}} message={homePageMessage}/>} />
                {
                  Content.map(({name, urlPath, content}) => {
                    return (
                      <Route key={urlPath} path={`/${urlPath}`} element={PageWithContent(content)}/>
                    );
                  })
                }
                {user && <Route path="/variant/:varId" loader={({ params }) => { }} action={({ params }) => { }} element={<Variant pageTitle={pageTitle} />} />}
                {user && <Route path="/profile" element={<Profile user={user} />} />}
                {user && <Route path="/logout" element={<Logout user={user} setUser={setUser} />} />}
              </Routes>
            </AppLayoutWithNavigation>
          } />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default AppRouter;
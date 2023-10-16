import './App.css';

import {BrowserRouter, Routes, Route} from 'react-router-dom'

import Home from './pages/home'
import Dashboard from './pages/dashboard'


function AppRouter () {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" exact element={<Home/>}/>
        <Route path="/snv" exact element={<Dashboard/>}/>
      </Routes>
      
    </BrowserRouter>
  )
}

export default AppRouter;
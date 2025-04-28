import React from 'react';
import { StyledEngineProvider } from '@mui/material/styles';
import ReactDOM from 'react-dom/client';
import AppRouter from './AppRouter.jsx';
import "./styles/styles.css";


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <StyledEngineProvider injectFirst>
      <AppRouter />
    </StyledEngineProvider >
  </React.StrictMode>
);


if (import.meta.hot) {
  import.meta.hot.on("vite:beforeUpdate", () => {
      console.clear(); // Clears the console before each HMR update
  });
}
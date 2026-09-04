import React from 'react';
import { StyledEngineProvider } from '@mui/material/styles';
import ReactDOM from 'react-dom/client';
import AppRouter from './AppRouter.jsx';
import _ from 'lodash';
import "./styles/styles.css";


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <StyledEngineProvider injectFirst>
      <AppRouter />
    </StyledEngineProvider >
  </React.StrictMode>
);

let browserWasInactive = false;

let throttledNotify = _.debounce(() => {
    window.dispatchEvent(new window.CustomEvent("browserReactivated", { detail: {} }));
  }, 30000, { leading: true, trailing: false });

function markBrowserInactive() {
//  console.log("mbi");
  browserWasInactive = true;
}

function detectBrowserReactivation() {
  if (browserWasInactive && document.visibilityState === "visible" && document.hasFocus()) {
    browserWasInactive = false;
    throttledNotify()
  }
}

document.addEventListener("visibilitychange", () => {
//  console.log("visibilitychange", document.visibilityState);
  if (document.visibilityState === "hidden") {
    markBrowserInactive();
  } else {
    detectBrowserReactivation();
  }
});
window.addEventListener("blur", markBrowserInactive);
window.addEventListener("focus", detectBrowserReactivation);
window.addEventListener("pagehide", markBrowserInactive);
window.addEventListener("pageshow", detectBrowserReactivation);

if (import.meta.hot) {
  import.meta.hot.on("vite:beforeUpdate", () => {
      console.clear(); // Clears the console before each HMR update
  });
}
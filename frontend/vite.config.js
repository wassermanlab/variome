import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import _ from 'lodash'
import path from 'path'

// add env variables here if you want to expose them to the frontend code 
// map values are defaults
// ( see https://vite.dev/guide/env-and-mode )
//  do not add sensitive data here, as this will be exposed to the frontend code
const envVariableDefaults = {
  BACKEND_ROOT:"http://localhost:8000/",
  ENVIRONMENT: 'production',
  FRONTEND_PORT: 3000,
  BVL_TITLE: 'A Variome BVL',
  API_PATH: '/api/',
  LOGIN_PATH: '/admin/login',
  LOGOUT_PATH: '/admin/logout'
};

var envs = loadEnv('', '..', _.keys(envVariableDefaults));

//const IS_DEVELOPMENT = envs.ENVIRONMENT === 'development';

_.defaults(envs, envVariableDefaults);

var define = _.mapKeys(envs, (value, key) => {
  return `import.meta.env.${key}`;
});

define = _.mapValues(define, (value, key) => {
  return JSON.stringify(value);
});

console.log("these env vars are available in the frontend code:", define);

// https://vitejs.dev/config/

export default defineConfig({
  //  envDir: '/Users/brad/variome-community-version/frontend/public/favicon',
  server: {
    port: envs.FRONTEND_PORT * 1,
  },
  plugins: [react()],
  define
});

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import _ from 'lodash'
import dotenv from 'dotenv'
import path from 'path'

// add env variables here if you want to expose them to the frontend code 
// ( see https://vite.dev/guide/env-and-mode )
const envVariablestoExpose = `
BVL_TITLE
LOGIN_PATH
LOGOUT_PATH
`.split('\n');

dotenv.config({ path: path.resolve(__dirname, '../.env') })


const IS_DEVELOPMENT = process.env.ENVIRONMENT === 'development'

_.defaults(process.env,{
  LOGIN_PATH: IS_DEVELOPMENT ? '/admin/login' : '/oauth2/login',
  LOGOUT_PATH: IS_DEVELOPMENT ? '/admin/logout' : '/oauth2/logout',
  BVL_TITLE: 'A Variome BVL'
});


var exposedEnvVariables = {};
_.each(envVariablestoExpose, (envVar) => {
  if (process.env[envVar]) {
    exposedEnvVariables[`import.meta.env.${envVar}`] = JSON.stringify(process.env[envVar]);
  }
});

// https://vitejs.dev/config/
export default defineConfig({
  server:{
    port: process.env.FRONTEND_PORT * 1,
  },
  plugins: [
    react()
  ]

})

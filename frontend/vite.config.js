import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import _ from 'lodash'
import dotenv from 'dotenv'
import path from 'path'

dotenv.config({ path: path.resolve(__dirname, '../.env') })

_.defaults(process.env, {
  VITE_LOGIN_PATH:'/accounts/microsoft/login/'
});

// https://vitejs.dev/config/
export default defineConfig({
  server:{
    port: 3000,
  },
  plugins: [react()],
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import _ from 'lodash'
import dotenv from 'dotenv'
import path from 'path'

dotenv.config({ path: path.resolve(__dirname, '../.env') })

const IS_DEVELOPMENT = process.env.ENVIRONMENT === 'development'

if (IS_DEVELOPMENT) {
  
  _.defaults(process.env, {
    VITE_LOGIN_PATH:'/admin/login',
    VITE_LOGOUT_PATH:'/admin/logout'
  });

} else {
  _.defaults(process.env, {
    VITE_LOGIN_PATH:'/oauth2/login',
    VITE_LOGOUT_PATH:'/oauth2/logout'
  });

}

// https://vitejs.dev/config/
export default defineConfig({
  server:{
    port: 3000,
  },
  plugins: [react()],
})

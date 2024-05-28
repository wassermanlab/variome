import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

import dotenv from 'dotenv'
import path from 'path'

dotenv.config({ path: path.resolve(__dirname, '../.env') })
// https://vitejs.dev/config/
export default defineConfig({
  server:{
    port: 3000,
  },
  plugins: [react()],
})

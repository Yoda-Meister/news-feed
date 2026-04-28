import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Set base to '/{repo-name}/' when deploying to GitHub Pages
// (e.g. '/beehiiv-dashboard/'). Use '/' if you have a custom domain
// or if this repo is your user/org site (username.github.io).
const base = process.env.VITE_BASE_PATH ?? '/'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base,
})

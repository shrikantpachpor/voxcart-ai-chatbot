import { defineConfig } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: 'src',
  envDir: __dirname,
  server: {
    port: 3000,
  },
  build: {
    outDir: '../dist',
    sourcemap: false,
  },
  esbuild: {
    jsx: 'automatic',
  },
  optimizeDeps: {
    esbuildOptions: {
      sourcemap: false,
      jsx: 'automatic',
    },
  },
});

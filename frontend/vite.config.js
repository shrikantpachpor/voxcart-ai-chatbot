import { defineConfig } from 'vite';
export default defineConfig({
  root: 'src',
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

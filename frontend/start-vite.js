#!/usr/bin/env node
const { spawn } = require('child_process');

const vite = spawn('vite', [], {
  cwd: process.cwd(),
  stdio: 'inherit',
  shell: true,
});

vite.on('error', (err) => {
  console.error('Failed to start vite:', err);
  process.exit(1);
});

vite.on('exit', (code) => {
  process.exit(code || 0);
});

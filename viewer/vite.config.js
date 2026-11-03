import { defineConfig } from 'vite';

export default defineConfig({ optimizeDeps: { include: ['b44ui'], extensions: ['.tsx'] } });

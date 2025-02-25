import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import vuetify from 'vite-plugin-vuetify';
import path from 'path';
import markdown from 'vite-plugin-markdown';

export default defineConfig({
  plugins: [
    vue({
      include: [/\.vue$/, /\.md$/] // Разрешаем обработку .md файлов как компонентов
    }),
    markdown(),
    vuetify({
      autoImport: true,
    }),
  ],
  define: { 'process.env': {} },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
      },
    },
  },
});
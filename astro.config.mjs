// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  integrations: [tailwind()],
  redirects: {
    '/en/kategori/gocmaksan': '/en/kategori/rebar',
    '/ru/kategori/gocmaksan': '/ru/kategori/rebar',
    '/bg/kategori/gocmaksan': '/bg/kategori/rebar',
  },
  vite: {
    server: {
      fs: {
        // Junction ile .BUILD_CACHE'e bagli node_modules'e izin ver
        allow: [
          'C:/Users/Kenan/Desktop/AI/Jaguar-ltd',
          'C:/YAZILIM_KASASI/.BUILD_CACHE/Jaguar-ltd/node_modules',
          'C:/Users/Kenan/Desktop/.BUILD_CACHE/Jaguar-ltd/node_modules',
        ]
      }
    }
  }
});

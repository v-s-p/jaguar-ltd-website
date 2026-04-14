/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#001a4d',    // Koyu lacivert
          light: '#0b162c',   // Daha koyu ton
          accent: '#ffcc00',  // Orijinal sitedeki sarı vurgu
          gray: '#f8f9fa',    // Kart arka planları için açık gri
        }
      },
      fontFamily: {
        sans: ['"Segoe UI"', 'Tahoma', 'Geneva', 'Verdana', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
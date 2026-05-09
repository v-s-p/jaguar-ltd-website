/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#004d54',      // Koyu turkuaz (header/footer bg)
          light: '#003a40',     // Daha koyu ton
          accent: '#00A8B5',    // Ana turkuaz vurgu
          hover: '#008c96',     // Hover durumu
          gray: '#f8f9fa',      // Kart arka planları
          warm: '#f0fafa',      // Açık turkuaz arka plan
        }
      },
      fontFamily: {
        sans: ['"Segoe UI"', 'Tahoma', 'Geneva', 'Verdana', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

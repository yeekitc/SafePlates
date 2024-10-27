/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    colors: {
      ...colors,
      'beige': '#F5F5EE',
      'yorange': '#F46527',
    },
    extend: {},
  },
  plugins: [],
}
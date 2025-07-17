// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './public/index.html',        // HTML 入口
    './src/**/*.{js,jsx,ts,tsx}', // 全部 JSX/TSX
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

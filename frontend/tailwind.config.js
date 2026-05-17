/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 24px 60px rgba(15, 23, 42, 0.45)",
      },
    },
  },
  plugins: [],
};

import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1E3A8A",
        accent: "#059669",
        background: "#F8FAFC",
        slateText: "#0F172A",
        warning: "#F59E0B",
        danger: "#DC2626"
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem"
      },
      boxShadow: {
        soft: "0 10px 30px -12px rgba(15, 23, 42, 0.18)"
      }
    }
  },
  plugins: [],
};

export default config;


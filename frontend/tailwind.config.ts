import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#050505",
        foreground: "#eaeaea",
        accent: {
          DEFAULT: "#00ff9d", // Neon Green
          glow: "rgba(0, 255, 157, 0.5)",
          hover: "#00cc7d"
        },
        panel: {
          DEFAULT: "#111111",
          border: "#333333"
        }
      },
      fontFamily: {
        mono: ['var(--font-geist-mono)'],
        sans: ['var(--font-geist-sans)'],
      }
    },
  },
  plugins: [],
};
export default config;

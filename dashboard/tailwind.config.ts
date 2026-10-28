/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
 * ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
 * ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
 * ║                                                                  ║
 * ║           © 2026 CodeX Devs — All Rights Reserved               ║
 * ║                                                                  ║
 * ║   discord  ──  https://discord.gg/codexdev                      ║
 * ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
 * ║   github   ──  https://github.com/RayExo                        ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: { DEFAULT: "#f47b30", hover: "#dc6317", glow: "rgba(244, 123, 48, 0.5)" },
        secondary: { DEFAULT: "#150c06", light: "#211812" },
        accent: { red: "rgba(244, 123, 48, 0.1)", glass: "rgba(255, 237, 214, 0.03)" },
        lime: { DEFAULT: "#d6de3a", soft: "#a9b02a" },
        red: {
          50: "#fff3ea", 100: "#ffe2cc", 200: "#ffc29a", 300: "#ff9d65", 400: "#fb8a4a",
          500: "#f47b30", 600: "#dc6317", 700: "#b44c12", 800: "#8a3a12", 900: "#5f2810", 950: "#34150a",
        },
        slate: {
          50: "#fbf6f0", 100: "#f4ebe0", 200: "#e7d8c6", 300: "#cdb8a0", 400: "#a89280",
          500: "#85705f", 600: "#624f41", 700: "#46372d", 800: "#30241c", 900: "#211812", 950: "#150c06",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        outfit: ["var(--font-outfit)", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;

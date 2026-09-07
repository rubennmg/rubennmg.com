/** @type {import('tailwindcss').Config} */
export default {
    content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
    theme: {
        colors: {
            white: "#ffffff",
            "df-text": "rgb(var(--text) / <alpha-value>)",
            background: "rgb(var(--background) / <alpha-value>)",
            bodyback: "rgb(var(--bodyback) / <alpha-value>)",
            navbar: "rgb(var(--bodyback) / <alpha-value>)",
            primary: "rgb(var(--text) / <alpha-value>)",
            secondary: "rgb(var(--border) / <alpha-value>)",
            accent: "rgb(var(--accent) / <alpha-value>)",
            "accent-soft": "rgb(var(--accent-soft) / <alpha-value>)",
            border: "rgb(var(--border) / <alpha-value>)",
            softblue: "rgb(var(--text-soft) / <alpha-value>)",
            textsoft: "rgb(var(--text-soft) / <alpha-value>)",
            labelbg: "#2d2d2d",
            txYellow: "#d4d4d8",
        },
    },
    plugins: [],
};

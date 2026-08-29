/** @type {import('tailwind.config.js').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        netacad: {
          navy: '#002C54',
          darkNavy: '#001A33',
          deepBlue: '#005073',
          blue: '#007AA6',
          sky: '#00BCEB',
          cyan: '#049FD9',
          green: '#6CC24A', // Iconic Cisco NetAcad green
          emerald: '#10B981',
          bg: '#F4F6F8',
          card: '#FFFFFF',
          border: '#DCE4EC',
          darkBg: '#09131F',
          darkCard: '#0F1E2E',
          darkBorder: '#1A334E',
          darkHover: '#162C46',
        },
        cisco: {
          bridge: '#007AA6',
          sky: '#00BCEB',
          blue: '#005073',
          dark: '#09131F',
          navy: '#002C54',
          surface: '#0F1E2E',
          card: '#0F1E2E',
          border: '#DCE4EC',
          green: '#6CC24A',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'netacad-card': '0 2px 8px -1px rgba(0, 44, 84, 0.08), 0 1px 3px -1px rgba(0, 44, 84, 0.05)',
        'netacad-hover': '0 10px 20px -3px rgba(0, 44, 84, 0.12), 0 4px 8px -2px rgba(0, 44, 84, 0.08)',
        'netacad-glow': '0 0 15px -3px rgba(0, 188, 235, 0.35)',
      },
    },
  },
  plugins: [],
}

/** Tailwind config for Perpustakaan Hati
 *  Tokens source: docs/brand/design-tokens.css
 *  Rationale:     docs/brand/visual-identity.md
 *  Copy into apps/web after Next.js scaffold (Phase 3).
 */
const brandColors = {
  ink: { DEFAULT: '#0a0a0c', soft: '#17171a' },
  gold: { DEFAULT: '#c9a86a', light: '#e9cea2', deep: '#a07b45' },
  sepia: { DEFAULT: '#573a2f', deep: '#3a2a21' },
  burgundy: { DEFAULT: '#5c1e17', deep: '#3f1711', light: '#c25a58' },
  terracotta: { DEFAULT: '#da725b', soft: '#e69677' },
  cream: '#fdfee6',
  paper: '#f4efe6',
  green: {
    DEFAULT: '#5b9b7d',
    light: '#8fc9a8',
    mid: '#3f7d5e',
    deep: '#255740',
    ink: '#173c2c',
    wash: '#d9efe1',
  },
};

module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: brandColors,
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        reading: ['Source Serif 4', 'Georgia', 'serif'],
      },
      borderRadius: { sm: '2px', md: '4px', lg: '8px' },
      boxShadow: {
        card: '0 1px 2px rgb(0 0 0 / 0.4), 0 8px 24px rgb(0 0 0 / 0.28)',
        lift: '0 2px 4px rgb(0 0 0 / 0.5), 0 16px 48px rgb(0 0 0 / 0.4)',
      },
      letterSpacing: {
        kicker: '0.18em',
        wordmark: '0.22em',
      },
      transitionTimingFunction: { sanctuary: 'cubic-bezier(0.16, 1, 0.3, 1)' },
      keyframes: {
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: { 'fade-up': 'fade-up 240ms cubic-bezier(0.16, 1, 0.3, 1) both' },
    },
  },
  plugins: [],
};

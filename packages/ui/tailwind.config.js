/** Tailwind config for Perpustakaan Hati
 *  Tokens source: docs/brand/design-tokens.css
 *  Rationale:     docs/brand/visual-identity.md
 *  Copy into apps/web after Next.js scaffold (Phase 3).
 */
const brandColors = {
  ink: {
    DEFAULT: '#0a0a0c',
    raised: '#121416',
    soft: '#17171a',
    elevated: '#202226',
  },
  gold: { DEFAULT: '#c9a86a', light: '#e9cea2', deep: '#a07b45' },
  sepia: { DEFAULT: '#573a2f', deep: '#3a2a21' },
  burgundy: { DEFAULT: '#5c1e17', deep: '#3f1711', light: '#c25a58' },
  terracotta: { DEFAULT: '#da725b', soft: '#e69677' },
  cream: '#fdfee6',
  paper: '#f4efe6',
  linen: '#eae2d4',
  // "Living Green" ramp — role-specific, see visual-identity.md
  green: {
    950: '#0b2418',
    900: '#123d2a',
    800: '#1d5a3d',
    700: '#2d7954',
    600: '#3f9167',
    500: '#5b9b7d',
    400: '#7db895',
    300: '#a7d3b6',
    200: '#cbe8d5',
    100: '#e4f4e9',
    DEFAULT: '#5b9b7d',
    light: '#7db895',
    mid: '#2d7954',
    deep: '#1d5a3d',
    ink: '#123d2a',
    wash: '#e4f4e9',
  },
  lime: { glow: '#c8e986' },
  mint: { glass: '#9de1c1' },
};

const brandShadows = {
  'depth-0': 'none',
  'depth-1':
    'inset 0 1px 0 rgb(255 255 255 / 0.05), 0 8px 24px rgb(0 0 0 / 0.24)',
  'depth-2':
    'inset 0 1px 0 rgb(255 255 255 / 0.06), 0 18px 50px rgb(0 0 0 / 0.34)',
  'depth-3':
    'inset 0 1px 0 rgb(255 255 255 / 0.08), 0 32px 80px rgb(0 0 0 / 0.42)',
  extrude: '0 3px 0 rgb(18 61 42 / 0.8), 0 32px 80px rgb(0 0 0 / 0.42)',
  card: '0 1px 2px rgb(0 0 0 / 0.4), 0 8px 24px rgb(0 0 0 / 0.28)',
  lift: '0 2px 4px rgb(0 0 0 / 0.5), 0 16px 48px rgb(0 0 0 / 0.4)',
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
      borderRadius: { sm: '2px', md: '4px', lg: '8px', pill: '999px' },
      boxShadow: brandShadows,
      letterSpacing: {
        kicker: '0.18em',
        wordmark: '0.22em',
      },
      transitionTimingFunction: { sanctuary: 'cubic-bezier(0.16, 1, 0.3, 1)' },
      backgroundImage: {
        // primary CTA fill — the healing green, measured 5.14:1 with ink label
        'green-cta': 'linear-gradient(135deg, #3f9167, #5b9b7d)',
        'green-cta-hover': 'linear-gradient(135deg, #2d7954, #4d9573)',
        // deep brand ground for 3D panels
        'green-deep': 'linear-gradient(160deg, #123d2a, #0b2418)',
      },
      keyframes: {
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        // healing progress — a travelling glow, never a spinner
        'heal-travel': {
          from: { transform: 'translateX(-100%)' },
          to: { transform: 'translateX(400%)' },
        },
      },
      animation: {
        'fade-up': 'fade-up 240ms cubic-bezier(0.16, 1, 0.3, 1) both',
        'heal-travel': 'heal-travel 2.4s cubic-bezier(0.16, 1, 0.3, 1) infinite',
      },
    },
  },
  plugins: [],
};

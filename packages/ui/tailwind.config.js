/** Tailwind config for Perpustakaan Hati
 *  Tokens source: docs/brand/design-tokens.css
 *  Rationale:     docs/brand/visual-identity.md
 *  Copy into apps/web after Next.js scaffold (Phase 3).
 */
const brandColors = {
  // v3 "Gilded Grove" grounds — green-black, the default dark ground
  forest: {
    night: '#07140d',
    raised: '#0d2117',
    soft: '#142c20',
    edge: 'rgb(157 225 193 / 0.14)',
    DEFAULT: '#07140d',
  },
  heart: { ruby: '#c8343c', 'ruby-deep': '#7d1a22' }, // emblem only, never text
  lantern: '#f2b85c', // glow cores only
  // text on dark grounds (design-tokens.css --text-on-dark / --text-muted-on-dark)
  'on-dark': { DEFAULT: '#e6e2da', muted: '#a49c8d' },
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
  // Charts & data-viz (locked 2026-11-08)
  chart: {
    1: '#5b9b7d',
    2: '#c9a86a',
    3: '#c25a58',
    4: '#f2b85c',
    5: '#9de1c1',
    track: '#142c20',
  },
  // Teman Hati companion
  companion: {
    bg: '#07140d',
    assistant: '#0d2117',
    user: '#5b9b7d',
  },
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
  'card-v3':
    'inset 0 1px 0 rgb(167 211 182 / 0.08), 0 24px 60px rgb(0 0 0 / 0.5), 0 0 0 1px rgb(201 168 106 / 0.10)',
  'cta-v3': '0 0 0 1px rgb(200 233 134 / 0.35), 0 10px 30px rgb(63 145 103 / 0.45)',
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
      // weights per role — fonts are variable 400-700 (build-fonts.py);
      // these match the SVG outline weights in build-logos.py
      fontWeight: { display: '560', hero: '660', title: '520', label: '600', byline: '500' },
      borderRadius: { sm: '2px', md: '4px', lg: '8px', pill: '999px' },
      boxShadow: brandShadows,
      letterSpacing: {
        kicker: '0.18em',
        wordmark: '0.22em',
        display: '0.06em',
        flank: '0.32em',
      },
      transitionTimingFunction: { sanctuary: 'cubic-bezier(0.16, 1, 0.3, 1)' },
      zIndex: { sticky: '30', header: '40', overlay: '50', sheet: '60', toast: '70' },
      minHeight: { tap: '44px', 'cta-mobile': '56px' },
      minWidth: { tap: '44px' },
      maxWidth: { reading: '640px', chat: '760px', grid: '1200px' },
      backgroundImage: {
        // primary CTA fill — the healing green, measured 5.14:1 with ink label
        'green-cta': 'linear-gradient(135deg, #3f9167, #5b9b7d)',
        'green-cta-hover': 'linear-gradient(135deg, #2d7954, #4d9573)',
        // deep brand ground for 3D panels
        'green-deep': 'linear-gradient(160deg, #123d2a, #0b2418)',
        // v3 foils — display type only (>= 32px), pair with bg-clip-text
        'foil-emerald':
          'linear-gradient(178deg, #d9f3df 0%, #8fd0a6 22%, #3f9167 46%, #2d7954 58%, #a7d3b6 76%, #3f9167 100%)',
        'foil-gold':
          'linear-gradient(178deg, #fff1c9 0%, #ecc983 24%, #b8904a 48%, #9a7638 58%, #f1d79b 78%, #b8904a 100%)',
        // v3 CTA — forest-night label measured 5.77:1 on green-500
        'cta-v3': 'linear-gradient(180deg, #7db895, #5b9b7d 50%, #3f9167)',
        'glow-emerald': 'radial-gradient(70% 60% at 50% 40%, rgb(63 145 103 / 0.42), transparent 72%)',
        'glow-lantern': 'radial-gradient(60% 50% at 50% 38%, rgb(242 184 92 / 0.30), transparent 70%)',
        vignette: 'radial-gradient(120% 90% at 50% 45%, transparent 48%, rgb(0 0 0 / 0.72) 100%)',
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

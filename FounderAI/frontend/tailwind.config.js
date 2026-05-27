/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        ink: {
          DEFAULT: '#0B1437',
          soft: '#1B2453',
        },
        brand: {
          50:  '#EEF1FF',
          100: '#E0E6FF',
          200: '#C2CCFF',
          300: '#94A2FF',
          400: '#6B78F2',
          500: '#4F46E5',
          600: '#4338CA',
          700: '#3730A3',
          800: '#2A2580',
          900: '#1E1B4B',
        },
        gold: {
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
        },
      },
      boxShadow: {
        'glow-brand': '0 10px 40px -10px rgba(79, 70, 229, 0.45)',
        'glow-gold': '0 10px 30px -10px rgba(245, 158, 11, 0.4)',
        'lift': '0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px -8px rgba(15, 23, 42, 0.08)',
      },
      keyframes: {
        'blob': {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%':      { transform: 'translate(30px, -40px) scale(1.08)' },
          '66%':      { transform: 'translate(-25px, 25px) scale(0.95)' },
        },
        'fade-up': {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'shimmer': {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'blob-slow':  'blob 14s ease-in-out infinite',
        'blob-slower':'blob 18s ease-in-out infinite',
        'fade-up':    'fade-up 0.4s ease-out both',
        'shimmer':    'shimmer 2.5s linear infinite',
      },
      backgroundImage: {
        'blueprint-grid':
          "linear-gradient(to right, rgba(79,70,229,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(79,70,229,0.08) 1px, transparent 1px)",
        'brand-gradient':
          'linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #4338CA 100%)',
        'gold-gradient':
          'linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%)',
      },
      backgroundSize: {
        'grid-md': '36px 36px',
      },
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ios: {
          blue: '#007AFF',
          'blue-dark': '#0A84FF',
          indigo: '#5856D6',
          'indigo-dark': '#5E5CE6',
          purple: '#AF52DE',
          'purple-dark': '#BF5AF2',
          pink: '#FF2D55',
          'pink-dark': '#FF375F',
          red: '#FF3B30',
          'red-dark': '#FF453A',
          orange: '#FF9500',
          'orange-dark': '#FF9F0A',
          yellow: '#FFCC00',
          'yellow-dark': '#FFD60A',
          green: '#34C759',
          'green-dark': '#30D158',
          mint: '#00C7BE',
          'mint-dark': '#63E6E2',
          teal: '#30B0C7',
          'teal-dark': '#40C8E0',
          cyan: '#32ADE6',
          'cyan-dark': '#64D2FF',
          bg: {
            light: '#F2F2F7',
            dark: '#000000',
          },
          card: {
            light: 'rgba(255, 255, 255, 0.85)',
            dark: 'rgba(28, 28, 30, 0.85)',
            solidLight: '#FFFFFF',
            solidDark: '#1C1C1E',
          },
          secondary: {
            light: '#E5E5EA',
            dark: '#2C2C2E',
          },
          tertiary: {
            light: '#D1D1D6',
            dark: '#3A3A3C',
          },
          quaternary: {
            light: '#C7C7CC',
            dark: '#48484A',
          },
          separator: {
            light: 'rgba(60, 60, 67, 0.12)',
            dark: 'rgba(84, 84, 88, 0.35)',
          }
        },
        navy: {
          950: '#030712',
          900: '#0B1120',
          800: '#151F38',
          700: '#1E293B',
          600: '#334155',
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"SF Pro Text"', '"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        mono: ['"SF Mono"', '"JetBrains Mono"', 'Menlo', 'Consolas', 'monospace'],
      },
      borderRadius: {
        'ios': '14px',
        'ios-lg': '18px',
        'ios-xl': '24px',
        'ios-2xl': '32px',
        'ios-squircle': '22%',
      },
      boxShadow: {
        'ios-sm': '0 2px 8px -1px rgba(0, 0, 0, 0.08), 0 1px 3px -1px rgba(0, 0, 0, 0.04)',
        'ios-md': '0 10px 30px -10px rgba(0, 0, 0, 0.12), 0 4px 10px -2px rgba(0, 0, 0, 0.04)',
        'ios-lg': '0 20px 40px -15px rgba(0, 0, 0, 0.25), 0 8px 16px -4px rgba(0, 0, 0, 0.08)',
        'ios-glow': '0 0 35px -5px rgba(0, 122, 255, 0.35)',
        'ios-glass': '0 8px 32px 0 rgba(0, 0, 0, 0.08), inset 0 1px 0 0 rgba(255, 255, 255, 0.15)',
        'ios-card': '0 4px 20px -2px rgba(0, 0, 0, 0.06), 0 0 1px 1px rgba(0, 0, 0, 0.04)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
        'fade-in': 'fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'spring-up': 'springUp 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'scale(0.98)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        springUp: {
          '0%': { opacity: '0', transform: 'translateY(12px) scale(0.96)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        }
      }
    },
  },
  plugins: [],
}

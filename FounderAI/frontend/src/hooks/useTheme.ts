import { useEffect, useState } from 'react'

export type Theme = 'light' | 'dark'

const KEY = 'founderai.theme'

function prefersDark(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

function initial(): Theme {
  if (typeof window === 'undefined') return 'light'
  const stored = window.localStorage.getItem(KEY) as Theme | null
  if (stored === 'light' || stored === 'dark') return stored
  return prefersDark() ? 'dark' : 'light'
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(initial)

  useEffect(() => {
    const el = document.documentElement
    el.classList.toggle('dark', theme === 'dark')
    try {
      window.localStorage.setItem(KEY, theme)
    } catch {
      /* ignore */
    }
  }, [theme])

  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => {
      // Only follow system if user hasn't explicitly chosen.
      if (!window.localStorage.getItem(KEY)) setTheme(e.matches ? 'dark' : 'light')
    }
    mq.addEventListener?.('change', handler)
    return () => mq.removeEventListener?.('change', handler)
  }, [])

  return {
    theme,
    toggle: () => setTheme(t => (t === 'dark' ? 'light' : 'dark')),
  }
}

export function useLanguageDir(language: string | null | undefined) {
  useEffect(() => {
    const el = document.documentElement
    if (language === 'he') {
      el.setAttribute('dir', 'rtl')
      el.setAttribute('lang', 'he')
    } else {
      el.setAttribute('dir', 'ltr')
      el.setAttribute('lang', 'en')
    }
  }, [language])
}

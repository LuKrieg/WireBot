import { useEffect, useState } from 'react'

export const WIREBOT_THEME_KEY = 'wirebot-theme'

function readInitialTheme() {
  const saved = window.localStorage.getItem(WIREBOT_THEME_KEY)
  if (saved === 'dark' || saved === 'light') {
    return saved
  }
  return 'dark'
}

export function useWireBotTheme() {
  const [theme, setTheme] = useState(readInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    window.localStorage.setItem(WIREBOT_THEME_KEY, theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'))
  }

  return { theme, setTheme, toggleTheme }
}

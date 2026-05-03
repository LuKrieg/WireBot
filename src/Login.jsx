import { useEffect, useState } from 'react'
import './App.css'

const STORAGE_KEY = 'wirebot-theme'

function getInitialTheme() {
  const savedTheme = window.localStorage.getItem(STORAGE_KEY)

  if (savedTheme === 'dark' || savedTheme === 'light') {
    return savedTheme
  }

  return 'dark'
}

export default function Login({ onSuccess }) {
  const [theme, setTheme] = useState(getInitialTheme)
  const [username, setUsername] = useState('')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'))
  }

  const handleAcceder = () => {
    onSuccess?.(username.trim())
  }

  return (
    <main className="login-screen">
      <button
        type="button"
        className="icon-button login-theme-toggle"
        onClick={toggleTheme}
        aria-label="Cambiar tema"
      >
        <img src="/brightness_medium.png" alt="" aria-hidden="true" />
      </button>

      <section className="login-card">
        <img src="/logo.png" alt="WireBot" className="login-logo" />

        <input
          type="text"
          className="login-username-input"
          placeholder="Ingresa tu usuario"
          aria-label="Usuario"
          autoComplete="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />

        <button type="button" className="login-submit-button" onClick={handleAcceder}>
          Acceder
        </button>
      </section>
    </main>
  )
}

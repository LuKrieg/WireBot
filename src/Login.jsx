import { useEffect, useState } from 'react'
import './App.css'
import { apiRequest } from './apiClient.js'

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
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'))
  }

  const handleAcceder = async () => {
    const code = username.trim() || 'default_user'
    let token = null
    setErrorMessage('')
    
    try {
      let result = await apiRequest('/api/login', {
        method: 'POST',
        body: JSON.stringify({ code })
      })
      
      if (!result.ok) {
        // If login fails, try to register
        await apiRequest('/api/register', {
          method: 'POST',
          body: JSON.stringify({ code })
        })
        
        // Then login again to get the token
        result = await apiRequest('/api/login', {
          method: 'POST',
          body: JSON.stringify({ code })
        })
      }
      
      if (result.ok) {
        token = result.data.token
      } else {
        setErrorMessage(result.errorMessage || 'No fue posible iniciar sesión.')
      }
    } catch (error) {
      console.error('Error connecting to backend:', error)
      setErrorMessage('Error de conexión con el backend.')
    }

    if (!token) return
    onSuccess?.(code, token)
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
        {errorMessage && <p className="login-error-message">{errorMessage}</p>}
      </section>
    </main>
  )
}

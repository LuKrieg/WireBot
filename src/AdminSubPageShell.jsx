import { useState } from 'react'
import './App.css'
import { useWireBotTheme } from './useWireBotTheme.js'

export default function AdminSubPageShell({ title, onBack, onLogout, children }) {
  const { toggleTheme } = useWireBotTheme()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  return (
    <main className="admin-subpage">
      <header className="admin-subpage-header">
        <button type="button" className="admin-back-button" onClick={onBack}>
          Volver
        </button>

        <div className="top-actions admin-subpage-actions">
          <button
            type="button"
            className="icon-button"
            onClick={toggleTheme}
            aria-label="Cambiar tema"
          >
            <img src="/brightness_medium.png" alt="" aria-hidden="true" />
          </button>

          <div className="user-menu-wrapper">
            <button
              type="button"
              className="icon-button"
              aria-label="Abrir menu de usuario"
              onClick={() => setIsUserMenuOpen((open) => !open)}
            >
              <img src="/logout.png" alt="" aria-hidden="true" />
            </button>

            {isUserMenuOpen && (
              <div className="user-menu" role="menu" aria-label="Menu de usuario">
                <p className="user-menu-title">
                  Hola <strong>Admin</strong>
                </p>

                <button
                  type="button"
                  className="logout-button"
                  onClick={() => {
                    setIsUserMenuOpen(false)
                    onLogout?.()
                  }}
                >
                  <span>Salir</span>
                  <img src="/arrow_back.png" alt="" aria-hidden="true" />
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="admin-subpage-content">
        <h1 className="admin-subpage-title">{title}</h1>
        {children}
      </div>
    </main>
  )
}

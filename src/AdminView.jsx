import { useState } from 'react'
import './App.css'
import { useWireBotTheme } from './useWireBotTheme.js'

export default function AdminView({ onNavigate, onLogout }) {
  const { toggleTheme } = useWireBotTheme()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  const cards = [
    {
      id: 'chat',
      label: 'Chat',
      icon: '/question_answer.png',
      target: 'adminChat',
    },
    {
      id: 'users',
      label: 'Gestionar usuarios',
      icon: '/groups.png',
      target: 'userManagement',
    },
    {
      id: 'data',
      label: 'Gestionar datos',
      icon: '/assignment.png',
      target: 'dataManagement',
    },
  ]

  return (
    <main className="admin-dashboard">
      <header className="top-actions admin-dashboard-top">
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
      </header>

      <div className="admin-dashboard-inner">
        <img src="/logo.png" alt="WireBot" className="admin-dashboard-logo" />

        <p className="admin-dashboard-greeting">
          Hola Admin, ¿Qué harás hoy?
        </p>

        <nav className="admin-nav-grid" aria-label="Panel de administracion">
          {cards.map((card) => (
            <button
              key={card.id}
              type="button"
              className="admin-nav-card"
              onClick={() => onNavigate?.(card.target)}
            >
              <span className="admin-nav-card-icon-well">
                <img src={card.icon} alt="" aria-hidden="true" />
              </span>
              <span className="admin-nav-card-label">{card.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </main>
  )
}

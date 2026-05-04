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

export default function Chat({ onLogout }) {
  const [theme, setTheme] = useState(getInitialTheme)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState([])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((currentTheme) => (currentTheme === 'dark' ? 'light' : 'dark'))
  }

  const sendMessage = () => {
    const text = draft.trim()
    if (!text) return

    const myId = `${Date.now()}-me`
    setMessages((current) => [...current, { id: myId, from: 'me', text }])
    setDraft('')

    window.setTimeout(() => {
      const otherId = `${Date.now()}-other`
      setMessages((current) => [
        ...current,
        {
          id: otherId,
          from: 'other',
          text: 'Recibido. ¿En qué más te puedo ayudar?',
        },
      ])
    }, 450)
  }

  return (
    <main className="chat-screen">
      <header className="top-actions">
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
            onClick={() => setIsUserMenuOpen((value) => !value)}
          >
            <img src="/logout.png" alt="" aria-hidden="true" />
          </button>

          {isUserMenuOpen && (
            <div className="user-menu" role="menu" aria-label="Menu de usuario">
              <p className="user-menu-title">
                Hola <strong>usser</strong>
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

      <section className="chat-body">
        <div className="chat-scroll-area">
          <section className="chat-welcome" aria-label="Bienvenida del chat">
            <img src="/logo.png" alt="" aria-hidden="true" className="chat-avatar" />
            <p className="chat-welcome-text">
              Hola usser, soy WireBot, tu asistente tecnico de confianza.
            </p>
          </section>

          <section className="chat-messages" aria-label="Mensajes">
            {messages.map((message) => (
              <div
                key={message.id}
                className={
                  message.from === 'me'
                    ? 'chat-row chat-row--me'
                    : 'chat-row chat-row--other'
                }
              >
                {message.from === 'other' && (
                  <img
                    src="/logo.png"
                    alt=""
                    aria-hidden="true"
                    className="chat-avatar"
                  />
                )}
                <div
                  className={
                    message.from === 'me'
                      ? 'chat-bubble chat-bubble--me'
                      : 'chat-bubble chat-bubble--other'
                  }
                >
                  {message.text}
                </div>
              </div>
            ))}
          </section>
        </div>
      </section>

      <section className="prompt-section" aria-label="Escribir mensaje">
        <input
          type="text"
          placeholder="Escribe aqui..."
          className="prompt-input"
          aria-label="Escribe aqui"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              sendMessage()
            }
          }}
        />
        <button
          type="button"
          className="send-button"
          onClick={sendMessage}
          aria-label="Enviar mensaje"
        >
          <img src="/send.png" alt="" aria-hidden="true" />
        </button>
      </section>
    </main>
  )
}

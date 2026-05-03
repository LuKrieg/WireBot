import { useState } from 'react'
import AdminSubPageShell from './AdminSubPageShell.jsx'

export default function AdminChat({ onBack, onLogout }) {
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState([])

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
          text: 'Perfecto. Indícame qué necesitas administrar.',
        },
      ])
    }, 450)
  }

  return (
    <AdminSubPageShell title="Chat" onBack={onBack} onLogout={onLogout}>
      <main className="chat-screen chat-screen--subpage">
        <section className="chat-body">
          <div className="chat-scroll-area">
            <section className="chat-welcome" aria-label="Bienvenida del chat">
              <img src="/logo.png" alt="" aria-hidden="true" className="chat-avatar" />
              <p className="chat-welcome-text">
                Hola Admin, soy WireBot. ¿Qué harás hoy?
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
          <button type="button" className="send-button" onClick={sendMessage}>
            Enviar
          </button>
        </section>
      </main>
    </AdminSubPageShell>
  )
}

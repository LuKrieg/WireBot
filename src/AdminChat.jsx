import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import AdminSubPageShell from './AdminSubPageShell.jsx'
import { apiRequest } from './apiClient.js'

export default function AdminChat({ onBack, onLogout, token }) {
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async () => {
    const text = draft.trim()
    if (!text) return

    const myId = `${Date.now()}-me`
    setMessages((current) => [...current, { id: myId, from: 'me', text }])
    setDraft('')
    setIsLoading(true)

    try {
      const result = await apiRequest('/api/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ pregunta: text })
      })

      if (result.ok) {
        const otherId = `${Date.now()}-other`
        setMessages((current) => [
          ...current,
          {
            id: otherId,
            from: 'other',
            text: result.data.respuesta || 'Sin respuesta',
          },
        ])
      } else {
        setMessages((current) => [
          ...current,
          {
            id: `${Date.now()}-err`,
            from: 'other',
            text: `**Error**: ${result.errorMessage}`,
          },
        ])
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-err`,
          from: 'other',
          text: '**Error de conexión.** Asegúrate de que el contenedor esté corriendo.',
        },
      ])
    } finally {
      setIsLoading(false)
    }
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
                    {message.from === 'other' ? (
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                    ) : (
                      message.text
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="chat-row chat-row--other">
                  <img src="/logo.png" alt="" aria-hidden="true" className="chat-avatar" />
                  <div className="chat-bubble chat-bubble--other">
                    <em>Pensando...</em>
                  </div>
                </div>
              )}
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
    </AdminSubPageShell>
  )
}

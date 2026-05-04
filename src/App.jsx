import { useState } from 'react'
import AdminChat from './AdminChat.jsx'
import AdminView from './AdminView.jsx'
import Chat from './Chat.jsx'
import DataManagement from './DataManagement.jsx'
import Login from './Login.jsx'
import UsserManagement from './UsserManagement.jsx'

export default function App() {
  const [session, setSession] = useState(null)
  const [adminScreen, setAdminScreen] = useState('dashboard')

  const handleLogout = () => {
    setSession(null)
    setAdminScreen('dashboard')
  }

  if (!session) {
    return (
      <Login
        onSuccess={(username, token) => {
          const isAdmin = username.toLowerCase() === 'admin'
          setSession({ role: isAdmin ? 'admin' : 'user', token })
          setAdminScreen('dashboard')
        }}
      />
    )
  }

  if (session.role === 'admin') {
    switch (adminScreen) {
      case 'adminChat':
        return (
          <AdminChat
            onBack={() => setAdminScreen('dashboard')}
            onLogout={handleLogout}
            token={session.token}
          />
        )
      case 'userManagement':
        return (
          <UsserManagement
            onBack={() => setAdminScreen('dashboard')}
            onLogout={handleLogout}
          />
        )
      case 'dataManagement':
        return (
          <DataManagement
            onBack={() => setAdminScreen('dashboard')}
            onLogout={handleLogout}
          />
        )
      default:
        return (
          <AdminView
            onNavigate={(target) => setAdminScreen(target)}
            onLogout={handleLogout}
          />
        )
    }
  }

  return <Chat onLogout={handleLogout} token={session.token} />
}

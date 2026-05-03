import AdminSubPageShell from './AdminSubPageShell.jsx'

export default function UsserManagement({ onBack, onLogout }) {
  return (
    <AdminSubPageShell
      title="Gestionar usuarios"
      onBack={onBack}
      onLogout={onLogout}
    >
      <p className="admin-subpage-placeholder">
        Gestion de usuarios (en construccion).
      </p>
    </AdminSubPageShell>
  )
}

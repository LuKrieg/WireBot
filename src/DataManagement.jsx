import AdminSubPageShell from './AdminSubPageShell.jsx'

export default function DataManagement({ onBack, onLogout }) {
  return (
    <AdminSubPageShell
      title="Gestionar datos"
      onBack={onBack}
      onLogout={onLogout}
    >
      <p className="admin-subpage-placeholder">
        Gestion de datos (en construccion).
      </p>
    </AdminSubPageShell>
  )
}

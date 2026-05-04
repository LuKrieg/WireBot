# app/models/user.py
#
# Almacenamiento en memoria simple.
# Cuando quieras persistencia real, reemplaza _store por SQLAlchemy / SQLite.

from __future__ import annotations
import uuid


# Simula la "base de datos" en memoria
_store: dict[str, "User"] = {}


class User:
    def __init__(self, code: str, id: str | None = None):
        self.id: str = id or str(uuid.uuid4())
        self.code: str = code

    # ── Persistencia ──────────────────────────────────────────────────────────

    def save(self) -> None:
        """Guarda (o actualiza) el usuario en el store."""
        _store[self.code] = self

    # ── Consultas ─────────────────────────────────────────────────────────────

    @classmethod
    def find_by_code(cls, code: str) -> "User | None":
        return _store.get(code)

    @classmethod
    def find_by_id(cls, user_id: str) -> "User | None":
        for user in _store.values():
            if user.id == user_id:
                return user
        return None

    # ── Representación ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"id": self.id, "code": self.code}

    def __repr__(self) -> str:
        return f"<User id={self.id} code={self.code}>"

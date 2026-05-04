# app/models/session.py
#
# Registro liviano de sesiones activas (token → user_id).
# Útil para invalidar tokens en logout sin necesidad de BD.

from __future__ import annotations
import uuid
from datetime import datetime


_sessions: dict[str, "Session"] = {}


class Session:
    def __init__(self, user_id: str, token: str):
        self.id: str = str(uuid.uuid4())
        self.user_id: str = user_id
        self.token: str = token
        self.created_at: datetime = datetime.utcnow()
        self.active: bool = True

    # ── Persistencia ──────────────────────────────────────────────────────────

    def save(self) -> None:
        _sessions[self.token] = self

    def revoke(self) -> None:
        self.active = False

    # ── Consultas ─────────────────────────────────────────────────────────────

    @classmethod
    def find_by_token(cls, token: str) -> "Session | None":
        return _sessions.get(token)

    @classmethod
    def revoke_all_for_user(cls, user_id: str) -> None:
        for session in _sessions.values():
            if session.user_id == user_id:
                session.active = False

    # ── Representación ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<Session user_id={self.user_id} active={self.active}>"

# app/config.py

import os


class Config:
    # ── Seguridad ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")

    # ── Archivos ───────────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    ALLOWED_EXTENSIONS = {"xlsx", "xls"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB máximo por archivo

    # ── Ollama ─────────────────────────────────────────────────────────────────
    OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

    # ── RAG: filas más similares enviadas al modelo (no es un barrido del Excel completo)
    RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "100"))
    # Máximo de filas extra por coincidencia textual en consultas de “listado” (p. ej. trefiladoras)
    RAG_LISTADO_MAX = int(os.environ.get("RAG_LISTADO_MAX", "500"))

    # ── JWT ────────────────────────────────────────────────────────────────────
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 8))

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Orígenes permitidos: el frontend en dev (Vite puerto 5173) y prod
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")

    @classmethod
    def validate_runtime(cls) -> None:
        if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-secret-key-cambiar-en-produccion":
            print("Advertencia: SECRET_KEY en valor por defecto. Configura SECRET_KEY en entorno.")

        if cls.JWT_EXPIRATION_HOURS <= 0:
            raise ValueError("JWT_EXPIRATION_HOURS debe ser mayor que 0.")

        if cls.RAG_TOP_K < 1:
            raise ValueError("RAG_TOP_K debe ser mayor o igual que 1.")

        if cls.RAG_LISTADO_MAX < 0:
            raise ValueError("RAG_LISTADO_MAX debe ser mayor o igual que 0.")

        if not cls.OLLAMA_URL.startswith(("http://", "https://")):
            raise ValueError("OLLAMA_URL debe iniciar con http:// o https://")

        if not cls.CORS_ORIGINS or not any(origin.strip() for origin in cls.CORS_ORIGINS):
            raise ValueError("CORS_ORIGINS no puede estar vacío.")

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

    # ── JWT ────────────────────────────────────────────────────────────────────
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 8))

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Orígenes permitidos: el frontend en dev (Vite puerto 5173) y prod
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")

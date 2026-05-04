# app/middleware/cors.py

from flask import Flask
from flask_cors import CORS


def init_cors(app: Flask) -> None:
    """
    Configura CORS para permitir llamadas desde el frontend.
    Los orígenes se leen de config.CORS_ORIGINS para que sean
    fácilmente ajustables por variable de entorno.
    """
    CORS(
        app,
        resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

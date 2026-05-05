# app/__init__.py

import os
import logging
import threading
from flask import Flask
from app.config import Config
from app.middleware.cors import init_cors
from app.middleware.error_handler import init_error_handlers


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.validate_runtime()
    _configurar_logging(app)

    # Middlewares
    init_cors(app)
    init_error_handlers(app)

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.stats import stats_bp
    from app.routes.upload import upload_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(upload_bp)

    @app.get("/healthz")
    def healthz():
        from app.services.rag_service import is_ready

        return {
            "status": "ok",
            "rag_ready": is_ready(),
            "model": app.config.get("OLLAMA_MODEL"),
        }, 200

    # Carga el Excel inicial si existe
    _cargar_datos_iniciales(app)

    return app


def _cargar_datos_iniciales(app: Flask):
    """
    Carga Excel + RAG en un hilo en segundo plano para que Flask enlace el puerto
    de inmediato (login, healthz). El chat devuelve 503 hasta que RAG esté listo.
    """
    from app.services.excel_service import cargar_excel
    from app.services.rag_service import inicializar

    excel_path = os.path.join(app.config["UPLOAD_FOLDER"], "datos_enerwire.xlsx")

    def _carga_background() -> None:
        if not os.path.exists(excel_path):
            app.logger.info("No hay Excel inicial en %s — sube uno con POST /upload.", excel_path)
            return
        try:
            app.logger.info("Cargando Excel y construyendo índice RAG en segundo plano…")
            cargar_excel(excel_path)
            inicializar()
            app.logger.info("Excel y RAG listos.")
        except Exception:
            app.logger.exception("No se pudo completar la carga inicial de Excel/RAG")

    threading.Thread(
        target=_carga_background,
        daemon=True,
        name="wirebot-rag-bootstrap",
    ).start()


def _configurar_logging(app: Flask) -> None:
    app.logger.setLevel(logging.INFO)

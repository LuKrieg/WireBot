# app/__init__.py

import os
from flask import Flask
from app.config import Config
from app.middleware.cors import init_cors
from app.middleware.error_handler import init_error_handlers


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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

    # Carga el Excel inicial si existe
    _cargar_datos_iniciales(app)

    return app


def _cargar_datos_iniciales(app: Flask):
    """Si ya existe un Excel guardado, lo carga al arrancar."""
    from app.services.excel_service import cargar_excel
    from app.services.rag_service import inicializar

    excel_path = os.path.join(app.config["UPLOAD_FOLDER"], "datos.xlsx")
    if os.path.exists(excel_path):
        try:
            print(f"Cargando Excel existente: {excel_path}")
            cargar_excel(excel_path)
            inicializar()
        except Exception as e:
            print(f"Advertencia: no se pudo cargar el Excel inicial: {e}")
    else:
        print("No se encontró Excel inicial. Sube uno vía POST /upload.")

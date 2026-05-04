# app/middleware/error_handler.py

from flask import Flask, jsonify


def init_error_handlers(app: Flask) -> None:

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Solicitud incorrecta", "detalle": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "No autorizado"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Acceso prohibido"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(413)
    def request_too_large(e):
        return jsonify({"error": "El archivo supera el tamaño máximo permitido (16 MB)"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500

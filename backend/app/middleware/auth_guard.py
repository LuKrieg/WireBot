# app/middleware/auth_guard.py

from functools import wraps
from flask import request, jsonify
from app.services.auth_service import decode_token


def require_auth(f):
    """
    Decorador que protege un endpoint exigiendo un JWT válido.

    Uso:
        @chat_bp.route("/chat", methods=["POST"])
        @require_auth
        def chat():
            ...

    El payload decodificado queda disponible en flask.g.current_user.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token no proporcionado"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            from flask import g
            g.current_user = decode_token(token)
        except ValueError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated

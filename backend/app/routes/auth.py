# app/routes/auth.py

from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    user_code = data.get("code")

    if not user_code:
        return jsonify({"error": "El código es requerido"}), 400

    try:
        user = register_user(user_code)

        return jsonify({
            "message": "Usuario registrado",
            "user": {
                "id": user.id,
                "code": user.code
            }
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user_code = data.get("code")

    if not user_code:
        return jsonify({"error": "El código es requerido"}), 400

    try:
        token = login_user(user_code)

        return jsonify({
            "message": "Login exitoso",
            "token": token
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401

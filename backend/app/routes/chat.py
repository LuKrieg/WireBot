# app/routes/chat.py

from flask import Blueprint, request, jsonify
from app.services.rag_service import buscar_contexto
from app.services.ollama_service import preguntar
from app.middleware.auth_guard import require_auth

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
@require_auth
def chat():
    data = request.get_json(silent=True)
    if not data or not data.get("pregunta"):
        return jsonify({"error": "Falta el campo 'pregunta'"}), 400

    pregunta = data["pregunta"]

    try:
        contexto = buscar_contexto(pregunta)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    respuesta = preguntar(contexto, pregunta)

    return jsonify({
        "respuesta": respuesta,
        "contexto_usado": contexto,
    })

from flask import Blueprint, request, jsonify
from app.services.rag_service import buscar_contexto
from app.services.ollama_service import preguntar

# Ruta legacy: usar backend/app/routes/chat.py para runtime principal.

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or not data.get("pregunta"):
        return jsonify({"error": "Falta el campo 'pregunta'"}), 400

    pregunta = data["pregunta"]

    contexto = buscar_contexto(pregunta)
    respuesta = preguntar(contexto, pregunta)

    return jsonify({
        "respuesta": respuesta,
        "contexto_usado": contexto,
    })

# app/routes/chat.py

import logging
import time
from flask import Blueprint, request, jsonify, current_app
from app.services.rag_service import construir_contexto_para_chat
from app.services.ollama_service import preguntar
from app.services.excel_service import get_resumen
from app.middleware.auth_guard import require_auth

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)


@chat_bp.route("/chat", methods=["POST"])
@require_auth
def chat():
    started_at = time.perf_counter()
    data = request.get_json(silent=True)
    if not data or not data.get("pregunta"):
        return jsonify({"error": "Falta el campo 'pregunta'"}), 400

    pregunta = data["pregunta"]

    try:
        top_k = current_app.config.get("RAG_TOP_K", 100)
        listado_max = current_app.config.get("RAG_LISTADO_MAX", 500)
        contexto, rag_meta = construir_contexto_para_chat(pregunta, top_k, listado_max)
    except RuntimeError as e:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.warning("event=chat_unavailable latency_ms=%s", elapsed_ms)
        return jsonify({"error": str(e)}), 503

    stats = {**rag_meta}
    try:
        res_doc = get_resumen()
        cols = res_doc.get("columnas") or []
        stats["num_columnas"] = len(cols)
        if cols:
            shown = [str(c) for c in cols[:35]]
            tail = len(cols) - len(shown)
            stats["columnas_resumen"] = ", ".join(shown) + (f" … (+{tail} más)" if tail > 0 else "")
    except Exception:
        pass

    respuesta = preguntar(contexto, pregunta, stats)
    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info("event=chat_completed latency_ms=%s context_chars=%s", elapsed_ms, len(contexto))

    return jsonify({
        "respuesta": respuesta,
        "contexto_usado": contexto,
        "rag_meta": rag_meta,
    })

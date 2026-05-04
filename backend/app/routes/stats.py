# app/routes/stats.py

from flask import Blueprint, jsonify
from app.services.excel_service import get_resumen   # ← import absoluto corregido
from app.middleware.auth_guard import require_auth

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/resumen", methods=["GET"])
@require_auth
def resumen():
    datos = get_resumen()
    if not datos:
        return jsonify({"error": "No hay ningún documento cargado."}), 404
    return jsonify(datos)

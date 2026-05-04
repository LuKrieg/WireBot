from flask import Blueprint, jsonify
from services.excel_service import get_resumen

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/resumen", methods=["GET"])
def resumen():
    datos = get_resumen()
    if not datos:
        return jsonify({"error": "No hay ningún documento cargado."}), 404
    return jsonify(datos)

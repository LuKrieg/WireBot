# app/routes/upload.py

import os
from flask import Blueprint, request, jsonify, current_app
from app.services.excel_service import cargar_excel
from app.services.rag_service import inicializar
from app.middleware.auth_guard import require_auth

upload_bp = Blueprint("upload", __name__)


def _extension_permitida(filename: str) -> bool:
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@upload_bp.route("/upload", methods=["POST"])
@require_auth
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "El archivo no tiene nombre."}), 400

    if not _extension_permitida(file.filename):
        return jsonify({"error": "Solo se permiten archivos .xlsx o .xls"}), 400

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    dest = os.path.join(upload_folder, "datos.xlsx")
    file.save(dest)

    try:
        cargar_excel(dest)
        inicializar()
    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

    return jsonify({"mensaje": "Archivo cargado correctamente.", "path": dest})

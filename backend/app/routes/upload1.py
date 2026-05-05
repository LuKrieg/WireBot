import os
from flask import Blueprint, request, jsonify, current_app
from app.services.excel_service import cargar_excel
from app.services.rag_service import construir_indice

# Ruta legacy: usar backend/app/routes/upload.py para runtime principal.

upload_bp = Blueprint("upload", __name__)


def _extension_permitida(filename: str) -> bool:
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@upload_bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "El archivo no tiene nombre."}), 400

    if not _extension_permitida(file.filename):
        return jsonify({"error": "Solo se permiten archivos .xlsx o .xls"}), 400

    # Guarda el archivo en la carpeta de uploads
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    dest = os.path.join(upload_folder, "datos_enerwire.xlsx")
    file.save(dest)

    # Recarga Excel y reconstruye el índice FAISS
    try:
        cargar_excel(dest)
        construir_indice()
    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

    return jsonify({"mensaje": "Archivo cargado correctamente.", "path": dest})

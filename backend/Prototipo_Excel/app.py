import faiss
import numpy as np
import os
import pandas as pd
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # <--- 1. NUEVA IMPORTACIÓN
from sentence_transformers import SentenceTransformer

# Archivo legacy para referencia/prototipo.
# Backend oficial: backend/run.py + backend/app/

app = Flask(__name__)
CORS(app)  # <--- 2. HABILITAR CORS GLOBALMENTE

# ── Configuración ──────────────────────────────────────────
OLLAMA_URL = "http://host.docker.internal:11434"
OLLAMA_MODEL = "llama3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
EXCEL_CANDIDATES = [
    os.path.join(PROJECT_ROOT, "uploads", "datos_enerwire.xlsx"),
    os.path.join(PROJECT_ROOT, "uploads", "datos.xlsx"),
    os.path.join(BASE_DIR, "datos_enerwire.xlsx"),
    os.path.join(BASE_DIR, "datos.xlsx"),
]
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "100"))


def _resolver_excel_path() -> str:
    for candidate in EXCEL_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "No se encontró un archivo Excel válido. "
        "Ubica el archivo en backend/uploads/datos_enerwire.xlsx"
    )

# ── Carga y vectorización del Excel ───────────────────────
print("Cargando Excel...")
EXCEL_PATH = _resolver_excel_path()
print(f"Usando Excel: {EXCEL_PATH}")
df = pd.read_excel(EXCEL_PATH)

def generar_resumen_global(df):
    resumen = {
        "total_filas": len(df),
        "columnas": df.columns.tolist(),
        "categoricas": {},
        "numericas": {}
    }
    for col in df.select_dtypes(include=['object']).columns:
        resumen["categoricas"][col] = df[col].value_counts().to_dict()
    for col in df.select_dtypes(include=['number']).columns:
        resumen["numericas"][col] = {
            "min": df[col].min(),
            "max": df[col].max(),
            "suma": df[col].sum(),
            "promedio": round(df[col].mean(), 2)
        }
    return resumen

resumen_global = generar_resumen_global(df)

def fila_a_texto(row):
    return " | ".join([f"{col}: {val}" for col, val in row.items()])

fragmentos = df.apply(fila_a_texto, axis=1).tolist()

print(f"Vectorizando {len(fragmentos)} filas...")
embedder = SentenceTransformer(EMBED_MODEL)
vectores = embedder.encode(fragmentos, show_progress_bar=True)
vectores = np.array(vectores, dtype="float32")

dimension = vectores.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(vectores)
print("FAISS listo ✓")

# ── Función RAG ────────────────────────────────────────────
def buscar_contexto(pregunta, top_k=DEFAULT_RAG_TOP_K):
    n = len(fragmentos)
    k = min(top_k, n)
    vec = embedder.encode([pregunta]).astype("float32")
    _, indices = index.search(vec, k)
    lines = ["Casos Históricos (datos cargados desde Excel):"]
    for rank, idx in enumerate(indices[0][:k], start=1):
        lines.append(f"{rank}. {fragmentos[int(idx)]}")
    return "\n".join(lines)

def preguntar_ollama(prompt):
    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=1800)
        return res.json().get("response", "Sin respuesta")
    except Exception as e:
        return f"Error conectando con Ollama: {str(e)}"

# ── Endpoints ─────────────────────────────────────────────
@app.route('/')
def home():
    # Esta ruta sirve el archivo HTML automáticamente al entrar a la IP
    return render_template('index.html')

@app.route("/resumen", methods=["GET"])
def ver_resumen():
    return jsonify(resumen_global)

# 3. MÉTODOS ACTUALIZADOS (POST y OPTIONS son manejados por CORS automáticamente ahora)
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    pregunta = data.get("pregunta", "")
    if not pregunta:
        return jsonify({"error": "Falta el campo 'pregunta'"}), 400

    contexto = buscar_contexto(pregunta)

    prompt = f"""Eres un Ingeniero Senior de Mantenimiento en Enerwire. Tu especialidad es el diagnóstico de fallas raíz (Root Cause Analysis).

Tarea: Analiza la descripción del operario comparándola con los [Casos Históricos] proporcionados abajo. Cada ítem numerado es un caso recuperado de datos técnicos cargados desde Excel.

[Casos Históricos]
{contexto}

Descripción / pregunta del operario:
{pregunta}

Formato de salida obligatorio (usa exactamente estos títulos de sección en español):

1) Identificación
Menciona el código, etiqueta o referencia de máquina/equipo u organización que corresponda a lo que describe el operario, solo si aparece en los casos o en su mensaje.

2) Diagnóstico probabilístico
Basado en la similitud y la recurrencia de tipos de falla **solo dentro de los casos numerados arriba**, enumera entre 2 y 3 causas raíz probables. Asigna un porcentaje a cada una de forma que refleje cuántas veces ese patrón aparece o se alinea con los casos recuperados; normaliza para que los porcentajes sumen 100%. No extrapoles datos que no estén en esos casos.

3) Plan de acción
Lista de pasos para que el operario verifique físicamente el equipo (por ejemplo: "Revisa el tensado del cable para descartar deslizamiento"). Sé concreto y seguro.

4) Solución histórica
Resume brevemente cómo se resolvieron o atendieron situaciones similares en los casos proporcionados (correctivo, preventivo, mejora, tiempos, etc.) cuando conste en el texto.

Restricciones:
- No afirmes cuántas filas o registros del sistema estás "analizando"; tampoco inventes totales. Solo trabajas con el bloque [Casos Históricos] que recibes.
- No inventes fallas, causas ni soluciones que no puedas fundamentar en los [Casos Históricos] o en la descripción del operario.
- No menciones folios ni números de orden de trabajo (OT).
- No menciones archivos, rutas ni nombres de archivo.
- Lenguaje técnico pero claro para un operario.
- Si los casos no permiten un diagnóstico razonable, dilo explícitamente en cada sección aplicable."""

    respuesta = preguntar_ollama(prompt)
    return jsonify({"respuesta": respuesta, "contexto_usado": contexto})

if __name__ == "__main__":
    # Escuchando en 0.0.0.0 para acceso desde Docker/Red Local
    app.run(host="0.0.0.0", port=5000)
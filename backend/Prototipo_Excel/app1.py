import faiss
import numpy as np
import pandas as pd
import requests
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# Archivo legacy para referencia/prototipo.
# Backend oficial: backend/run.py + backend/app/

app = Flask(__name__)

# ── Configuración ──────────────────────────────────────────
OLLAMA_URL = "http://host.docker.internal:11434"
OLLAMA_MODEL = "llama3"
EXCEL_PATH = "datos_enerwire.xlsx"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ── Carga y vectorización del Excel ───────────────────────
print("Cargando Excel...")
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
def buscar_contexto(pregunta, top_k=5):
    vec = embedder.encode([pregunta]).astype("float32")
    _, indices = index.search(vec, top_k)
    return "\n".join([fragmentos[i] for i in indices[0]])

def preguntar_ollama(prompt):
    res = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })
    return res.json().get("response", "Sin respuesta")

# ── Endpoints ─────────────────────────────────────────────
@app.route("/resumen", methods=["GET"])
def ver_resumen():
    return jsonify(resumen_global)  # Devuelve JSON estructurado, no texto plano

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    pregunta = data.get("pregunta", "")
    if not pregunta:
        return jsonify({"error": "Falta el campo 'pregunta'"}), 400

    contexto = buscar_contexto(pregunta)

    # Prompt limpio, sin resumen_global
    prompt = f"""Eres un asistente especializado de la empresa Enerwire.
Tu objetivo es responder preguntas sobre los mantenimientos, fallas y datos técnicos de máquinas y equipos de Enerwire, basándote en los datos extraídos del archivo oficial 'datos_enerwire.xlsx'.

FILAS DE DATOS MÁS RELEVANTES (MÁQUINAS Y EQUIPOS DE ENERWIRE):
{contexto}

Pregunta del usuario: {pregunta}

Instrucciones importantes:
1. Responde de forma concisa basándote ÚNICAMENTE en las filas proporcionadas arriba.
2. NUNCA inventes información ni menciones productos como "laptops" o inventario general si no está en el contexto. El enfoque es estrictamente sobre maquinaria de Enerwire."""

    respuesta = preguntar_ollama(prompt)
    return jsonify({"respuesta": respuesta, "contexto_usado": contexto})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
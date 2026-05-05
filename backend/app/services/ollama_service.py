# app/services/ollama_service.py

import re
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

# Preguntas de datos / listados / metadatos → nunca usar plantilla RCA
_DATA_OR_LIST_RE = re.compile(
    r"(?i)(cuántas?\s+filas|cuántas?\s+columnas|filas?\s+y\s+columnas|columnas?\s+y\s+filas|"
    r"listar|listado|enumerar|datos\s+de|todas\s+las|dime\s+los\s+datos|qué\s+datos|"
    r"trefiladora|trefiladoras?|enconchadora|muestra(me)?|cuántos?\s+casos)"
)

# Síntomas, averías, pedir RCA
_RCA_RE = re.compile(
    r"(?i)\b(falla|avería|averías|averi[oa]|falló|parad[ao]|vibraci[oó]n|"
    r"ruido\s+anormal|no\s+arranca|atasc|rotur|grieta|fuga\s+de|temperatura\s+alta|"
    r"calidad\s+defect|causa\s+raíz|root\s+cause|\brca\b|"
    r"diagnóstico\s+probabilístico|diagnóstico\s+de\s+falla|qué\s+causó)\b"
)


def _clasificar_modo(pregunta: str) -> str:
    """
    Por defecto 'directo' para no forzar la plantilla RCA.
    Solo 'rca' si huele a avería/síntoma y no es una consulta de datos/listado.
    """
    if not pregunta or not pregunta.strip():
        return "directo"
    if _DATA_OR_LIST_RE.search(pregunta):
        return "directo"
    if _RCA_RE.search(pregunta):
        return "rca"
    return "directo"


def preguntar(contexto: str, pregunta: str, stats: dict | None = None) -> str:
    """
    Construye el prompt, llama a Ollama y devuelve la respuesta como string.
    Lee OLLAMA_URL y OLLAMA_MODEL desde la config de Flask para que sean
    configurables por variable de entorno.

    stats: metadatos opcionales (RAG + Excel) para preguntas sobre cobertura,
    filas, columnas; evita que el modelo invente cifras.
    """
    modo = _clasificar_modo(pregunta)
    logger.info("event=ollama_prompt_mode mode=%s", modo)
    prompt = _construir_prompt(contexto, pregunta, stats, modo)
    return _llamar_ollama(prompt)


def _bloque_metadatos_sistema(stats: dict | None) -> str:
    if not stats:
        return ""
    cols = stats.get("columnas_resumen")
    partes = []
    if stats.get("total_filas_excel") is not None:
        partes.append(f"- Filas totales en el Excel cargado: {stats['total_filas_excel']}")
    if stats.get("num_columnas") is not None:
        partes.append(f"- Número de columnas: {stats['num_columnas']}")
    if cols:
        partes.append(f"- Nombres de columnas: {cols}")
    if stats.get("casos_total_en_contexto") is not None:
        partes.append(
            f"- Fragmentos de caso enviados en este mensaje: {stats['casos_total_en_contexto']} "
            f"(por similitud: {stats.get('casos_por_similitud', '?')}; "
            f"por coincidencia de texto: {stats.get('casos_por_coincidencia_texto', '?')})"
        )
    if stats.get("rag_top_k_config") is not None:
        partes.append(f"- Límite configurado de casos por similitud (top_k): {stats['rag_top_k_config']}")
    if not partes:
        return ""
    return (
        "\n[Metadatos del sistema — usa SOLO estos números si el usuario pregunta por filas, columnas o "
        "cuántos casos se enviaron; no inventes otras cifras]\n"
        + "\n".join(partes)
        + "\n"
    )


def _construir_prompt_directo(contexto: str, pregunta: str, stats: dict | None) -> str:
    meta = _bloque_metadatos_sistema(stats)
    return f"""Eres un asistente técnico en Enerwire. Responde en español.

Fuente de datos: solo lo que aparece en [Casos Históricos] y en [Metadatos del sistema]. Cada número de lista es una fila de datos.

{meta}[Casos Históricos]
{contexto}

Pregunta:
{pregunta}

Instrucciones (obligatorias):
- Responde de forma directa (viñetas o párrafos). 
- PROHIBIDO usar las secciones "1) Identificación", "2) Diagnóstico probabilístico", "3) Plan de acción", "4) Solución histórica" o cualquier plantilla RCA. No inventes un "informe de falla" si no se pidió.
- Si preguntan equipos (ej. trefiladoras): lista nombres, códigos o textos que identifiquen máquina **copiándolos tal como salen** en las líneas relevantes (mira columnas tipo Equipo, Máquina, Línea, Descripción, Referencia al inicio de cada caso). Si una fila menciona ese equipo por código o nombre, no digas que "no hay referencia".
- Para filas/columnas/cuántos casos se envían: cita exactamente [Metadatos del sistema]; no inventes cifras.
- Si no hay filas que coincidan con lo pedido, dilo sin rellenar con diagnósticos genéricos.
- No menciones folios ni OT. Evita rutas de archivo."""


def _construir_prompt_rca(contexto: str, pregunta: str, stats: dict | None) -> str:
    meta = _bloque_metadatos_sistema(stats)
    return f"""Eres un ingeniero de mantenimiento en Enerwire (modo diagnóstico de falla).

{meta}[Casos Históricos]
{contexto}

Consulta sobre síntoma o avería:
{pregunta}

Responde con exactamente estas secciones en español:

1) Identificación
2) Diagnóstico probabilístico
3) Plan de acción
4) Solución histórica

En 2) solo causas que puedas fundamentar en los casos numerados; si no hay base, indica "No consta en los casos" y no fabriques porcentajes.

Restricciones: no inventes datos fuera de los casos; no menciones folios ni OT; evita rutas de archivo."""


def _construir_prompt(contexto: str, pregunta: str, stats: dict | None, modo: str) -> str:
    if modo == "rca":
        return _construir_prompt_rca(contexto, pregunta, stats)
    return _construir_prompt_directo(contexto, pregunta, stats)


def _llamar_ollama(prompt: str) -> str:
    ollama_url = current_app.config.get("OLLAMA_URL", "http://host.docker.internal:11434")
    ollama_model = current_app.config.get("OLLAMA_MODEL", "llama3")
    logger.info("event=ollama_request_start model=%s url=%s", ollama_model, ollama_url)

    try:
        res = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=1800,
        )
        res.raise_for_status()
        logger.info("event=ollama_request_ok status=%s", res.status_code)
        return res.json().get("response", "Sin respuesta del modelo.")
    except requests.exceptions.ConnectionError:
        logger.error("event=ollama_connection_error")
        return "Error: no se pudo conectar con Ollama. Verifica que esté corriendo."
    except requests.exceptions.Timeout:
        logger.error("event=ollama_timeout")
        return "Error: Ollama tardó demasiado en responder."
    except requests.exceptions.HTTPError as e:
        logger.error("event=ollama_http_error detail=%s", str(e))
        return f"Error HTTP al llamar a Ollama: {e}"

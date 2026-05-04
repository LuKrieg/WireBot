import requests

# ── Configuración ──────────────────────────────────────────────────────────────

OLLAMA_URL = "http://host.docker.internal:11434"
OLLAMA_MODEL = "llama3"


# ── Interfaz pública ───────────────────────────────────────────────────────────

def preguntar(contexto: str, pregunta: str) -> str:
    """
    Construye el prompt, llama a Ollama y devuelve la respuesta como string.

    Args:
        contexto: Filas relevantes devueltas por rag_service.buscar_contexto().
        pregunta: Pregunta original del usuario.

    Returns:
        Texto de respuesta del modelo, o un mensaje de error descriptivo.
    """
    prompt = _construir_prompt(contexto, pregunta)
    return _llamar_ollama(prompt)


# ── Lógica interna ─────────────────────────────────────────────────────────────

def _construir_prompt(contexto: str, pregunta: str) -> str:
    return f"""Eres un asistente que responde preguntas sobre un documento Excel.

FILAS MÁS RELEVANTES A LA PREGUNTA:
{contexto}

Pregunta: {pregunta}

Responde de forma concisa basándote únicamente en las filas proporcionadas.
Si la información no es suficiente para responder, indícalo claramente."""


def _llamar_ollama(prompt: str) -> str:
    try:
        res = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=1800,
        )
        res.raise_for_status()
        return res.json().get("response", "Sin respuesta del modelo.")
    except requests.exceptions.ConnectionError:
        return "Error: no se pudo conectar con Ollama. Verifica que esté corriendo."
    except requests.exceptions.Timeout:
        return "Error: Ollama tardó demasiado en responder."
    except requests.exceptions.HTTPError as e:
        return f"Error HTTP al llamar a Ollama: {e}"

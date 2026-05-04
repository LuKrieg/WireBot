# app/services/ollama_service.py

import requests
from flask import current_app


def preguntar(contexto: str, pregunta: str) -> str:
    """
    Construye el prompt, llama a Ollama y devuelve la respuesta como string.
    Lee OLLAMA_URL y OLLAMA_MODEL desde la config de Flask para que sean
    configurables por variable de entorno.
    """
    prompt = _construir_prompt(contexto, pregunta)
    return _llamar_ollama(prompt)


def _construir_prompt(contexto: str, pregunta: str) -> str:
    return f"""Eres un asistente que responde preguntas sobre un documento Excel.

FILAS MÁS RELEVANTES A LA PREGUNTA:
{contexto}

Pregunta: {pregunta}

Responde de forma concisa basándote únicamente en las filas proporcionadas.
Si la información no es suficiente para responder, indícalo claramente."""


def _llamar_ollama(prompt: str) -> str:
    ollama_url = current_app.config.get("OLLAMA_URL", "http://host.docker.internal:11434")
    ollama_model = current_app.config.get("OLLAMA_MODEL", "llama3")

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
        return res.json().get("response", "Sin respuesta del modelo.")
    except requests.exceptions.ConnectionError:
        return "Error: no se pudo conectar con Ollama. Verifica que esté corriendo."
    except requests.exceptions.Timeout:
        return "Error: Ollama tardó demasiado en responder."
    except requests.exceptions.HTTPError as e:
        return f"Error HTTP al llamar a Ollama: {e}"

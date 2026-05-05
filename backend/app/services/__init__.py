# Expone los puntos de entrada principales de cada servicio
# para que las routes importen desde aquí sin conocer la estructura interna.

from .excel_service import cargar_excel, get_fragmentos, get_resumen, get_dataframe
from .rag_service import (
    inicializar as inicializar_rag,
    construir_indice,
    buscar_contexto,
    construir_contexto_para_chat,
)
from .ollama_service import preguntar

__all__ = [
    "cargar_excel",
    "get_fragmentos",
    "get_resumen",
    "get_dataframe",
    "inicializar_rag",
    "construir_indice",
    "buscar_contexto",
    "construir_contexto_para_chat",
    "preguntar",
]

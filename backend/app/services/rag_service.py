import re
import faiss
import numpy as np
import logging
from sentence_transformers import SentenceTransformer

from .excel_service import get_fragmentos, buscar_fragmentos_por_subcadenas

# ── Configuración ──────────────────────────────────────────────────────────────

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_RAG_TOP_K = 100

# ── Estado interno ─────────────────────────────────────────────────────────────

_embedder: SentenceTransformer | None = None
_index: faiss.IndexFlatL2 | None = None
logger = logging.getLogger(__name__)

# Consultas que piden enumerar / contar (“todas las…”, “cuántas…”, etc.)
_LISTADO_RE = re.compile(
    r"(?i)\b(todas?\s+(las|los)|listar|listado|enumerar|cuánt[oa]s\b|"
    r"dime(\s+todas|\s+los|\s+las)?|cada\s+uno|cada\s+una|hay\s+|existen|muestr[ao])\b"
)

# Palabras de equipo conocidas en el dominio → subcadenas de búsqueda en el texto de fila.
_KEYWORD_TO_PARTS: list[tuple[str, tuple[str, ...]]] = [
    ("trefiladora", ("trefiladora", "trefilador", "trefilación", "trefilacion")),
    ("trefiladoras", ("trefiladora", "trefilador", "trefilación", "trefilacion")),
    ("enconchadora", ("enconchadora", "enconchador")),
    ("enconchadoras", ("enconchadora", "enconchador")),
]


def _terminos_listado_desde_pregunta(pregunta: str) -> list[str]:
    p = pregunta.lower()
    tomados: list[str] = []
    for needle, parts in _KEYWORD_TO_PARTS:
        if needle in p:
            for part in parts:
                if part not in tomados:
                    tomados.append(part)
    return tomados


def _consulta_listado_con_terminos(pregunta: str, terminos: list[str]) -> bool:
    if not terminos:
        return False
    if _LISTADO_RE.search(pregunta):
        return True
    pl = pregunta.lower()
    if re.search(r"(?i)\b(trefiladora|trefilador|enconchadora|enconchador)\b", pl) and re.search(
        r"(?i)\b(cuánt[oa]s|hay|existen|lista|listado|muestra|dime|busca|encuentra)\b",
        pl,
    ):
        return True
    return False


# ── Inicialización ─────────────────────────────────────────────────────────────

def inicializar() -> None:
    """
    Carga el modelo de embeddings y construye el índice FAISS
    a partir de los fragmentos del excel_service.
    Llamar después de excel_service.cargar_excel().
    """
    global _embedder, _index

    logger.info("event=rag_init_start embed_model=%s", EMBED_MODEL)
    _embedder = SentenceTransformer(EMBED_MODEL)

    construir_indice()


def construir_indice() -> None:
    """
    (Re)construye el índice FAISS con los fragmentos actuales.
    Llamar cada vez que se suba un nuevo Excel.
    """
    global _index

    fragmentos = get_fragmentos()
    if not fragmentos:
        raise ValueError("No hay fragmentos disponibles. Carga un Excel primero.")

    logger.info("event=rag_index_build_start rows=%s", len(fragmentos))
    vectores = _embedder.encode(fragmentos, show_progress_bar=True)
    vectores = np.array(vectores, dtype="float32")

    dimension = vectores.shape[1]
    _index = faiss.IndexFlatL2(dimension)
    _index.add(vectores)
    logger.info("event=rag_index_build_done rows=%s dimension=%s", len(fragmentos), dimension)


# ── Búsqueda ───────────────────────────────────────────────────────────────────

def buscar_contexto(pregunta: str, top_k: int = DEFAULT_RAG_TOP_K) -> str:
    """
    Busca las filas más relevantes a la pregunta y las devuelve
    como bloque de texto numerado "Casos Históricos" listo para el prompt.
    """
    if _index is None or _embedder is None:
        raise RuntimeError("El servicio RAG no ha sido inicializado.")

    fragmentos = get_fragmentos()
    n = len(fragmentos)
    if n == 0:
        raise RuntimeError("No hay fragmentos disponibles. Carga un Excel primero.")

    k = min(top_k, n)
    vec = _embedder.encode([pregunta]).astype("float32")
    _, indices = _index.search(vec, k)

    lines = ["Casos Históricos (datos cargados desde Excel):"]
    for rank, idx in enumerate(indices[0][:k], start=1):
        lines.append(f"{rank}. {fragmentos[int(idx)]}")
    return "\n".join(lines)


def construir_contexto_para_chat(
    pregunta: str, top_k: int, listado_max: int
) -> tuple[str, dict]:
    """
    Similarity top_k +, si la pregunta es de listado y hay términos conocidos (p. ej. trefiladora),
    añade todas las filas que contienen esas subcadenas hasta listado_max.
    """
    if _index is None or _embedder is None:
        raise RuntimeError("El servicio RAG no ha sido inicializado.")

    fragmentos = get_fragmentos()
    n = len(fragmentos)
    if n == 0:
        raise RuntimeError("No hay fragmentos disponibles. Carga un Excel primero.")

    k = min(top_k, n)
    vec = _embedder.encode([pregunta]).astype("float32")
    _, indices = _index.search(vec, k)

    sim_frags: list[str] = []
    sim_seen: set[str] = set()
    for idx in indices[0][:k]:
        frag = fragmentos[int(idx)]
        sim_frags.append(frag)
        sim_seen.add(frag)

    terminos = _terminos_listado_desde_pregunta(pregunta)
    extra_frags: list[str] = []
    if listado_max > 0 and _consulta_listado_con_terminos(pregunta, terminos):
        extra_frags = buscar_fragmentos_por_subcadenas(terminos, listado_max)
        extra_frags = [f for f in extra_frags if f not in sim_seen]

    lines = ["Casos Históricos (datos cargados desde Excel):"]
    rank = 1
    for frag in sim_frags:
        lines.append(f"{rank}. {frag}")
        rank += 1
    if extra_frags:
        lines.append("")
        lines.append(
            "Casos adicionales (misma palabra clave en el texto de la fila; útil para listar equipos):"
        )
        for frag in extra_frags:
            lines.append(f"{rank}. {frag}")
            rank += 1

    meta = {
        "total_filas_excel": n,
        "rag_top_k_config": top_k,
        "casos_por_similitud": len(sim_frags),
        "casos_por_coincidencia_texto": len(extra_frags),
        "casos_total_en_contexto": len(sim_frags) + len(extra_frags),
        "listado_por_palabras_clave": bool(extra_frags),
    }
    return "\n".join(lines), meta


def is_ready() -> bool:
    return _embedder is not None and _index is not None

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .excel_service import get_fragmentos

# ── Configuración ──────────────────────────────────────────────────────────────

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ── Estado interno ─────────────────────────────────────────────────────────────

_embedder: SentenceTransformer | None = None
_index: faiss.IndexFlatL2 | None = None


# ── Inicialización ─────────────────────────────────────────────────────────────

def inicializar() -> None:
    """
    Carga el modelo de embeddings y construye el índice FAISS
    a partir de los fragmentos del excel_service.
    Llamar después de excel_service.cargar_excel().
    """
    global _embedder, _index

    print("Cargando modelo de embeddings...")
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

    print(f"Vectorizando {len(fragmentos)} filas...")
    vectores = _embedder.encode(fragmentos, show_progress_bar=True)
    vectores = np.array(vectores, dtype="float32")

    dimension = vectores.shape[1]
    _index = faiss.IndexFlatL2(dimension)
    _index.add(vectores)
    print("Índice FAISS listo ✓")


# ── Búsqueda ───────────────────────────────────────────────────────────────────

def buscar_contexto(pregunta: str, top_k: int = 5) -> str:
    """
    Busca las filas más relevantes a la pregunta y las devuelve
    como un bloque de texto listo para incluir en el prompt.
    """
    if _index is None or _embedder is None:
        raise RuntimeError("El servicio RAG no ha sido inicializado.")

    vec = _embedder.encode([pregunta]).astype("float32")
    _, indices = _index.search(vec, top_k)

    fragmentos = get_fragmentos()
    return "\n".join([fragmentos[i] for i in indices[0]])

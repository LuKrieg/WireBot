import re
import pandas as pd
import logging


# ── Estado interno del servicio ────────────────────────────────────────────────
# Se inicializa al arrancar la app y se reemplaza cuando se sube un nuevo Excel.

_df: pd.DataFrame = pd.DataFrame()
_fragmentos: list[str] = []
_resumen: dict = {}
logger = logging.getLogger(__name__)


# ── Carga ──────────────────────────────────────────────────────────────────────

def cargar_excel(path: str) -> None:
    """
    Carga el archivo Excel en memoria, genera el resumen estadístico
    y prepara los fragmentos de texto para el índice FAISS.
    Llamar al inicio de la app y cada vez que se suba un nuevo archivo.
    """
    global _df, _fragmentos, _resumen

    _df = pd.read_excel(path)
    _df = _reordenar_columnas_equipo_primero(_df)
    _fragmentos = _df.apply(_fila_a_texto, axis=1).tolist()
    _resumen = _generar_resumen(_df)
    logger.info("event=excel_loaded path=%s rows=%s columns=%s", path, len(_df), len(_df.columns))


# ── Acceso a datos ─────────────────────────────────────────────────────────────

def get_fragmentos() -> list[str]:
    """Devuelve la lista de fragmentos de texto (una cadena por fila del Excel)."""
    return _fragmentos


def get_resumen() -> dict:
    """Devuelve el resumen estadístico del documento cargado."""
    return _resumen


def get_dataframe() -> pd.DataFrame:
    """Devuelve el DataFrame completo por si algún servicio lo necesita."""
    return _df


def buscar_fragmentos_por_subcadenas(subcadenas: list[str], max_resultados: int) -> list[str]:
    """
    Filas (fragmentos) donde aparece cualquiera de las subcadenas (sin distinguir mayúsculas).
    Recorre el Excel en el orden de filas cargadas. Útil para listados (“todas las trefiladoras”),
    no para ranking semántico.
    """
    if not subcadenas or max_resultados <= 0:
        return []
    subs = [s.lower() for s in subcadenas if s and len(s) >= 3]
    if not subs:
        return []
    salida: list[str] = []
    for frag in _fragmentos:
        fl = frag.lower()
        if any(s in fl for s in subs):
            salida.append(frag)
            if len(salida) >= max_resultados:
                break
    return salida


# ── Lógica interna ─────────────────────────────────────────────────────────────

_COL_PRIORIDAD = re.compile(
    r"(?i)equipo|máquina|maquina|activo|l[ií]nea|tag|ubic|descrip|detalle|"
    r"falla|paro|area|área|proceso|id\b|c[oó]digo|codigo|referencia|trefil|stn"
)


def _reordenar_columnas_equipo_primero(df: pd.DataFrame) -> pd.DataFrame:
    """Pone al frente columnas que suelen traer nombre/código de máquina (mejor RAG y lectura LLM)."""
    cols = list(df.columns)
    pri = [c for c in cols if _COL_PRIORIDAD.search(str(c))]
    resto = [c for c in cols if c not in pri]
    orden = pri + resto
    return df[orden]


def _fila_a_texto(row) -> str:
    """Convierte una fila del DataFrame en una cadena legible: 'col1: val1 | col2: val2'."""
    return " | ".join([f"{col}: {val}" for col, val in row.items()])

"""
def _generar_resumen(df: pd.DataFrame) -> dict:
    Genera un resumen estadístico estructurado del DataFrame.
    Devuelve un dict con:
      - total_filas
      - columnas
      - categoricas: {col: {valor: conteo, ...}}
      - numericas:   {col: {min, max, suma, promedio}}
    resumen = {
        "total_filas": len(df),
        "columnas": df.columns.tolist(),
        "categoricas": {},
        "numericas": {},
    }

    for col in df.select_dtypes(include=["object"]).columns:
        resumen["categoricas"][col] = df[col].value_counts().to_dict()

    for col in df.select_dtypes(include=["number"]).columns:
        resumen["numericas"][col] = {
            "min": df[col].min(),
            "max": df[col].max(),
            "suma": df[col].sum(),
            "promedio": round(float(df[col].mean()), 2),
        }

    return resumen
"""
    
def _generar_resumen(df: pd.DataFrame) -> dict:
    resumen = {
        "total_filas": int(len(df)),
        "columnas": df.columns.tolist(),
        "categoricas": {},
        "numericas": {},
    }

    for col in df.select_dtypes(include=["object"]).columns:
        resumen["categoricas"][col] = {
            str(k): int(v)
            for k, v in df[col].value_counts().items()
        }

    for col in df.select_dtypes(include=["number"]).columns:
        resumen["numericas"][col] = {
            "min":      float(df[col].min()),
            "max":      float(df[col].max()),
            "suma":     float(df[col].sum()),
            "promedio": round(float(df[col].mean()), 2),
        }

    return resumen
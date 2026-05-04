import pandas as pd


# ── Estado interno del servicio ────────────────────────────────────────────────
# Se inicializa al arrancar la app y se reemplaza cuando se sube un nuevo Excel.

_df: pd.DataFrame = pd.DataFrame()
_fragmentos: list[str] = []
_resumen: dict = {}


# ── Carga ──────────────────────────────────────────────────────────────────────

def cargar_excel(path: str) -> None:
    """
    Carga el archivo Excel en memoria, genera el resumen estadístico
    y prepara los fragmentos de texto para el índice FAISS.
    Llamar al inicio de la app y cada vez que se suba un nuevo archivo.
    """
    global _df, _fragmentos, _resumen

    _df = pd.read_excel(path)
    _fragmentos = _df.apply(_fila_a_texto, axis=1).tolist()
    _resumen = _generar_resumen(_df)


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


# ── Lógica interna ─────────────────────────────────────────────────────────────

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
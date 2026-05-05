import os
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    from app.services.excel_service import cargar_excel, get_resumen
    from app.services.rag_service import inicializar
except Exception as e:
    print("Error importing app modules:", e)
    raise

path = os.path.join(os.getcwd(), "uploads", "datos_enerwire.xlsx")
print("Looking for data file:", path)
if not os.path.exists(path):
    raise FileNotFoundError(path)

print("Cargando Excel...")
cargar_excel(path)
print("Resumen:", get_resumen())

print("Inicializando RAG y reconstruyendo FAISS...")
inicializar()
print("OK: índice reconstruido con datos_enerwire.xlsx")

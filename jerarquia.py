import os
from typing import List, Dict, Any, Optional
from const import ROOT_DIR
from archivos import read_csv_rows

# ----------------------------
# Lectura recursiva de carpetas
# ----------------------------
def recoger_items_recursivo(ruta_actual: str, niveles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    if niveles is None:
        niveles = [None, None, None]

    items_acumulados = []

    try:
        entradas = os.listdir(ruta_actual)
    except FileNotFoundError:
        return []
    except OSError as e:
        print(f"[ERROR] Accediendo a {ruta_actual}: {e}")
        return []

    # Si hay 'items.csv' en esta carpeta, se leen los items y se agregan con su ubicación
    csv_file = os.path.join(ruta_actual, "items.csv")
    if os.path.isfile(csv_file):
        filas = read_csv_rows(csv_file)
        rel = os.path.relpath(ruta_actual, ROOT_DIR)
        partes = rel.split(os.sep)
        n1 = partes[0] if len(partes) > 0 else ""
        n2 = partes[1] if len(partes) > 1 else ""
        n3 = partes[2] if len(partes) > 2 else ""
        for f in filas:
            item = dict(f)
            item["nivel1"] = n1
            item["nivel2"] = n2
            item["nivel3"] = n3
            items_acumulados.append(item)

    # Recorrer subdirectorios
    for entrada in entradas:
        ruta = os.path.join(ruta_actual, entrada)
        if os.path.isdir(ruta):
            items_acumulados.extend(recoger_items_recursivo(ruta))
    return items_acumulados

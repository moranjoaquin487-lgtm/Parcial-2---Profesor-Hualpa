import os
import csv
from typing import List, Dict, Any
from const import CSV_HEADER

# ----------------------------
# Manejo de archivos y CSV
# ----------------------------
def ensure_dir(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"[ERROR] No se pudo crear el directorio {path}: {e}")
        raise


def csv_path_for_levels(root: str, nivel1: str, nivel2: str, nivel3: str) -> str:
    safe_path = os.path.join(root, nivel1, nivel2, nivel3)
    ensure_dir(safe_path)
    return os.path.join(safe_path, "items.csv")


def write_csv_rows(path: str, rows: List[Dict[str, Any]]):
    try:
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            writer.writeheader()
            for r in rows:
                writer.writerow({
                    "id": r["id"],
                    "nombre": r["nombre"],
                    "precio": f"{float(r['precio']):.2f}",
                    "stock": int(r["stock"]),
                    "descripcion": r.get("descripcion", "")
                })
    except Exception as e:
        print(f"[ERROR] Al escribir {path}: {e}")
        raise


def append_csv_row(path: str, row: Dict[str, Any]):
    try:
        file_existed = os.path.exists(path)
        with open(path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            if not file_existed:
                writer.writeheader()
            writer.writerow({
                "id": row["id"],
                "nombre": row["nombre"],
                "precio": f"{float(row['precio']):.2f}",
                "stock": int(row["stock"]),
                "descripcion": row.get("descripcion", "")
            })
    except Exception as e:
        print(f"[ERROR] Al agregar fila a {path}: {e}")
        raise


def read_csv_rows(path: str) -> List[Dict[str, Any]]:
    items = []
    try:
        with open(path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    item = {
                        "id": r["id"],
                        "nombre": r["nombre"],
                        "precio": float(r["precio"]),
                        "stock": int(float(r["stock"])),
                        "descripcion": r.get("descripcion", "")
                    }
                    items.append(item)
                except Exception:
                    print(f"[WARN] Fila con formato inválido en {path}: {r}")
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"[ERROR] Leyendo {path}: {e}")
        raise
    return items

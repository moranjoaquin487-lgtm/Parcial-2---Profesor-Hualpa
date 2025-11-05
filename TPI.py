
import os
import csv
import uuid
from typing import List, Dict, Any, Optional

ROOT_DIR = "data"  # carpeta raíz donde se guardan las jerarquías
CSV_HEADER = ["id", "nombre", "precio", "stock", "descripcion"]


# -----------------------
# Utilidades de archivo
# -----------------------
def ensure_dir(path: str):
    """Crea directorios recursivamente si no existen."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"[ERROR] No se pudo crear el directorio {path}: {e}")
        raise


def csv_path_for_levels(root: str, nivel1: str, nivel2: str, nivel3: str) -> str:
    """
    Construye la ruta segura al csv final para los tres niveles.
    El nombre del archivo será 'items.csv' dentro de la carpeta del nivel3.
    """
    safe_path = os.path.join(root, nivel1, nivel2, nivel3)
    ensure_dir(safe_path)
    return os.path.join(safe_path, "items.csv")


def write_csv_rows(path: str, rows: List[Dict[str, Any]]):
    """Sobrescribe un CSV con las filas provistas (lista de diccionarios)."""
    try:
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            writer.writeheader()
            for r in rows:
                # asegurar que sólo se escriban las columnas esperadas
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
    """Agrega una fila a un CSV; si no existe, lo crea con encabezado."""
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
    """Lee un CSV y devuelve lista de diccionarios (con tipos convertidos)."""
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
                    # salto de fila por formato inválido, pero lo registramos
                    print(f"[WARN] Fila con formato inválido en {path}: {r}")
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"[ERROR] Leyendo {path}: {e}")
        raise
    return items


# -----------------------
# Lectura recursiva
# -----------------------
def recoger_items_recursivo(ruta_actual: str, niveles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Función recursiva que recorre la jerarquía desde 'ruta_actual'
    y devuelve una lista con todos los ítems encontrados en todos los CSV.
    Cada item incluye además las claves 'nivel1','nivel2','nivel3' con su ubicación.
    Caso base: si encuentra un archivo 'items.csv', lo lee y devuelve sus ítems.
    Paso recursivo: si encuentra subdirectorios, llama a sí misma en cada uno.
    """
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

    # Si hay 'items.csv' en esta carpeta, es una carpeta hoja: leer y anexar
    csv_file = os.path.join(ruta_actual, "items.csv")
    if os.path.isfile(csv_file):
        filas = read_csv_rows(csv_file)
        # Derivar niveles desde ruta relativa al ROOT_DIR
        rel = os.path.relpath(ruta_actual, ROOT_DIR)
        partes = rel.split(os.sep)
        n1 = partes[0] if len(partes) > 0 else ""
        n2 = partes[1] if len(partes) > 1 else ""
        n3 = partes[2] if len(partes) > 2 else ""
        for f in filas:
            item = dict(f)  # copia
            item["nivel1"] = n1
            item["nivel2"] = n2
            item["nivel3"] = n3
            items_acumulados.append(item)
        # No recorremos más dentro de una hoja con items.csv (pero si hay subcarpetas, también se leerán abajo)
    # Paso recursivo: para cada subdirectorio, llamar recursivamente
    for entrada in entradas:
        ruta = os.path.join(ruta_actual, entrada)
        if os.path.isdir(ruta):
            items_acumulados.extend(recoger_items_recursivo(ruta))
    return items_acumulados


# -----------------------
# Validaciones de entrada
# -----------------------
def solicitar_no_vacio(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val == "":
            print("No puede estar vacío. Intenta de nuevo.")
        else:
            return val


def solicitar_int(prompt: str, positivo: bool = True) -> int:
    while True:
        s = input(prompt).strip()
        try:
            v = int(float(s))
            if positivo and v <= 0:
                print("El número debe ser mayor que cero.")
            else:
                return v
        except Exception:
            print("Entrada inválida. Escribe un número entero.")


def solicitar_float(prompt: str, positivo: bool = True) -> float:
    while True:
        s = input(prompt).strip()
        try:
            v = float(s)
            if positivo and v <= 0:
                print("El número debe ser mayor que cero.")
            else:
                return v
        except Exception:
            print("Entrada inválida. Escribe un número válido (ej: 199.99).")


# -----------------------
# Operaciones CRUD y util
# -----------------------
def alta_item():
    print("\n--- Alta de nuevo producto (creación jerárquica) ---")
    nivel1 = solicitar_no_vacio("Categoría (nivel 1): ")
    nivel2 = solicitar_no_vacio("Marca (nivel 2): ")
    nivel3 = solicitar_no_vacio("Familia/Modelo (nivel 3): ")
    nombre = solicitar_no_vacio("Nombre del producto: ")
    precio = solicitar_float("Precio (ej: 199.99): ")
    stock = solicitar_int("Stock (entero): ")
    descripcion = input("Descripción (opcional): ").strip()

    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "descripcion": descripcion
    }

    ruta_csv = csv_path_for_levels(ROOT_DIR, nivel1, nivel2, nivel3)
    try:
        append_csv_row(ruta_csv, nuevo)
        print(f"Producto agregado con id={nuevo['id']} en {nivel1}/{nivel2}/{nivel3}")
    except Exception as e:
        print(f"[ERROR] No se pudo agregar el producto: {e}")


def mostrar_items(global_items: List[Dict[str, Any]]):
    if not global_items:
        print("No hay ítems registrados.")
        return
    print("\n--- Ítems registrados ---")
    for it in global_items:
        print(f"id: {it['id']} | nombre: {it['nombre']} | precio: {it['precio']} | stock: {it['stock']} | ubicación: {it.get('nivel1')}/{it.get('nivel2')}/{it.get('nivel3')}")


def filtrar_items(global_items: List[Dict[str, Any]]):
    print("\n--- Filtrado ---")
    if not global_items:
        print("No hay datos para filtrar.")
        return
    print("Atributos disponibles para filtrar: nombre, nivel1, nivel2, nivel3, precio, stock")
    campo = solicitar_no_vacio("Filtrar por (campo): ")
    valor = solicitar_no_vacio("Valor a buscar (para precio/stock puede usar comparadores: >100, <50, =200): ")

    resultados = []
    # soporte simple para comparadores numéricos
    if campo in ("precio", "stock"):
        # parse comparator
        comp = None
        v = valor
        if valor.startswith(">"):
            comp = ">"
            v = valor[1:]
        elif valor.startswith("<"):
            comp = "<"
            v = valor[1:]
        elif valor.startswith("="):
            comp = "="
            v = valor[1:]
        try:
            numv = float(v)
        except Exception:
            print("Valor numérico inválido.")
            return
        for it in global_items:
            try:
                val = float(it[campo])
                ok = False
                if comp == ">":
                    ok = val > numv
                elif comp == "<":
                    ok = val < numv
                elif comp == "=":
                    ok = val == numv
                else:
                    ok = val == numv
                if ok:
                    resultados.append(it)
            except Exception:
                continue
    else:
        # búsqueda por substring (case-insensitive)
        for it in global_items:
            if campo not in it:
                continue
            if valor.lower() in str(it[campo]).lower():
                resultados.append(it)

    print(f"Resultados: {len(resultados)}")
    mostrar_items(resultados)


def buscar_item_por_id(global_items: List[Dict[str, Any]], idbuscado: str) -> Optional[Dict[str, Any]]:
    for it in global_items:
        if it["id"] == idbuscado:
            return it
    return None


def modificar_item():
    print("\n--- Modificación de ítem ---")
    todos = recoger_items_recursivo(ROOT_DIR)
    if not todos:
        print("No hay ítems para modificar.")
        return
    idb = solicitar_no_vacio("Ingresa el id del ítem a modificar: ")
    item = buscar_item_por_id(todos, idb)
    if not item:
        print("Ítem no encontrado.")
        return
    print("Ítem encontrado:")
    print(item)
    attr = solicitar_no_vacio("¿Qué atributo quieres modificar? (nombre, precio, stock, descripcion): ")
    if attr not in ("nombre", "precio", "stock", "descripcion"):
        print("Atributo no válido.")
        return
    # solicitar nuevo valor con validación
    if attr == "nombre":
        nuevo = solicitar_no_vacio("Nuevo nombre: ")
    elif attr == "precio":
        nuevo = solicitar_float("Nuevo precio: ")
    elif attr == "stock":
        nuevo = solicitar_int("Nuevo stock: ")
    else:
        nuevo = input("Nueva descripción (puede quedar vacía): ").strip()

    # Modificar en memoria
    item[attr] = nuevo

    # Ahora reescribir sólo el CSV que contiene este ítem
    ruta_csv = csv_path_for_levels(ROOT_DIR, item.get("nivel1", ""), item.get("nivel2", ""), item.get("nivel3", ""))
    try:
        filas = read_csv_rows(ruta_csv)
        cambiado = False
        for f in filas:
            if f["id"] == idb:
                f[attr] = float(nuevo) if attr == "precio" else (int(nuevo) if attr == "stock" else nuevo)
                cambiado = True
                break
        if not cambiado:
            print("[WARN] No se encontró el ítem en el CSV esperado, puede haber inconsistencia.")
            return
        write_csv_rows(ruta_csv, filas)
        print("Modificación guardada correctamente.")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar la modificación: {e}")


def eliminar_item():
    print("\n--- Eliminación de ítem ---")
    todos = recoger_items_recursivo(ROOT_DIR)
    if not todos:
        print("No hay ítems para eliminar.")
        return
    idb = solicitar_no_vacio("Ingresa el id del ítem a eliminar: ")
    item = buscar_item_por_id(todos, idb)
    if not item:
        print("Ítem no encontrado.")
        return
    ruta_csv = csv_path_for_levels(ROOT_DIR, item.get("nivel1", ""), item.get("nivel2", ""), item.get("nivel3", ""))
    try:
        filas = read_csv_rows(ruta_csv)
        nuevas = [f for f in filas if f["id"] != idb]
        if len(nuevas) == len(filas):
            print("[WARN] El ítem no estaba en el CSV esperado.")
            return
        write_csv_rows(ruta_csv, nuevas)
        print("Ítem eliminado y CSV actualizado.")
    except Exception as e:
        print(f"[ERROR] No se pudo eliminar el ítem: {e}")


def ordenar_items():
    print("\n--- Ordenamiento global ---")
    todos = recoger_items_recursivo(ROOT_DIR)
    if not todos:
        print("No hay ítems para ordenar.")
        return
    print("Atributos disponibles: nombre, precio, stock, nivel1")
    campo = solicitar_no_vacio("Ordenar por (campo): ")
    if campo not in ("nombre", "precio", "stock", "nivel1"):
        print("Campo no válido.")
        return
    sentido = solicitar_no_vacio("Ascendente (A) o Descendente (D)? [A/D]: ").upper()
    reverse = sentido == "D"
    try:
        todos_sorted = sorted(todos, key=lambda x: x.get(campo, ""), reverse=reverse)
        mostrar_items(todos_sorted)
    except Exception as e:
        print(f"[ERROR] Ordenando: {e}")


def estadisticas():
    print("\n--- Estadísticas globales ---")
    todos = recoger_items_recursivo(ROOT_DIR)
    total = len(todos)
    print(f"Cantidad total de ítems: {total}")
    if total == 0:
        return
    # promedio precio
    suma_precio = sum([float(it["precio"]) for it in todos])
    promedio_precio = suma_precio / total
    print(f"Precio promedio: {promedio_precio:.2f}")
    # suma stock
    suma_stock = sum([int(it["stock"]) for it in todos])
    print(f"Suma total de stock: {suma_stock}")
    # recuento por categoria (nivel1)
    conteo_por_n1 = {}
    for it in todos:
        k = it.get("nivel1", "SIN_CATEGORIA")
        conteo_por_n1[k] = conteo_por_n1.get(k, 0) + 1
    print("Recuento por categoría (nivel1):")
    for k, v in conteo_por_n1.items():
        print(f"  {k}: {v}")


# -----------------------
# Menú principal
# -----------------------
def menu():
    ensure_dir(ROOT_DIR)
    opciones = {
        "1": ("Alta de nuevo ítem (crear carpetas si es necesario)", alta_item),
        "2": ("Mostrar todos los ítems (lectura recursiva)", lambda: mostrar_items(recoger_items_recursivo(ROOT_DIR))),
        "3": ("Filtrar ítems", lambda: filtrar_items(recoger_items_recursivo(ROOT_DIR))),
        "4": ("Modificar ítem", modificar_item),
        "5": ("Eliminar ítem", eliminar_item),
        "6": ("Ordenar ítems globalmente", ordenar_items),
        "7": ("Estadísticas y recuentos", estadisticas),
        "0": ("Salir", None)
    }
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        for k, (desc, _) in opciones.items():
            print(f"{k}. {desc}")
        opt = input("Elige una opción: ").strip()
        if opt == "0":
            print("Saliendo. ¡Hasta luego!")
            break
        accion = opciones.get(opt)
        if not accion:
            print("Opción no válida.")
            continue
        try:
            accion[1]()  # ejecutar función
        except Exception as e:
            print(f"[ERROR] Ocurrió un error en la operación: {e}")


if __name__ == "__main__":
    menu()


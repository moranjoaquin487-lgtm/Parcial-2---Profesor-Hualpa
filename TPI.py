import os
import csv
import uuid
from typing import List, Dict, Any, Optional

ROOT_DIR = "data"
CSV_HEADER = ["id", "nombre", "precio", "stock", "descripcion"]


# =====================================================
# VALIDACIONES
# =====================================================

def pedir_texto(msg: str) -> str:
    """Pide un texto no vacío."""
    while True:
        val = input(msg).strip()
        if val:
            return val
        print("Error: el campo no puede estar vacío.")


def pedir_int(msg: str) -> int:
    """Pide un entero válido (positivo o cero)."""
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Error: ingrese un número entero válido.")


def pedir_float(msg: str) -> float:
    """Pide un número decimal válido."""
    while True:
        try:
            return float(input(msg))
        except ValueError:
            print("Error: ingrese un número decimal válido.")


def pedir_opcion(msg: str, opciones: tuple) -> str:
    """Valida que el usuario elija una opción válida."""
    while True:
        val = input(msg).strip().lower()
        if val in opciones:
            return val
        print(f"Opción inválida. Opciones permitidas: {opciones}")


# =====================================================
# ARCHIVOS Y DIRECTORIOS
# =====================================================

def ensure_dir(path: str):
    """Crea un directorio si no existe."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"[ERROR] No se pudo crear el directorio {path}: {e}")
        raise


def csv_path_for_levels(n1: str, n2: str, n3: str) -> str:
    """Devuelve la ruta final del CSV según los 3 niveles."""
    path = os.path.join(ROOT_DIR, n1, n2, n3)
    ensure_dir(path)
    return os.path.join(path, "items.csv")


def leer_csv(path: str) -> List[Dict[str, Any]]:
    """Lee un CSV y devuelve una lista de diccionarios."""
    if not os.path.exists(path):
        return []

    items = []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["precio"] = float(row["precio"])
                row["stock"] = int(row["stock"])
                items.append(row)
    except Exception as e:
        print(f"[ERROR] No se pudo leer {path}: {e}")
    return items


def escribir_csv(path: str, items: List[Dict[str, Any]]):
    """Sobrescribe un CSV con los ítems dados."""
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            writer.writeheader()
            writer.writerows(items)
    except Exception as e:
        print(f"[ERROR] No se pudo escribir {path}: {e}")


# =====================================================
# RECORRIDO RECURSIVO
# =====================================================

def recoger_items_recursivo(ruta_actual: str) -> List[Dict[str, Any]]:
    """
    Recorre recursivamente todas las carpetas a partir de ruta_actual
    y devuelve todos los ítems encontrados en cualquier items.csv.
    """
    todos = []

    # 1) Leer el CSV si existe
    csv_file = os.path.join(ruta_actual, "items.csv")
    if os.path.isfile(csv_file):
        todos.extend(leer_csv(csv_file))

    # 2) Buscar subcarpetas y llamar recursivamente
    try:
        for entrada in os.listdir(ruta_actual):
            ruta = os.path.join(ruta_actual, entrada)
            if os.path.isdir(ruta):
                todos.extend(recoger_items_recursivo(ruta))
    except FileNotFoundError:
        pass

    return todos


# =====================================================
# CRUD
# =====================================================

def alta_item():
    print("\n--- Alta de nuevo ítem ---")

    nivel1 = pedir_texto("Categoría (nivel 1): ")
    nivel2 = pedir_texto("Marca (nivel 2): ")
    nivel3 = pedir_texto("Modelo/Familia (nivel 3): ")

    nombre = pedir_texto("Nombre del producto: ")
    precio = pedir_float("Precio: ")
    stock = pedir_int("Stock: ")
    descripcion = input("Descripción (opcional): ").strip()

    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "descripcion": descripcion
    }

    path = csv_path_for_levels(nivel1, nivel2, nivel3)
    items = leer_csv(path)
    items.append(nuevo)
    escribir_csv(path, items)

    print(f"✓ Producto agregado con ID: {nuevo['id']}")


def mostrar_items():
    print("\n--- Todos los ítems ---")
    items = recoger_items_recursivo(ROOT_DIR)
    if not items:
        print("No hay ítems registrados.")
        return
    for it in items:
        print(it)


def filtrar_items():
    print("\n--- Filtrar ítems ---")
    campo = pedir_texto("Campo (nombre/precio/stock/descripcion): ").lower()
    valor = pedir_texto("Valor a filtrar: ")

    items = recoger_items_recursivo(ROOT_DIR)

    filtrados = [i for i in items if valor.lower() in str(i.get(campo, "")).lower()]

    if filtrados:
        for it in filtrados:
            print(it)
    else:
        print("No se encontraron coincidencias.")


def modificar_item():
    print("\n--- Modificar ítem ---")
    id_buscar = pedir_texto("ID del ítem: ")

    encontrado = None
    ubicacion = None
    lista_original = None

    # Buscar manualmente en cada CSV
    for raiz, dirs, files in os.walk(ROOT_DIR):
        if "items.csv" in files:
            path = os.path.join(raiz, "items.csv")
            lista = leer_csv(path)
            for it in lista:
                if it["id"] == id_buscar:
                    encontrado = it
                    ubicacion = path
                    lista_original = lista
                    break

    if not encontrado:
        print("No se encontró el ítem.")
        return

    print("Actual:", encontrado)
    nuevo_precio = pedir_float("Nuevo precio: ")
    nuevo_stock = pedir_int("Nuevo stock: ")

    # Cambiar en la lista
    encontrado["precio"] = nuevo_precio
    encontrado["stock"] = nuevo_stock

    escribir_csv(ubicacion, lista_original)
    print("✓ Ítem modificado correctamente.")


def eliminar_item():
    print("\n--- Eliminar ítem ---")
    id_buscar = pedir_texto("ID: ")

    for raiz, dirs, files in os.walk(ROOT_DIR):
        if "items.csv" in files:
            path = os.path.join(raiz, "items.csv")
            items = leer_csv(path)
            nuevos = [i for i in items if i["id"] != id_buscar]

            if len(nuevos) != len(items):
                escribir_csv(path, nuevos)
                print("✓ Ítem eliminado.")
                return

    print("No se encontró un ítem con ese ID.")


def ordenar_items():
    print("\n--- Ordenar ítems ---")
    campo = pedir_texto("Ordenar por (nombre/precio/stock): ").lower()
    items = recoger_items_recursivo(ROOT_DIR)

    try:
        ordenados = sorted(items, key=lambda x: x[campo])
        for it in ordenados:
            print(it)
    except KeyError:
        print("Campo inválido.")


def estadisticas():
    print("\n--- Estadísticas globales ---")
    items = recoger_items_recursivo(ROOT_DIR)

    if not items:
        print("No hay datos.")
        return

    precios = [i["precio"] for i in items]
    stocks = [i["stock"] for i in items]

    print("Total de ítems:", len(items))
    print("Precio promedio:", sum(precios) / len(precios))
    print("Stock total:", sum(stocks))


# =====================================================
# MENÚ
# =====================================================

def menu():
    ensure_dir(ROOT_DIR)

    opciones = {
        "1": ("Alta de ítem", alta_item),
        "2": ("Mostrar todos", mostrar_items),
        "3": ("Filtrar", filtrar_items),
        "4": ("Modificar", modificar_item),
        "5": ("Eliminar", eliminar_item),
        "6": ("Ordenar", ordenar_items),
        "7": ("Estadísticas", estadisticas),
        "0": ("Salir", None)
    }

    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        for k, v in opciones.items():
            print(f"{k}. {v[0]}")

        op = input("Elige una opción: ").strip()

        if op == "0":
            print("Saliendo...")
            break

        accion = opciones.get(op)
        if not accion:
            print("Opción inválida.")
            continue

        try:
            accion[1]()
        except Exception as e:
            print("Error durante la ejecución:", e)


if __name__ == "__main__":
    menu()

import uuid
from typing import List, Dict, Any, Optional
from const import ROOT_DIR
from archivos import csv_path_for_levels, append_csv_row, read_csv_rows, write_csv_rows
from jerarquia import recoger_items_recursivo
from validaciones import solicitar_no_vacio, solicitar_float, solicitar_int

# ----------------------------
# Operaciones CRUD y utilitarias
# ----------------------------
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
    append_csv_row(ruta_csv, nuevo)
    print(f"Producto agregado con id={nuevo['id']} en {nivel1}/{nivel2}/{nivel3}")


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
    if campo in ("precio", "stock"):
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

    if attr == "nombre":
        nuevo = solicitar_no_vacio("Nuevo nombre: ")
    elif attr == "precio":
        nuevo = solicitar_float("Nuevo precio: ")
    elif attr == "stock":
        nuevo = solicitar_int("Nuevo stock: ")
    else:
        nuevo = input("Nueva descripción (puede quedar vacía): ").strip()

    item[attr] = nuevo

    ruta_csv = csv_path_for_levels(ROOT_DIR, item.get("nivel1", ""), item.get("nivel2", ""), item.get("nivel3", ""))
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
    filas = read_csv_rows(ruta_csv)
    nuevas = [f for f in filas if f["id"] != idb]
    if len(nuevas) == len(filas):
        print("[WARN] El ítem no estaba en el CSV esperado.")
        return
    write_csv_rows(ruta_csv, nuevas)
    print("Ítem eliminado y CSV actualizado.")


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
    reverse = (sentido == "D")
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
    suma_precio = sum([float(it["precio"]) for it in todos])
    promedio_precio = suma_precio / total
    print(f"Precio promedio: {promedio_precio:.2f}")
    suma_stock = sum([int(it["stock"]) for it in todos])
    print(f"Suma total de stock: {suma_stock}")
    conteo_por_n1 = {}
    for it in todos:
        k = it.get("nivel1", "SIN_CATEGORIA")
        conteo_por_n1[k] = conteo_por_n1.get(k, 0) + 1
    print("Recuento por categoría (nivel1):")
    for k, v in conteo_por_n1.items():
        print(f"  {k}: {v}")

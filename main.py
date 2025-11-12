from const import ROOT_DIR
from archivos import ensure_dir
from jerarquia import recoger_items_recursivo
from operaciones import (
    alta_item, mostrar_items, filtrar_items,
    modificar_item, eliminar_item, ordenar_items, estadisticas
)

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

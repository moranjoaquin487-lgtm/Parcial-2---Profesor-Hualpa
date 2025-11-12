# ----------------------------
# Validaciones de entrada
# ----------------------------
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

# Sistema de Persistencia Jerárquica en Python — Parcial 2 (Programación I)

## 📌 Descripción
Este proyecto implementa un sistema de persistencia jerárquica utilizando Python, archivos CSV y la librería `os`, cumpliendo los requisitos del Parcial 2 de Programación I.

El sistema permite gestionar productos tecnológicos mediante una estructura jerárquica de carpetas y archivos:

- **Nivel 1:** Categoría (Ej: Computadoras, Celulares)
- **Nivel 2:** Marca (Ej: Lenovo, Samsung)
- **Nivel 3:** Modelo/Familia (Ej: IdeaPad, GalaxyA)

Cada carpeta de nivel 3 contiene un archivo `items.csv` con los productos registrados.

---

## 🧠 Conceptos Aplicados

| Concepto | Implementación |
|---|---|
Persistencia | Archivos CSV + estructura de directorios |
Recursividad | Función para recorrer todo el árbol de carpetas |
CRUD completo | Alta, listar/filtrar, modificar y eliminar ítems |
Validaciones | Tipos correctos, valores positivos, no nulos |
IDs únicos | `uuid.uuid4()` |
Excepciones | `try/except` para lectura y escritura |
Ordenamiento | Por nombre, stock, precio, nivel |
Estadísticas | Conteo, promedio, sumatoria, agrupación |

---

## 🗂 Estructura de Archivos


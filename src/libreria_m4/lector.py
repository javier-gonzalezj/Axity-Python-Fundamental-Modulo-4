import json
import math
from itertools import batched
from pathlib import Path

from libreria_m4.excepciones import (
    ArchivoJSONInvalidoError,
    ArchivoNoEncontradoError,
    CodificacionArchivoError,
    LibroInvalidoError,
    PermisoArchivoError,
)
from libreria_m4.utilidades import escritura_atomica

CAMPOS_LIBRO = {
    "isbn": str,
    "titulo": str,
    "autor": dict,
    "genero": list,
    "año_publicacion": int,
    "precio": (int, float),
    "en_stock": bool,
    "cantidad_disponible": int,
    "editorial": str,
}

def validar_libro(libro: dict) -> None:
    """Valida que el diccionario tenga la estructura y tipos esperados de un libro.

    Lanza LibroInvalidoError con un mensaje descriptivo si algo no cumple.
    """
    if not isinstance(libro, dict):
        raise LibroInvalidoError(f"El libro debe ser un diccionario, se recibió {type(libro)}")

    for campo, tipo in CAMPOS_LIBRO.items():
        if campo not in libro:
            raise LibroInvalidoError(f"Falta el campo requerido: '{campo}'")
        if not isinstance(libro[campo], tipo):
            raise LibroInvalidoError(
                f"El campo '{campo}' debe ser de tipo {tipo}, se recibió {type(libro[campo])}"
            )

    # Validaciones de contenido, no solo de tipo
    if not libro["isbn"].strip():
        raise LibroInvalidoError("El ISBN no puede estar vacío")

    if not libro["titulo"].strip():
        raise LibroInvalidoError("El título no puede estar vacío")

    if "nombre" not in libro["autor"] or not isinstance(libro["autor"]["nombre"], str):
        raise LibroInvalidoError("El autor debe tener un campo 'nombre' de tipo str")

    if libro["precio"] < 0:
        raise LibroInvalidoError("El precio no puede ser negativo")

    if libro["cantidad_disponible"] < 0:
        raise LibroInvalidoError("La cantidad disponible no puede ser negativa")

    if libro["año_publicacion"] < 0 or libro["año_publicacion"] > 2100:
        raise LibroInvalidoError(f"El año de publicación ({libro['año_publicacion']}) no es válido")


def agregar_libro(data: dict, libro: dict) -> dict:
    """Agrega un nuevo libro al catálogo, validando su estructura y que el ISBN no exista ya."""
    validar_libro(libro)

    isbn_existente = {libro["isbn"] for libro in data["libros"]}
    if libro["isbn"] in isbn_existente:
        raise LibroInvalidoError(f"Ya existe un libro con ISBN {libro['isbn']}")

    data["libros"].append(libro)
    return data


def cargar_datos(ruta: str | Path) -> dict:
    """Carga y devuelve los datos de la librería desde un archivo JSON."""
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ArchivoNoEncontradoError(f"No se encontró el archivo: {ruta}") from None
    except PermissionError:
        raise PermisoArchivoError(f"Sin permisos para leer el archivo: {ruta}") from None
    except UnicodeDecodeError:
        raise CodificacionArchivoError(
            f"El archivo {ruta} no está codificado en UTF-8. "
            "Vuelve a guardarlo con esa codificación."
        ) from None
    except json.JSONDecodeError as e:
        raise ArchivoJSONInvalidoError(
            f"El archivo {ruta} no contiene JSON válido (línea {e.lineno}, columna {e.colno})"
        ) from None


def guardar_datos(ruta: str | Path, data: dict) -> None:
    """Guarda los datos de la librería en el archivo JSON."""
    ruta = Path(ruta)
    try:
        with escritura_atomica(ruta) as f:
            # Aqui se modifico el codigo para poder hacer uso del context manager creado arriba
            json.dump(data, f, ensure_ascii=False, indent=2)
    except PermissionError:
        raise PermisoArchivoError(f"Sin permisos para escribir el archivo: {ruta}") from None
    except FileNotFoundError:
        raise ArchivoNoEncontradoError(f"No existe la carpeta de destino: {ruta.parent}") from None


def _mostrar_libro(libro: dict) -> None:
    """Imprime los datos de un solo libro."""
    disponibilidad = "✅ Disponible" if libro["en_stock"] else "❌ Agotado"
    print(f"\n{libro['titulo']} ({libro['año_publicacion']})")
    print(f"  Autor: {libro['autor']['nombre']} ({libro['autor']['nacionalidad']})")
    print(f"  Género: {', '.join(libro['genero'])}")
    print(f"  Precio: ${libro['precio']:.2f}")
    print(f"  {disponibilidad} — {libro['cantidad_disponible']} unidades")


def mostrar_libreria(data: dict, por_pagina: int = 5) -> None:
    """
    Imprime la información de la librería y su catálogo,
    paginado de `por_pagina` en `por_pagina`.
    """

    print(f"📚 {data['nombre']}")
    print(
        f"📍 {data['direccion']['calle']}, "
        f"{data['direccion']['colonia']}, "
        f"{data['direccion']['ciudad']}"
    )
    print(f"📞 {data['telefono']}")
    print(f"🕒 {data['horario']}")
    print("-" * 40)

    libros = data["libros"]
    total_paginas = math.ceil(len(libros) / por_pagina)

    for num, pagina in enumerate(batched(libros, por_pagina, strict=False), start=1):
        print(f"\n── Página {num} de {total_paginas} ──")
        for libro in pagina:
            _mostrar_libro(libro)

        if num < total_paginas:
            respuesta = input("\nEnter para ver más, 'q' para terminar: ").strip().lower()
            if respuesta == "q":
                break

    print("\n" + "=" * 40)
    print(f"Total de libros: {len(libros)}")
    valor_total = sum(libro["precio"] * libro["cantidad_disponible"] for libro in libros)
    print(f"Valor total del inventario: ${valor_total:.2f}")


def mostrar_libros(libros: list[dict]) -> None:
    """Imprime una lista de libros (útil para mostrar resultados filtrados)."""
    if not libros:
        print("No se encontraron libros con esos criterios.")
        return

    for libro in libros:
        _mostrar_libro(libro)

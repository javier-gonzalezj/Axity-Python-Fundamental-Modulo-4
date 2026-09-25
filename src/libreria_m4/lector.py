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
from libreria_m4.modelos import Libro
from libreria_m4.utilidades import escritura_atomica


def agregar_libro(data: dict, libro: Libro) -> dict:
    """Agrega un nuevo libro al catálogo, verificando que el ISBN no exista ya.

    La validación de la estructura ya la hizo el modelo Libro al crearse.
    """
    isbn_existentes = {existente.isbn for existente in data["libros"]}
    if libro.isbn in isbn_existentes:
        raise LibroInvalidoError(f"Ya existe un libro con ISBN {libro.isbn}")

    data["libros"].append(libro)
    return data


def cargar_datos(ruta: str | Path) -> dict:
    """Carga los datos de la librería desde un archivo JSON.

    Los libros se convierten a objetos Libro (validados); el resto de los datos
    de la librería se queda como diccionario.
    """
    try:
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
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

    if not isinstance(data.get("libros"), list):
        raise ArchivoJSONInvalidoError(f"El archivo {ruta} no tiene una lista 'libros'")

    # Conversión a entidad: cada dict del JSON se vuelve un Libro validado
    data["libros"] = [Libro.desde_dict(libro) for libro in data["libros"]]
    return data


def guardar_datos(ruta: str | Path, data: dict) -> None:
    """Guarda los datos de la librería en el archivo JSON."""
    ruta = Path(ruta)

    # Serialización: cada Libro se vuelve dict. Se crea una copia para no
    # modificar `data`, que el programa sigue usando con objetos Libro.
    data_json = {**data, "libros": [libro.a_dict() for libro in data["libros"]]}

    try:
        with escritura_atomica(ruta) as f:
            json.dump(data_json, f, ensure_ascii=False, indent=2)
    except PermissionError:
        raise PermisoArchivoError(f"Sin permisos para escribir el archivo: {ruta}") from None
    except FileNotFoundError:
        raise ArchivoNoEncontradoError(f"No existe la carpeta de destino: {ruta.parent}") from None


def _mostrar_libro(libro: Libro) -> None:
    """Imprime los datos de un solo libro."""
    disponibilidad = "✅ Disponible" if libro.en_stock else "❌ Agotado"
    print(f"\n{libro.titulo} ({libro.año_publicacion})")
    print(f"  Autor: {libro.autor.nombre} ({libro.autor.nacionalidad})")
    print(f"  Género: {', '.join(libro.genero)}")
    print(f"  Precio: ${libro.precio:.2f}")
    print(f"  {disponibilidad} — {libro.cantidad_disponible} unidades")


def mostrar_libreria(data: dict, por_pagina: int = 5) -> None:
    """
    Imprime la información de la librería y su catálogo ordenado,
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

    libros = sorted(data["libros"])  # usa Libro.__lt__: año, título, ISBN
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
    valor_total = sum(libro.precio * libro.cantidad_disponible for libro in libros)
    print(f"Valor total del inventario: ${valor_total:.2f}")


def mostrar_libros(libros: list[Libro]) -> None:
    """Imprime una lista de libros ordenada (útil para mostrar resultados filtrados)."""
    if not libros:
        print("No se encontraron libros con esos criterios.")
        return

    for libro in sorted(libros):
        _mostrar_libro(libro)

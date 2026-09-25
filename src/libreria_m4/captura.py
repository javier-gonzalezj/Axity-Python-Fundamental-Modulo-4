def capturar_libro(data: dict) -> dict:
    """Solicita al usuario los datos de un nuevo libro por consola."""
    print("\n📖 Nuevo libro")
    print("-" * 40)

    isbn_existente = {libro.isbn for libro in data["libros"]}
    while True:
        isbn = input("ISBN: ").strip()
        if isbn in isbn_existente:
            print("  ⚠️  Ya existe un libro con ese ISBN. Intenta con otro.")
            continue
        if not isbn:
            print("  ⚠️  El ISBN no puede estar vacío.")
            continue
        break

    titulo = input("Título: ").strip()
    nombre_autor = input("Nombre del autor: ").strip()
    nacionalidad_autor = input("Nacionalidad del autor: ").strip()

    generos_texto = input("Género(s) (separados por coma): ").strip()
    generos = [g.strip() for g in generos_texto.split(",") if g.strip()]

    while True:
        try:
            año = int(input("Año de publicación: ").strip())
            break
        except ValueError:
            print("  ⚠️  Ingresa un número válido para el año.")

    while True:
        try:
            precio = float(input("Precio: ").strip())
            if precio < 0:
                print("  ⚠️  El precio no puede ser negativo.")
                continue
            break
        except ValueError:
            print("  ⚠️  Ingresa un número válido para el precio.")

    while True:
        try:
            cantidad = int(input("Cantidad disponible: ").strip())
            if cantidad < 0:
                print("  ⚠️  La cantidad no puede ser negativa.")
                continue
            break
        except ValueError:
            print("  ⚠️  Ingresa un número entero válido.")

    editorial = input("Editorial: ").strip()

    return {
        "isbn": isbn,
        "titulo": titulo,
        "autor": {"nombre": nombre_autor, "nacionalidad": nacionalidad_autor},
        "genero": generos,
        "año_publicacion": año,
        "precio": precio,
        "en_stock": cantidad > 0,
        "cantidad_disponible": cantidad,
        "editorial": editorial,
    }


def filtrar_libros(
    data: dict,
    autor: str | None = None,
    genero: str | None = None,
    en_stock: bool | None = None,
    precio_max: float | None = None,
    año_min: int | None = None,
) -> list[dict]:
    """Filtra el catálogo de libros según los criterios indicados.

    Cualquier parámetro que se deje en None se ignora (no filtra por ese campo).
    """
    resultado = data["libros"]

    if autor is not None:
        resultado = [
            libro for libro in resultado if autor.lower() in libro.autor.nombre.lower()
        ]

    if genero is not None:
        resultado = [
            libro
            for libro in resultado
            if any(genero.lower() in g.lower() for g in libro.genero)
        ]

    if en_stock is not None:
        resultado = [libro for libro in resultado if libro.en_stock == en_stock]

    if precio_max is not None:
        resultado = [libro for libro in resultado if libro.precio <= precio_max]

    if año_min is not None:
        resultado = [libro for libro in resultado if libro.año_publicacion >= año_min]

    return resultado


def capturar_filtros(data: dict) -> list[dict]:
    """Pregunta al usuario qué filtros quiere aplicar y devuelve el resultado."""

    print("\n🔍 Filtrar libros")
    print("(deja el campo vacío para no filtrar por ese criterio)")
    print("-" * 40)

    autor = input("Autor: ").strip() or None

    genero = input("Género: ").strip() or None

    en_stock_texto = input("¿Solo en stock? (s/n, vacío = no filtrar): ").strip().lower()
    if en_stock_texto == "s":
        en_stock = True
    elif en_stock_texto == "n":
        en_stock = False
    else:
        en_stock = None

    precio_max_texto = input("Precio máximo: ").strip()
    precio_max = None
    if precio_max_texto:
        try:
            precio_max = float(precio_max_texto)
        except ValueError:
            print("  ⚠️  Precio inválido, se ignora este filtro.")

    año_min_texto = input("Año de publicación mínimo: ").strip()
    año_min = None
    if año_min_texto:
        try:
            año_min = int(año_min_texto)
        except ValueError:
            print("  ⚠️  Año inválido, se ignora este filtro.")

    return filtrar_libros(
        data,
        autor=autor,
        genero=genero,
        en_stock=en_stock,
        precio_max=precio_max,
        año_min=año_min,
    )

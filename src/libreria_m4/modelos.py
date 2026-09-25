from dataclasses import asdict, dataclass, field

from libreria_m4.excepciones import LibroInvalidoError


@dataclass(frozen=True, order=True)
class Autor:
    """Define al autor del libro: ordena alfabéticamente por nombre y nacionalidad."""

    nombre: str
    nacionalidad: str = ""

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise LibroInvalidoError("El nombre del autor no puede estar vacío")


@dataclass(order=True)
class Libro:
    """Define un libro del catálogo.

    Se ordena por año de publicación, luego por título y al final por ISBN.
    El resto de campos no participan en las comparaciones.
    """

    # Campos que definen el orden (en este orden)
    año_publicacion: int
    titulo: str
    isbn: str

    # Campos que no participan en la comparacion
    autor: Autor = field(compare=False)
    genero: list[str] = field(compare=False)
    precio: float = field(compare=False)
    en_stock: bool = field(compare=False)
    cantidad_disponible: int = field(compare=False)
    editorial: str = field(compare=False)

    def __post_init__(self) -> None:
        """Validaciones de contenido que antes hacía validar_libro()."""
        if not self.isbn.strip():
            raise LibroInvalidoError("El ISBN no puede estar vacío")

        if not self.titulo.strip():
            raise LibroInvalidoError("El título no puede estar vacío")

        if self.precio < 0:
            raise LibroInvalidoError("El precio no puede ser negativo")

        if self.cantidad_disponible < 0:
            raise LibroInvalidoError("La cantidad disponible no puede ser negativa")

        if not 0 <= self.año_publicacion <= 2100:
            raise LibroInvalidoError(f"El año de publicación ({self.año_publicacion}) no es válido")

    @classmethod
    def desde_dict(cls, datos: dict) -> "Libro":
        """Crea un Libro a partir de un diccionario como los del archivo JSON."""
        try:
            autor = Autor(**datos["autor"])
            return cls(**{**datos, "autor": autor})
        except KeyError as e:
            raise LibroInvalidoError(f"Falta el campo requerido: {e}") from None
        except TypeError as e:
            raise LibroInvalidoError(f"Estructura de libro inválida: {e}") from None

    def a_dict(self) -> dict:
        """Convierte el Libro (incluyendo su Autor) a diccionario para guardarlo en JSON."""
        return asdict(self)
    
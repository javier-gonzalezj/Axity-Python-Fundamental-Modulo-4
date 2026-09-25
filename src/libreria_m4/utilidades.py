import time
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def cronometro(etiqueta: str = "Bloque") -> Iterator[None]:
    """Context manager de temporizacion: Imprime cuanto tiempo
    tardo en ejecutarse el bloque with aunque falle.
    """
    inicio = time.perf_counter()
    try:
        yield
    finally:
        duracion = time.perf_counter() - inicio
        print(f"{etiqueta}: {duracion:.4f}s")

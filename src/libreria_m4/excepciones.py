class LibreriaError(Exception):
    """Excepción base para errores del proyecto libreria."""


class ArchivoNoEncontradoError(LibreriaError):
    """Se lanza cuando el archivo JSON de la librería no existe."""


class ArchivoJSONInvalidoError(LibreriaError):
    """Se lanza cuando el archivo existe pero su contenido no es JSON válido."""


class PermisoArchivoError(LibreriaError):
    """Se lanza cuando no hay permisos para leer o escribir el archivo."""


class CodificacionArchivoError(LibreriaError):
    """Se lanza cuando el archivo no está codificado en UTF-8 (o similar)."""


class LibroInvalidoError(LibreriaError):
    """Se lanza cuando un diccionario de libro no cumple con la estructura esperada."""

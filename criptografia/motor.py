"""Punto de entrada común para todas las interfaces."""

from .config import ALGORITMOS, MODOS, MODOS_POR_ALGORITMO
from .validaciones import ErrorValidacion, validar_mensaje
from . import algoritmos, analisis

OPERACIONES = {
    ("afin", "cifrar"): algoritmos.cifrar_afin,
    ("afin", "descifrar"): algoritmos.descifrar_afin,
    ("cesar", "cifrar"): algoritmos.cifrar_cesar,
    ("cesar", "descifrar"): algoritmos.descifrar_cesar,
    ("sustitucion", "cifrar"): algoritmos.cifrar_sustitucion,
    ("sustitucion", "descifrar"): algoritmos.descifrar_sustitucion,
    ("vigenere", "cifrar"): algoritmos.cifrar_vigenere,
    ("vigenere", "descifrar"): algoritmos.descifrar_vigenere,
}
ANALISIS = {"cesar": analisis.fuerza_bruta_cesar, "afin": analisis.fuerza_bruta_afin}


def ejecutar(algoritmo, modo, mensaje, clave=None):
    if not isinstance(algoritmo, str) or algoritmo not in ALGORITMOS:
        raise ErrorValidacion("Selecciona un algoritmo válido.", "algoritmo")
    if not isinstance(modo, str) or modo not in MODOS_POR_ALGORITMO[algoritmo]:
        raise ErrorValidacion("Selecciona una operación válida.", "modo")
    validar_mensaje(mensaje)
    if modo == "analizar":
        return ANALISIS[algoritmo](mensaje)
    return OPERACIONES[(algoritmo, modo)](mensaje, clave)

"""Herramientas educativas; ninguna estimación se declara clave confirmada."""

from collections import Counter, defaultdict
from .config import ALFABETO, CARACTERES_PERMITIDOS, MAXIMO_ANALISIS
from .validaciones import validar_mensaje, ErrorValidacion
from .algoritmos import descifrar_cesar


def _letras(mensaje):
    validar_mensaje(mensaje)
    if len(mensaje) > MAXIMO_ANALISIS:
        raise ErrorValidacion(f"El análisis admite hasta {MAXIMO_ANALISIS} caracteres. No se ha recortado el mensaje.")
    return "".join(c.upper() for c in mensaje if CARACTERES_PERMITIDOS[c]["tipo"] == "letra")


def fuerza_bruta_cesar(mensaje):
    letras = _letras(mensaje)
    candidatos = [descifrar_cesar(mensaje, clave) for clave in range(1, 26)]
    return {"tipo": "fuerza_bruta", "algoritmo": "cesar", "modo": "analizar", "mensaje": mensaje,
            "candidatos": candidatos, "total_letras": len(letras),
            "explicacion": "Se prueban 25 desplazamientos no triviales. La clave 0 deja el texto intacto. Ningún candidato se elige automáticamente."
            + (" El mensaje no contiene letras; todos los candidatos son idénticos y no permiten inferir una clave." if not letras else "")}


def fuerza_bruta_afin(mensaje):
    """Enumera 312 claves; las trazas completas se calculan al solicitar un candidato."""
    from .algoritmos import descifrar_afin
    letras = _letras(mensaje)
    candidatos = []
    for a in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        for b in range(26):
            registro = descifrar_afin(mensaje, {"a": a, "b": b})
            candidatos.append({"clave": registro["clave"], "clave_efectiva": {"a": a, "b": b},
                               "resultado": registro["resultado"], "identidad": a == 1 and b == 0})
    return {"tipo": "fuerza_bruta", "algoritmo": "afin", "modo": "analizar", "mensaje": mensaje,
            "candidatos": candidatos, "total_letras": len(letras), "total_claves": 312,
            "explicacion": "12 multiplicadores coprimos con 26 × 26 desplazamientos = 312 claves. Incluye a=1, b=0, que conserva el texto. Ningún candidato está confirmado."
            + (" No hay letras: todos los candidatos coinciden." if not letras else "")}

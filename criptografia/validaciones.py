"""Validación estricta previa al procesamiento; no normaliza el mensaje."""

import re
from .config import (ALFABETO, ALFABETO_INGLES, CARACTERES_PERMITIDOS,
                     MAXIMO_MENSAJE, MAXIMO_CLAVE)


class ErrorValidacion(ValueError):
    def __init__(self, mensaje, campo="mensaje", detalles=None):
        super().__init__(mensaje)
        self.campo = campo
        self.detalles = detalles or []


def validar_mensaje(mensaje):
    if not isinstance(mensaje, str):
        raise ErrorValidacion("El mensaje debe ser texto.")
    if not mensaje:
        raise ErrorValidacion("Ingresa un mensaje para continuar.")
    if len(mensaje) > MAXIMO_MENSAJE:
        raise ErrorValidacion(f"El máximo es {MAXIMO_MENSAJE} caracteres. El texto no se ha recortado.")
    errores, linea, columna, anterior = [], 1, 1, ""
    for posicion, caracter in enumerate(mensaje, 1):
        if caracter not in CARACTERES_PERMITIDOS:
            errores.append({"caracter": caracter, "posicion": posicion,
                            "linea": linea, "columna": columna})
        if caracter == "\r":
            linea, columna = linea + 1, 1
        elif caracter == "\n":
            linea, columna = linea + (anterior != "\r"), 1
        else:
            columna += 1
        anterior = caracter
    if errores:
        primero = errores[0]
        simbolo = repr(primero["caracter"])
        raise ErrorValidacion(
            f"Símbolo no permitido: {simbolo} (línea {primero['linea']}, "
            f"columna {primero['columna']}). Se encontraron {len(errores)} "
            "caracteres fuera de la configuración. Corrige el mensaje para continuar.",
            detalles=errores,
        )
    return mensaje


def validar_desplazamiento(clave):
    if isinstance(clave, bool):
        raise ErrorValidacion("El desplazamiento debe ser un entero.", "clave")
    texto = str(clave) if isinstance(clave, (str, int)) else ""
    if not re.fullmatch(r"[+-]?[0-9]{1,100}", texto):
        raise ErrorValidacion("Ingresa un desplazamiento entero, por ejemplo 3, 0 o -3.", "clave")
    return int(texto)


def validar_clave_letras(clave):
    if not isinstance(clave, str) or not clave:
        raise ErrorValidacion("La clave Vigenère no puede estar vacía.", "clave")
    if len(clave) > MAXIMO_CLAVE:
        raise ErrorValidacion(f"La clave admite hasta {MAXIMO_CLAVE} letras.", "clave")
    if any(c not in CARACTERES_PERMITIDOS or CARACTERES_PERMITIDOS[c]["tipo"] != "letra" for c in clave):
        raise ErrorValidacion("La clave debe contener solo letras inglesas A-Z, sin espacios, números ni acentos.", "clave")
    return clave.upper()


def validar_alfabeto_sustituto(clave):
    if not isinstance(clave, str) or len(clave) != len(ALFABETO):
        raise ErrorValidacion("El alfabeto sustituto debe tener exactamente 26 letras inglesas.", "clave")
    if any(c not in CARACTERES_PERMITIDOS or CARACTERES_PERMITIDOS[c]["tipo"] != "letra" for c in clave):
        raise ErrorValidacion("El alfabeto sustituto solo admite letras inglesas A-Z.", "clave")
    normalizada = clave.upper()
    if set(normalizada) != set(ALFABETO_INGLES) or len(set(normalizada)) != len(ALFABETO):
        raise ErrorValidacion("El alfabeto sustituto debe incluir las 26 letras, sin duplicados.", "clave")
    return normalizada


def validar_clave_afin(clave):
    from math import gcd
    if not isinstance(clave, dict) or set(clave) != {"a", "b"}:
        raise ErrorValidacion("La clave Afín debe contener a y b.", "clave-a")
    valores = {}
    for nombre in ("a", "b"):
        try:
            valores[nombre] = validar_desplazamiento(clave[nombre]) % 26
        except ErrorValidacion:
            raise ErrorValidacion(f"El valor de {nombre} debe ser un entero.", "clave-" + nombre)
    if gcd(valores["a"], 26) != 1:
        raise ErrorValidacion("El multiplicador a debe ser coprimo con 26. Valores válidos: 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25.", "clave-a")
    return valores

"""Menú de terminal con la misma configuración y funciones que Flask."""

import argparse
from criptografia.config import ADVERTENCIA, ALGORITMOS
from criptografia.motor import ejecutar
from criptografia.validaciones import ErrorValidacion

MENU = """
SISTEMA DE ENCRIPTACIÓN CLÁSICA
1. Cifrado César
2. Descifrado César
3. Cifrado de sustitución simple
4. Descifrado de sustitución simple
5. Cifrado Vigenère
6. Descifrado Vigenère
7. Información de los algoritmos
8. Cifrado Afín
9. Descifrado Afín
10. Fuerza bruta César
11. Fuerza bruta Afín
0. Salir
"""
OPCIONES = {"8": ("afin", "cifrar"), "9": ("afin", "descifrar"),
            "10": ("cesar", "analizar"), "11": ("afin", "analizar"),"1": ("cesar", "cifrar"), "2": ("cesar", "descifrar"),
            "3": ("sustitucion", "cifrar"), "4": ("sustitucion", "descifrar"),
            "5": ("vigenere", "cifrar"), "6": ("vigenere", "descifrar")}


def leer_mensaje():
    mensaje = input("Mensaje (o /multi para varias líneas): ")
    if mensaje != "/multi":
        return mensaje
    print("Escribe el mensaje. Termina con /fin en una línea independiente.")
    lineas = []
    while True:
        linea = input()
        if linea == "/fin":
            return "\n".join(lineas)
        lineas.append(linea)


def main(mostrar_pasos=False):
    print(ADVERTENCIA)
    while True:
        print(MENU)
        opcion = input("Seleccione una opción: ")
        if opcion == "0":
            print("Sesión finalizada.")
            return
        if opcion == "7":
            print("César: C=(P+k) mod 26; clave entera; vulnerable a fuerza bruta.")
            print("Sustitución: permutación biyectiva A-Z; vulnerable a frecuencias.")
            print("Vigenère: Cᵢ=(Pᵢ+Kᵢ) mod 26; clave repetida; Kasiski orienta su longitud.")
            print("Afín: C=(aP+b) mod 26; a coprimo con 26; 312 claves válidas.")
            print("Solo letras inglesas. Los caracteres fuera de config.py se rechazan.")
            continue
        if opcion not in OPCIONES:
            print("Opción no válida. Selecciona una opción del menú.")
            continue
        algoritmo, modo = OPCIONES[opcion]
        mensaje = leer_mensaje()
        etiqueta = {"cesar": "Desplazamiento entero", "sustitucion": "Permutación de 26 letras", "vigenere": "Clave A-Z", "afin": "Clave Afín"}[algoritmo]
        clave = None if modo == "analizar" else ({"a": input("Multiplicador a: "), "b": input("Desplazamiento b: ")} if algoritmo == "afin" else input(f"{etiqueta}: "))
        try:
            resultado = ejecutar(algoritmo, modo, mensaje, clave)
        except ErrorValidacion as error:
            print(f"Error: {error}")
            continue
        print(f"Método: {ALGORITMOS[algoritmo]} | Operación: {modo}")
        print(f"Mensaje original: {mensaje}")
        if resultado["tipo"] == "fuerza_bruta":
            print(resultado["explicacion"])
            for candidato in resultado["candidatos"]:
                print(f"Clave {candidato['clave']}: {candidato['resultado']}")
            continue
        print(f"Resultado: {resultado['resultado']}")
        if mostrar_pasos:
            print(f"Fórmula: {resultado['formula']}")
            for paso in resultado["pasos"]:
                print(f"{paso['posicion']}. {paso['entrada']!r}: {paso['calculo']} → {paso['salida']!r}")


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--pasos", action="store_true", help="Imprime todos los cálculos.")
    opciones = argumentos.parse_args()
    try:
        main(opciones.pasos)
    except (EOFError, KeyboardInterrupt):
        print("\nSesión finalizada.")

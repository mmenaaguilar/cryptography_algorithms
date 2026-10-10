"""Resultados y trazas se generan juntos, sin una segunda simulación."""

from .config import ALFABETO, CARACTERES_PERMITIDOS, TAMANO_ALFABETO
from .validaciones import (validar_mensaje, validar_desplazamiento,
                          validar_clave_letras, validar_alfabeto_sustituto)


def _transformar(mensaje, algoritmo, modo, clave):
    validar_mensaje(mensaje)
    cifrar = modo == "cifrar"
    if algoritmo == "cesar":
        clave = validar_desplazamiento(clave)
        efectiva = clave % TAMANO_ALFABETO
        formula = "C = (P + k) mod 26" if cifrar else "P = (C - k) mod 26"
    elif algoritmo == "sustitucion":
        clave = validar_alfabeto_sustituto(clave)
        efectiva = clave
        mapa = dict(zip(ALFABETO, clave)) if cifrar else dict(zip(clave, ALFABETO))
        formula = "Salida = mapa[entrada]" if cifrar else "Salida = mapa_inverso[entrada]"
    else:
        clave = validar_clave_letras(clave)
        efectiva = clave
        formula = "Cᵢ = (Pᵢ + Kᵢ) mod 26" if cifrar else "Pᵢ = (Cᵢ - Kᵢ) mod 26"

    pasos, salida, indice_letra = [], [], 0
    for posicion, caracter in enumerate(mensaje, 1):
        dato = CARACTERES_PERMITIDOS[caracter]
        paso = {"posicion": posicion, "entrada": caracter, "letra": dato["tipo"] == "letra"}
        if dato["tipo"] != "letra":
            paso.update({"salida": caracter, "valor_entrada": None, "valor_salida": None,
                         "clave_letra": None, "valor_clave": None, "indice_clave": None,
                         "numero_letra": None, "calculo": "Se conserva; no consume clave."})
        else:
            valor = dato["valor"]
            indice_letra += 1
            paso.update({"valor_entrada": valor, "numero_letra": indice_letra,
                         "clave_letra": None, "valor_clave": None, "indice_clave": None})
            if algoritmo == "sustitucion":
                letra_salida = mapa[ALFABETO[valor]]
                resultado = ALFABETO.index(letra_salida)
                calculo = f"{ALFABETO[valor]} → {letra_salida} (mapa {'directo' if cifrar else 'inverso'})"
            else:
                if algoritmo == "vigenere":
                    indice = (indice_letra - 1) % len(clave)
                    letra_clave = clave[indice]
                    valor_clave = CARACTERES_PERMITIDOS[letra_clave]["valor"]
                    paso.update({"clave_letra": letra_clave, "valor_clave": valor_clave,
                                 "indice_clave": indice + 1})
                else:
                    valor_clave = efectiva
                    paso["valor_clave"] = efectiva
                total = valor + valor_clave if cifrar else valor - valor_clave
                resultado = total % TAMANO_ALFABETO
                operador = "+" if cifrar else "-"
                calculo = f"({valor} {operador} {valor_clave}) mod 26 = {resultado}"
                paso["antes_modulo"] = total
                letra_salida = ALFABETO[resultado]
            paso.update({"valor_salida": resultado, "calculo": calculo,
                         "salida": letra_salida if dato["mayuscula"] else letra_salida.lower()})
        salida.append(paso["salida"])
        pasos.append(paso)
    return {"tipo": "transformacion", "algoritmo": algoritmo, "modo": modo,
            "mensaje": mensaje, "clave": str(clave), "clave_efectiva": efectiva,
            "formula": formula, "alfabeto": ALFABETO, "pasos": pasos,
            "resultado": "".join(salida), "total_letras": indice_letra}


def cifrar_cesar(mensaje, clave):
    """Cifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar(mensaje, "cesar", "cifrar", clave)


def descifrar_cesar(mensaje, clave):
    """Descifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar(mensaje, "cesar", "descifrar", clave)


def cifrar_sustitucion(mensaje, clave):
    """Cifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar(mensaje, "sustitucion", "cifrar", clave)


def descifrar_sustitucion(mensaje, clave):
    """Descifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar(mensaje, "sustitucion", "descifrar", clave)


def cifrar_vigenere(mensaje, clave):
    """Cifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar(mensaje, "vigenere", "cifrar", clave)


def descifrar_vigenere(mensaje, clave):
    """Descifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar(mensaje, "vigenere", "descifrar", clave)


def inverso_modular(a, modulo=26):
    """Euclides extendido: devuelve el inverso y los cocientes realmente usados."""
    r0, r1, t0, t1 = modulo, a, 0, 1
    pasos = []
    while r1:
        cociente = r0 // r1
        resto = r0 - cociente * r1
        nuevo_t = t0 - cociente * t1
        pasos.append({"dividendo": r0, "divisor": r1, "cociente": cociente,
                      "resto": resto, "t_anterior": t0, "t_actual": t1, "t_nuevo": nuevo_t})
        r0, r1, t0, t1 = r1, resto, t1, nuevo_t
    if r0 != 1:
        raise ValueError("El multiplicador no tiene inverso modular.")
    return t0 % modulo, pasos


def _transformar_afin(mensaje, modo, clave):
    """Produce resultado y procedimiento en la misma operación."""
    from .validaciones import validar_clave_afin
    validar_mensaje(mensaje)
    efectiva = validar_clave_afin(clave)
    a, b = efectiva["a"], efectiva["b"]
    inverso, euclides = inverso_modular(a)
    cifrar = modo == "cifrar"
    pasos, salida, numero = [], [], 0
    for posicion, caracter in enumerate(mensaje, 1):
        dato = CARACTERES_PERMITIDOS[caracter]
        paso = {"posicion": posicion, "entrada": caracter, "letra": dato["tipo"] == "letra",
                "valor_entrada": None, "valor_salida": None, "clave_letra": None,
                "valor_clave": None, "indice_clave": None, "numero_letra": None}
        if paso["letra"]:
            numero += 1
            valor = dato["valor"]
            intermedio = a * valor if cifrar else valor - b
            total = intermedio + b if cifrar else inverso * intermedio
            resultado = total % 26
            letra = ALFABETO[resultado]
            calculo = (f"{a} × {valor} = {intermedio}; {intermedio} + {b} = {total}; {total} mod 26 = {resultado}"
                       if cifrar else f"{valor} - {b} = {intermedio}; {inverso} × {intermedio} = {total}; {total} mod 26 = {resultado}")
            paso.update(valor_entrada=valor, valor_salida=resultado, numero_letra=numero,
                        intermedio=intermedio, antes_modulo=total, calculo=calculo,
                        salida=letra if dato["mayuscula"] else letra.lower())
        else:
            paso.update(salida=caracter, calculo="Se conserva sin transformar.")
        pasos.append(paso)
        salida.append(paso["salida"])
    return {"tipo": "transformacion", "algoritmo": "afin", "modo": modo,
            "mensaje": mensaje, "clave": f"a={a}, b={b}", "clave_efectiva": efectiva,
            "clave_original": clave, "inverso": inverso, "euclides": euclides,
            "formula": "C = (a × P + b) mod 26" if cifrar else "P = a⁻¹ × (C - b) mod 26",
            "alfabeto": ALFABETO, "pasos": pasos, "resultado": "".join(salida), "total_letras": numero}


def cifrar_afin(mensaje, clave):
    """Cifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar_afin(mensaje, "cifrar", clave)


def descifrar_afin(mensaje, clave):
    """Descifrar el mensaje y devuelve el procedimiento completo."""
    return _transformar_afin(mensaje, "descifrar", clave)

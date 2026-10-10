"""Fuente única del alfabeto y de los caracteres admitidos."""

ALFABETO_INGLES = {
    "A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5,
    "G": 6, "H": 7, "I": 8, "J": 9, "K": 10, "L": 11,
    "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17,
    "S": 18, "T": 19, "U": 20, "V": 21, "W": 22, "X": 23,
    "Y": 24, "Z": 25,
}
ALFABETO = "".join(ALFABETO_INGLES)
TAMANO_ALFABETO = len(ALFABETO_INGLES)
GRUPOS_CONSERVADOS = {
    "separador": " \t\r\n",
    "digito": "0123456789",
    "signo": "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~¡¿",
}
CARACTERES_PERMITIDOS = {
    caracter: {"tipo": "letra", "valor": valor, "mayuscula": caracter == letra}
    for letra, valor in ALFABETO_INGLES.items()
    for caracter in (letra, letra.lower())
}
CARACTERES_PERMITIDOS.update({
    caracter: {"tipo": "conservado", "categoria": categoria}
    for categoria, caracteres in GRUPOS_CONSERVADOS.items()
    for caracter in caracteres
})

MAXIMO_MENSAJE = 5000
MAXIMO_ANALISIS = 2000
MAXIMO_CLAVE = 100
ALGORITMOS = {"cesar": "César", "sustitucion": "Sustitución Simple", "vigenere": "Vigenère", "afin": "Afín"}
MODOS_POR_ALGORITMO = {nombre: {"cifrar", "descifrar", "analizar"} if nombre in {"cesar", "afin"} else {"cifrar", "descifrar"} for nombre in ALGORITMOS}
MODOS = {"cifrar", "descifrar", "analizar"}
ADVERTENCIA = (
    "Uso estrictamente educativo. Los cifrados clásicos no deben emplearse "
    "para proteger contraseñas, datos personales, información institucional ni comunicaciones sensibles."
)

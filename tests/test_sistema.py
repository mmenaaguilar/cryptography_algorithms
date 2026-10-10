"""Pruebas de la práctica, contratos matemáticos y entradas adversas."""
import io
from contextlib import redirect_stdout
from unittest.mock import patch
import pytest
from app import crear_app
from consola import main
from criptografia.motor import ejecutar
from criptografia.config import ALFABETO, CARACTERES_PERMITIDOS
from criptografia.validaciones import ErrorValidacion, validar_mensaje

CLAVES = {"cesar": "3", "sustitucion": "QWERTYUIOPASDFGHJKLZXCVBNM", "vigenere": "SOL", "afin": {"a": 5, "b": 8}}

def test_cesar_obligatorio():
    cifrado = ejecutar("cesar", "cifrar", "HOLA MUNDO", "3")
    assert cifrado["resultado"] == "KROD PXQGR"
    assert ejecutar("cesar", "descifrar", cifrado["resultado"], "3")["resultado"] == "HOLA MUNDO"

def test_vigenere_obligatorio():
    cifrado = ejecutar("vigenere", "cifrar", "CRIPTOGRAFIA", "SOL")
    assert cifrado["resultado"] == "UFTHHZYFLXWL"
    assert ejecutar("vigenere", "descifrar", cifrado["resultado"], "SOL")["resultado"] == "CRIPTOGRAFIA"

def test_vector_vigenere_conocido():
    assert ejecutar("vigenere", "cifrar", "ATTACKATDAWN", "LEMON")["resultado"] == "LXFOPVEFRNHR"

@pytest.mark.parametrize("algoritmo", CLAVES)
@pytest.mark.parametrize("mensaje", [" Hola, Mundo! 123 ¿Que? ¡Si! ", "A\tZ\r\nb\nc", ALFABETO + ALFABETO.lower(), "... 123 \t\n"])
def test_ida_vuelta_preserva_caracteres(algoritmo, mensaje):
    cifrado = ejecutar(algoritmo, "cifrar", mensaje, CLAVES[algoritmo])
    assert ejecutar(algoritmo, "descifrar", cifrado["resultado"], CLAVES[algoritmo])["resultado"] == mensaje
    assert len(cifrado["pasos"]) == len(mensaje)
    assert "".join(p["salida"] for p in cifrado["pasos"]) == cifrado["resultado"]
    for posicion, caracter in enumerate(mensaje):
        if CARACTERES_PERMITIDOS[caracter]["tipo"] != "letra":
            assert cifrado["resultado"][posicion] == caracter

@pytest.mark.parametrize("caracter", ["ñ", "Ñ", "á", "é", "ü", "🙂", "α", "Ж", "中", "ſ", "ß", "İ", "\u0301", "\x00", "\u00a0", "“"])
@pytest.mark.parametrize("algoritmo", CLAVES)
def test_rechazo_fuera_del_diccionario(algoritmo, caracter):
    with pytest.raises(ErrorValidacion, match="Símbolo no permitido"):
        ejecutar(algoritmo, "cifrar", "ABC" + caracter, CLAVES[algoritmo])

@pytest.mark.parametrize("clave", ["", "S OL", "123", "ñ", "ſ", "A" * 101, None])
def test_clave_vigenere_invalida(clave):
    with pytest.raises(ErrorValidacion):
        ejecutar("vigenere", "cifrar", "HOLA", clave)

@pytest.mark.parametrize("clave", ["A" * 26, ALFABETO[:-1], ALFABETO[:-1] + "ñ", ALFABETO[:-1] + "1", None])
def test_permutacion_invalida(clave):
    with pytest.raises(ErrorValidacion):
        ejecutar("sustitucion", "cifrar", "HOLA", clave)

@pytest.mark.parametrize("clave", ["", "1.5", " 3", "٣", "3e2", True, None, []])
def test_entero_invalido(clave):
    with pytest.raises(ErrorValidacion):
        ejecutar("cesar", "cifrar", "HOLA", clave)

@pytest.mark.parametrize("clave", [-29, -3, 0, 26, 29, 10**50])
def test_modulo_enteros(clave):
    cifrado = ejecutar("cesar", "cifrar", "AZaz", clave)
    esperado = "".join(chr((ord(c.upper()) - 65 + clave) % 26 + (65 if c.isupper() else 97)) for c in "AZaz")
    assert cifrado["resultado"] == esperado
    assert ejecutar("cesar", "descifrar", esperado, clave)["resultado"] == "AZaz"

def test_alineacion_no_consume_simbolos():
    dato = ejecutar("vigenere", "cifrar", "A, 9b\nC!", "BC")
    assert dato["resultado"] == "B, 9d\nD!"
    assert [p["clave_letra"] for p in dato["pasos"] if p["letra"]] == ["B", "C", "B"]

@pytest.mark.parametrize("algoritmo", ["cesar", "vigenere"])
@pytest.mark.parametrize("modo", ["cifrar", "descifrar"])
def test_traza_calculo_y_resultado_coinciden(algoritmo, modo):
    dato = ejecutar(algoritmo, modo, "Az, zA!", CLAVES[algoritmo])
    for paso in dato["pasos"]:
        if paso["letra"]:
            signo = 1 if modo == "cifrar" else -1
            assert paso["antes_modulo"] == paso["valor_entrada"] + signo * paso["valor_clave"]
            assert paso["valor_salida"] == paso["antes_modulo"] % 26
            assert paso["salida"].upper() == ALFABETO[paso["valor_salida"]]

def test_posicion_error_crlf():
    with pytest.raises(ErrorValidacion) as error:
        validar_mensaje("A\r\nBñ")
    assert error.value.detalles == [{"caracter": "ñ", "posicion": 5, "linea": 2, "columna": 2}]

@pytest.mark.parametrize("mensaje", ["", None, [], "A" * 5001])
def test_mensaje_invalido(mensaje):
    with pytest.raises(ErrorValidacion):
        ejecutar("cesar", "cifrar", mensaje, "3")

def test_limite_sin_recorte():
    assert len(ejecutar("cesar", "cifrar", "A" * 5000, "3")["resultado"]) == 5000
    with pytest.raises(ErrorValidacion):
        ejecutar("cesar", "analizar", "A" * 2001)

def test_fuerza_bruta_25():
    dato = ejecutar("cesar", "analizar", "KROD PXQGR")
    assert len(dato["candidatos"]) == 25
    assert dato["candidatos"][2]["resultado"] == "HOLA MUNDO"
    assert {int(c["clave"]) for c in dato["candidatos"]} == set(range(1, 26))

@pytest.mark.parametrize("algoritmo", ["sustitucion", "vigenere"])
def test_analisis_retirado(algoritmo):
    with pytest.raises(ErrorValidacion):
        ejecutar(algoritmo, "analizar", "ABC")

@pytest.mark.parametrize("algoritmo", ["cesar", "afin"])
def test_fuerza_bruta_sin_letras(algoritmo):
    dato = ejecutar(algoritmo, "analizar", "123 !")
    assert dato["total_letras"] == 0
    assert all(c["resultado"] == "123 !" for c in dato["candidatos"])

def test_menu_invalido_regresa():
    salida = io.StringIO()
    with patch("builtins.input", side_effect=["99", "0"]), redirect_stdout(salida):
        main()
    texto = salida.getvalue()
    assert "Opción no válida" in texto
    assert texto.count("Seleccione") == 0  # input simulado no imprime su prompt.
    assert texto.count("SISTEMA DE ENCRIPTACIÓN CLÁSICA") == 2
    assert "Sesión finalizada" in texto

def test_consola_operacion_y_pasos():
    salida = io.StringIO()
    with patch("builtins.input", side_effect=["1", "HOLA MUNDO", "3", "0"]), redirect_stdout(salida):
        main(True)
    assert "Resultado: KROD PXQGR" in salida.getvalue()
    assert "(7 + 3) mod 26 = 10" in salida.getvalue()

@pytest.fixture
def cliente():
    aplicacion = crear_app()
    aplicacion.config["TESTING"] = True
    return aplicacion.test_client()

def test_web_configuracion(cliente):
    assert cliente.get("/").status_code == 200
    dato = cliente.get("/api/config").json
    assert dato["alfabeto"] == ALFABETO
    assert set(dato["permitidos"]) == set(CARACTERES_PERMITIDOS)

@pytest.mark.parametrize("algoritmo", CLAVES)
def test_api_mismo_motor(cliente, algoritmo):
    carga = {"algoritmo": algoritmo, "modo": "cifrar", "mensaje": "Hola! 9", "clave": CLAVES[algoritmo]}
    respuesta = cliente.post("/api/operar", json=carga)
    assert respuesta.status_code == 200
    assert respuesta.json == ejecutar(**carga)

@pytest.mark.parametrize("carga", [None, [], {}, {"algoritmo": [], "modo": "cifrar"}, {"algoritmo": "cesar", "modo": {}, "mensaje": "A"}, {"algoritmo": "cesar", "modo": "cifrar", "mensaje": "Añ", "clave": 3}])
def test_api_error_sin_resultado_parcial(cliente, carga):
    respuesta = cliente.post("/api/operar", json=carga)
    assert respuesta.status_code == 400
    assert "error" in respuesta.json and "resultado" not in respuesta.json

def test_api_no_interpreta_html(cliente):
    respuesta = cliente.post("/api/operar", json={"algoritmo": "cesar", "modo": "cifrar", "mensaje": "<script>alert(1)</script>", "clave": 0})
    assert respuesta.json["resultado"] == "<script>alert(1)</script>"
    assert "script-src 'self'" in respuesta.headers["Content-Security-Policy"]

def test_api_tamano_solicitud(cliente):
    assert cliente.post("/api/operar", data="A" * 128001, content_type="application/json").status_code == 413


def test_afin_vector_independiente():
    assert ejecutar("afin", "cifrar", "HOLA MUNDO", {"a": 5, "b": 8})["resultado"] == "RALI QEVXA"
    assert ejecutar("afin", "descifrar", "RALI QEVXA", {"a": 5, "b": 8})["resultado"] == "HOLA MUNDO"

@pytest.mark.parametrize("a", [1,3,5,7,9,11,15,17,19,21,23,25])
@pytest.mark.parametrize("b", range(26))
def test_afin_312_claves_y_traza(a,b):
    mensaje = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz, 123!\n"
    r = ejecutar("afin", "cifrar", mensaje, {"a":a,"b":b})
    esperado = "".join(chr((a*(ord(c.upper())-65)+b)%26+(65 if c.isupper() else 97)) if c.isascii() and c.isalpha() else c for c in mensaje)
    assert r["resultado"] == esperado
    d = ejecutar("afin", "descifrar", esperado, {"a":a,"b":b})
    assert d["resultado"] == mensaje
    assert (a*d["inverso"])%26 == 1
    for paso in d["pasos"]:
        if paso["letra"]:
            assert paso["antes_modulo"] == d["inverso"]*(paso["valor_entrada"]-b)
            assert paso["valor_salida"] == paso["antes_modulo"]%26

@pytest.mark.parametrize("a", [0,2,4,6,8,10,12,13,14,16,18,20,22,24,26])
def test_afin_rechaza_no_invertibles(a):
    with pytest.raises(ErrorValidacion, match="coprimo"):
        ejecutar("afin", "cifrar", "A", {"a":a,"b":8})

@pytest.mark.parametrize("clave", [{"a":True,"b":8}, {"a":"5.0","b":8}, {"a":5,"b":None}, {}, None])
def test_afin_clave_malformada(clave):
    with pytest.raises(ErrorValidacion):
        ejecutar("afin", "cifrar", "A", clave)

def test_afin_fuerza_bruta_completa():
    r=ejecutar("afin", "analizar", "RALI QEVXA")
    assert len(r["candidatos"]) == 312
    assert len({(c["clave_efectiva"]["a"], c["clave_efectiva"]["b"]) for c in r["candidatos"]}) == 312
    assert next(c for c in r["candidatos"] if c["clave_efectiva"] == {"a":5,"b":8})["resultado"] == "HOLA MUNDO"
    assert sum(c["identidad"] for c in r["candidatos"]) == 1

def test_api_afin_y_rechazo_modo(cliente):
    r=cliente.post("/api/operar",json={"algoritmo":"afin","modo":"cifrar","mensaje":"HOLA MUNDO","clave":{"a":5,"b":8}})
    assert r.status_code == 200 and r.json["resultado"] == "RALI QEVXA"
    for algoritmo in ("sustitucion", "vigenere"):
        assert cliente.post("/api/operar",json={"algoritmo":algoritmo,"modo":"analizar","mensaje":"A"}).status_code == 400

def test_consola_afin_y_fuerza_bruta():
    salida=io.StringIO()
    with patch("builtins.input",side_effect=["8","HOLA MUNDO","5","8","11","RALI QEVXA","0"]), redirect_stdout(salida):
        main()
    assert "Resultado: RALI QEVXA" in salida.getvalue()
    assert "Clave a=5, b=8: HOLA MUNDO" in salida.getvalue()

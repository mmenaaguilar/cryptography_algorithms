"""Servidor local Flask. No persiste mensajes ni claves."""

import argparse
from flask import Flask, jsonify, render_template, request
from criptografia.config import (ALFABETO, ALGORITMOS, ADVERTENCIA, CARACTERES_PERMITIDOS,
                                 MAXIMO_MENSAJE, MAXIMO_ANALISIS, MAXIMO_CLAVE)
from criptografia.motor import ejecutar
from criptografia.validaciones import ErrorValidacion


def crear_app():
    aplicacion = Flask(__name__)
    aplicacion.config.update(MAX_CONTENT_LENGTH=128_000, JSON_SORT_KEYS=False)
    aplicacion.json.ensure_ascii = False

    @aplicacion.get("/")
    def inicio():
        return render_template("index.html", advertencia=ADVERTENCIA)

    @aplicacion.get("/api/config")
    def configuracion():
        return jsonify(alfabeto=ALFABETO, algoritmos=ALGORITMOS,
                       permitidos="".join(CARACTERES_PERMITIDOS),
                       maximo_mensaje=MAXIMO_MENSAJE, maximo_analisis=MAXIMO_ANALISIS,
                       maximo_clave=MAXIMO_CLAVE)

    @aplicacion.post("/api/operar")
    def operar():
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict):
            return jsonify(error="Envía un objeto JSON con los datos de la operación.", campo="mensaje", detalles=[]), 400
        try:
            resultado = ejecutar(datos.get("algoritmo"), datos.get("modo"), datos.get("mensaje"), datos.get("clave"))
        except ErrorValidacion as error:
            return jsonify(error=str(error), campo=error.campo, detalles=error.detalles), 400
        return jsonify(resultado)

    @aplicacion.errorhandler(413)
    def entrada_grande(_error):
        return jsonify(error="La solicitud excede el tamaño permitido.", campo="mensaje", detalles=[]), 413

    @aplicacion.after_request
    def cabeceras(respuesta):
        respuesta.headers["Cache-Control"] = "no-store"
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        respuesta.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        return respuesta

    return aplicacion


app = crear_app()

if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description="Laboratorio local de criptografía clásica")
    argumentos.add_argument("--port", type=int, default=5000)
    opciones = argumentos.parse_args()
    app.run(host="127.0.0.1", port=opciones.port, debug=False, use_reloader=False)

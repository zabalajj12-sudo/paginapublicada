"""
Rutas principales de la app (requieren sesión iniciada).
Esta capa NO sabe cómo se calcula un destino ni cómo se guarda el
historial: eso se lo delega a los modelos `destino` y `registro`.
"""

from flask import Blueprint, render_template, request, session, jsonify, current_app

from models.destino import calcular_destino
from models.registro import guardar_registro, leer_historial_usuario
from models.chatbot import responder_pregunta
from utils.decoradores import login_requerido, api_login_requerido

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_requerido
def index():
    respuesta = current_app.make_response(
        render_template("index.html", usuario=session["usuario"])
    )
    # Evita que el navegador guarde esta página en caché: si no, al hacer
    # "atrás" después de cerrar sesión se puede ver una versión desactualizada.
    respuesta.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    respuesta.headers["Pragma"] = "no-cache"
    return respuesta


@main_bp.route("/api/recomendar", methods=["POST"])
@api_login_requerido
def recomendar():
    data = request.get_json(force=True)
    nombre = (data.get("nombre") or "").strip()
    gustos = data.get("gustos") or []
    entorno = data.get("entorno") or "indiferente"

    if not nombre or not gustos:
        return jsonify({"error": "Faltan datos"}), 400

    destino = calcular_destino(gustos, entorno)
    guardar_registro(session["usuario"], nombre, gustos, entorno, destino)

    return jsonify(destino)


@main_bp.route("/api/historial")
@api_login_requerido
def historial():
    return jsonify(leer_historial_usuario(session["usuario"]))


@main_bp.route("/api/chat", methods=["POST"])
@api_login_requerido
def chat():
    data = request.get_json(force=True)
    pregunta = (data.get("pregunta") or "").strip()
    destino = data.get("destino") or {}

    if not pregunta:
        return jsonify({"error": "Escribe una pregunta"}), 400
    if not destino.get("nombre"):
        return jsonify({"error": "Primero busca un destino"}), 400

    respuesta = responder_pregunta(pregunta, destino)
    return jsonify({"respuesta": respuesta})

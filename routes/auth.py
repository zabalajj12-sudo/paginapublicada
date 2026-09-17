"""
Rutas de autenticación (registro, login, logout, y login con Google).
Esta capa NO sabe cómo se guardan los usuarios ni cómo se hashean las
contraseñas: eso se lo delega por completo al modelo `models.usuario`.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import config
from models.usuario import crear_usuario, verificar_credenciales, crear_o_obtener_usuario_google

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        if not usuario or not password:
            error = "Completa todos los campos."
        elif not crear_usuario(usuario, password):
            error = "Ese usuario ya existe."
        else:
            session["usuario"] = usuario
            return redirect(url_for("main.index"))

    return render_template("registro.html", error=error, google_client_id=config.GOOGLE_CLIENT_ID)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        if verificar_credenciales(usuario, password):
            session["usuario"] = usuario
            return redirect(url_for("main.index"))
        error = "Usuario o contraseña incorrectos."

    return render_template("login.html", error=error, google_client_id=config.GOOGLE_CLIENT_ID)


@auth_bp.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("auth.login"))


@auth_bp.route("/auth/google", methods=["POST"])
def auth_google():
    """
    Recibe el token que genera el botón de Google (Google Identity Services),
    verifica con los servidores de Google que sea legítimo, y crea la sesión.
    """
    data = request.get_json(force=True)
    token = data.get("credential")

    if not token:
        return jsonify({"error": "Falta el token de Google"}), 400

    if config.GOOGLE_CLIENT_ID.startswith("PEGA-AQUI"):
        return jsonify({"error": "El servidor no tiene configurado el Client ID de Google (revisa config.py)"}), 500

    try:
        info = id_token.verify_oauth2_token(
            token, google_requests.Request(), config.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        # Imprime la razón EXACTA en la consola donde corre 'python app.py'
        # (no se la mostramos al usuario final por seguridad, pero a ti sí
        # te sirve para saber qué está mal configurado).
        print(f"[Google Sign-In] Token rechazado: {e}")
        return jsonify({"error": "Token de Google inválido"}), 401

    correo = info.get("email")
    if not correo:
        return jsonify({"error": "Google no devolvió un correo válido"}), 401

    session["usuario"] = crear_o_obtener_usuario_google(correo)
    return jsonify({"ok": True})

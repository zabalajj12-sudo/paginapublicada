"""
Modelo de Usuario.
Se encarga únicamente de leer/escribir las cuentas registradas (usuarios.json)
y de verificar contraseñas. Ninguna otra parte del proyecto debe tocar
ese archivo directamente: siempre pasa por aquí.

Cada usuario se guarda como:
    "correo_o_usuario": {"password_hash": "...", "origen": "local" | "google"}

Las cuentas creadas con Google no tienen password_hash (nadie escribe esa
contraseña a mano), por eso siempre se debe verificar el "origen" antes de
pedir contraseña.
"""

import json
import os

from werkzeug.security import generate_password_hash, check_password_hash

from config import USERS_FILE


def cargar_usuarios():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)


def existe_usuario(usuario):
    return usuario in cargar_usuarios()


def crear_usuario(usuario, password):
    """Crea una cuenta local nueva con la contraseña encriptada. Devuelve False si ya existía."""
    usuarios = cargar_usuarios()
    if usuario in usuarios:
        return False
    usuarios[usuario] = {"password_hash": generate_password_hash(password), "origen": "local"}
    guardar_usuarios(usuarios)
    return True


def verificar_credenciales(usuario, password):
    """Devuelve True si el usuario existe, es una cuenta local, y la contraseña coincide."""
    usuarios = cargar_usuarios()
    cuenta = usuarios.get(usuario)
    if not cuenta or cuenta.get("origen") != "local":
        return False
    return check_password_hash(cuenta["password_hash"], password)


def crear_o_obtener_usuario_google(correo):
    """
    Da de alta automáticamente una cuenta ligada a un correo de Google la
    primera vez que alguien inicia sesión con ese botón (no requiere
    contraseña: la verificación de identidad ya la hizo Google).
    """
    usuarios = cargar_usuarios()
    if correo not in usuarios:
        usuarios[correo] = {"password_hash": None, "origen": "google"}
        guardar_usuarios(usuarios)
    return correo

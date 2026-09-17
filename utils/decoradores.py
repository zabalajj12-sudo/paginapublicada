"""
Decoradores de autenticación.
Se usan encima de las rutas para exigir que haya sesión iniciada.
"""

from functools import wraps
from flask import session, redirect, url_for, jsonify


def login_requerido(vista):
    """Para páginas normales: si no hay sesión, redirige a /login."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("auth.login"))
        return vista(*args, **kwargs)
    return envoltura


def api_login_requerido(vista):
    """Para rutas /api/*: si no hay sesión, responde JSON 401 en vez de
    redirigir (una redirección rompe el fetch() del frontend, porque el
    navegador la sigue automáticamente y recibe HTML en vez de JSON)."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            return jsonify({"error": "Sesión no iniciada"}), 401
        return vista(*args, **kwargs)
    return envoltura

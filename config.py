"""
Configuración central del proyecto.
Aquí viven las rutas de archivos y ajustes generales, para no tenerlos
repartidos ni repetidos por todo el código.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_FILE = os.path.join(DATA_DIR, "usuarios.json")
DB_FILE = os.path.join(DATA_DIR, "viajeros.db")

# Cambia esta clave por una propia y secreta antes de entregar/publicar el proyecto
SECRET_KEY = "cambia-esta-clave-por-una-super-secreta-12345"

# Client ID de Google para el botón "Iniciar sesión con Google".
# Se obtiene gratis en https://console.cloud.google.com/apis/credentials
# Se puede pegar directo aquí, o (mejor, para no subirlo a GitHub) definirlo
# como variable de entorno GOOGLE_CLIENT_ID antes de correr la app.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "42453258264-ujj65gr25fnrps5b9cvsrf7htno0of86.apps.googleusercontent.com")

os.makedirs(DATA_DIR, exist_ok=True)

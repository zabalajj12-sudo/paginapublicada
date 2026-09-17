"""
Wanderlust - Recomendador de viajes
------------------------------------
Punto de entrada de la aplicación. Este archivo NO contiene lógica de
negocio: solo crea la app de Flask y conecta las capas (arquitectura
en carpetas):

    config.py       -> configuración y rutas de archivos
    models/         -> datos y reglas de negocio (usuarios, destinos, historial)
    routes/         -> controladores / endpoints (Blueprints)
    utils/          -> utilidades compartidas (decoradores de sesión)
    templates/      -> vistas HTML

Cómo correrlo:
    1) pip install -r requirements.txt
    2) python app.py
    3) Abrir http://127.0.0.1:5000
"""

from flask import Flask

import config
from models.registro import inicializar_bd
from routes.auth import auth_bp
from routes.main import main_bp


def crear_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app


app = crear_app()

if __name__ == "__main__":
    inicializar_bd()
    app.run(debug=True)

"""
Modelo de Registro (historial de búsquedas).
Toda la lectura/escritura en la base de datos SQLite vive aquí.
Ninguna ruta debe hablar con sqlite3 directamente: siempre pasa por este módulo.
"""

import sqlite3
from datetime import datetime

from config import DB_FILE


def obtener_conexion():
    conexion = sqlite3.connect(DB_FILE)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_bd():
    """Crea el archivo de base de datos y la tabla si no existen."""
    conexion = obtener_conexion()
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            usuario TEXT NOT NULL,
            nombre_viajero TEXT NOT NULL,
            intereses TEXT NOT NULL,
            entorno TEXT NOT NULL,
            destino TEXT NOT NULL,
            pais TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()


def guardar_registro(usuario, nombre, gustos, entorno, destino):
    """Inserta una fila nueva cada vez que se genera una recomendación."""
    inicializar_bd()
    conexion = obtener_conexion()
    conexion.execute(
        """INSERT INTO registros (fecha, usuario, nombre_viajero, intereses, entorno, destino, pais)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            usuario,
            nombre,
            ", ".join(gustos),
            entorno,
            destino["nombre"],
            destino["pais"],
        ),
    )
    conexion.commit()
    conexion.close()


def leer_historial_usuario(usuario, limite=50):
    inicializar_bd()
    conexion = obtener_conexion()
    filas = conexion.execute(
        """SELECT fecha, nombre_viajero, intereses, entorno, destino, pais
           FROM registros WHERE usuario = ?
           ORDER BY id DESC LIMIT ?""",
        (usuario, limite),
    ).fetchall()
    conexion.close()
    return [
        {
            "fecha": f["fecha"],
            "nombre": f["nombre_viajero"],
            "gustos": f["intereses"],
            "entorno": f["entorno"],
            "destino": f["destino"],
            "pais": f["pais"],
        }
        for f in filas
    ]

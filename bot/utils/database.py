"""Utilidades de SQLite compartidas entre el bot y la API del dashboard.

El bot y la API del dashboard (que corre en un hilo aparte, dentro del mismo
proceso) abren conexiones a los mismos archivos ``db/*.db``. En modo
``journal_mode=DELETE`` una lectura larga de la API puede bloquear las
escrituras del bot y provocar errores ``database is locked``.

Activamos WAL (lectores y escritores concurrentes) y un ``busy_timeout``
razonable al arrancar. WAL es una propiedad persistente del archivo, así que
las conexiones que se abran después lo heredan automáticamente.
"""

from __future__ import annotations

import os
import sqlite3


def enable_wal(directory: str = "db") -> None:
    """Activa WAL y ``busy_timeout`` en todas las bases de datos del directorio."""
    try:
        names = [name for name in os.listdir(directory) if name.endswith(".db")]
    except OSError:
        return

    for name in names:
        path = os.path.join(directory, name)
        try:
            connection = sqlite3.connect(path, timeout=5)
            try:
                connection.execute("PRAGMA busy_timeout=5000")
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute("PRAGMA synchronous=NORMAL")
            finally:
                connection.close()
        except sqlite3.Error as error:
            # Una base bloqueada o de solo lectura no debe impedir el arranque.
            print(f"[db] No se pudo activar WAL en {path}: {error}")

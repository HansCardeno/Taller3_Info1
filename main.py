import os
import shutil
import random
import csv
import json
import re
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

REGISTROS_BIOMEDICOS = []

def registrar_log(accion):
    try:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("log.txt", "a", encoding="utf-8") as archivo_log:
            archivo_log.write(f"[{fecha_hora}] {accion}\n")
    except Exception as error:
        print(f"Error al escribir en log.txt: {error}")

def preparar_carpetas():
    try:
        rutas = [Path("data/txt"), Path("data/csv"), Path("data/json")]
        for ruta in rutas:
            os.makedirs(ruta, exist_ok=True)
        registrar_log("Estructura de carpetas (/data/txt, /data/csv, /data/json) verificada/creada.")
    except Exception as error:
        print(f"Error al crear directorios: {error}")
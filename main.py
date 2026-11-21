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

def validar_patron_registro(registro):
    patron_id = r"^ID-\d{3}$"
    patron_fr = r"^\d{1,3} Años$"
    patron_fc = r"^\d{3}ppm$"
    patron_spo2 = r"^\d{2,3}%$"

    id_valido = re.match(patron_id, registro["id"])
    fr_valido = re.match(patron_fr, registro["fr"])
    fc_valido = re.match(patron_fc, registro["fc"])
    spo2_valido = re.match(patron_spo2, registro["spo2"])

    if id_valido and fr_valido and fc_valido and spo2_valido:
        return True
    return False

def ordenar_por_fc(lista_datos):
    n = len(lista_datos)
    for i in range(n):
        for j in range(0, n - i - 1):
            fc_actual = int(lista_datos[j]["fc"].replace("ppm", ""))
            fc_siguiente = int(lista_datos[j + 1]["fc"].replace("ppm", ""))
            if fc_actual > fc_siguiente:
                temp = lista_datos[j]
                lista_datos[j] = lista_datos[j + 1]
                lista_datos[j + 1] = temp
    return lista_datos

def generar_registros_aleatorios():
    global REGISTROS_BIOMEDICOS
    REGISTROS_BIOMEDICOS = []

    for i in range(1, 51):
        id_pac = f"ID-{i:03d}"
        edad = f"{random.randint(18, 90)} Años"
        frec_card = f"{random.randint(60, 150):03d}ppm"
        oxigeno = f"{random.randint(85, 100)}%"

        registro = {
            "id": id_pac,
            "fr": edad,
            "fc": frec_card,
            "spo2": oxigeno
        }
        REGISTROS_BIOMEDICOS.append(registro)

    REGISTROS_BIOMEDICOS = ordenar_por_fc(REGISTROS_BIOMEDICOS)
    registrar_log("50 registros biomedicos aleatorios generados y ordenados por fc.")
    print("\nse generaron y ordenaron 50 registros biomedicos exitosamente.")

def ingresar_registro_manual():
    global REGISTROS_BIOMEDICOS
    print("INGRESO MANUAL DE REGISTRO BIOMEDICO".center(45))

    while True:
        num_id = input("Ingrese los 3 digitos del ID (ej. 051): ").strip()
        if re.match(r"^\d{3}$", num_id):
            id_pac = f"ID-{num_id}"
            break
        print("formato invalido. Debe ingresar exactamente 3 digitos (ej. 051)")

    while True:
        num_edad = input("Ingrese la edad en numeros (ej. 18): ").strip()
        if re.match(r"^\d{1,3}$", num_edad):
            edad = f"{num_edad} Años"
            break
        print("formato invalido. Ingrese solo el numero de años (ej. 18)")

    while True:
        num_fc = input("Ingrese la frecuencia cardiaca en 3 digitos (ej. 090): ").strip()
        if re.match(r"^\d{3}$", num_fc):
            frec_card = f"{num_fc}ppm"
            break
        print("formato invalido. Debe ingresar 3 digitos (ej. 090) ")

    while True:
        num_spo2 = input("Ingrese el porcentaje de SpO2 sin simbolo (ej. 95): ").strip()
        if re.match(r"^\d{2,3}$", num_spo2):
            oxigeno = f"{num_spo2}%"
            break
        print("formato invalido. Ingrese solo el numero (ej. 95) ")

    nuevo_registro = {
        "id": id_pac,
        "fr": edad,
        "fc": frec_card,
        "spo2": oxigeno
    }

    REGISTROS_BIOMEDICOS.append(nuevo_registro)
    REGISTROS_BIOMEDICOS = ordenar_por_fc(REGISTROS_BIOMEDICOS)
    registrar_log(f"Registro manual ingresado y validado: {id_pac}")
    print(f"-> Registro {id_pac} guardado y ordenado correctamente.")

def validar_todos_los_registros():
    if not REGISTROS_BIOMEDICOS:
        print("\nno hay registros guardados para validar")
        return

    validos = 0
    invalidos = 0
    for reg in REGISTROS_BIOMEDICOS:
        if validar_patron_registro(reg):
            validos += 1
        else:
            invalidos += 1
            print(f"registro con formato incorrecto: {reg}")

    registrar_log(f"validacion ejecutada: {validos} validos, {invalidos} invalidos")
    print(f"\nresultado de validacion: {validos} registros validos | {invalidos} registros invalidos")
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

def exportar_archivos():
    if not REGISTROS_BIOMEDICOS:
        print("\nno hay registros guardados para exportar, genere o ingrese datos primero")
        return
    preparar_carpetas()

    try:
        ruta_txt = Path("data/txt/registros_biomedicos.txt")
        with open(ruta_txt, "w", encoding="utf-8") as f_txt:
            for reg in REGISTROS_BIOMEDICOS:
                linea = f"{reg['id']} | {reg['fr']} | {reg['fc']} | {reg['spo2']}\n"
                f_txt.write(linea)

        ruta_csv = Path("data/csv/registros_biomedicos.csv")
        with open(ruta_csv, "w", newline="", encoding="utf-8") as f_csv:
            campos = ["id", "fr", "fc", "spo2"]
            escritor = csv.DictWriter(f_csv, fieldnames=campos)
            escritor.writeheader()
            for reg in REGISTROS_BIOMEDICOS:
                escritor.writerow(reg)

        ruta_json = Path("data/json/registros_biomedicos.json")
        with open(ruta_json, "w", encoding="utf-8") as f_json:
            json.dump(REGISTROS_BIOMEDICOS, f_json, indent=4, ensure_ascii=False)

        registrar_log("Archivos .txt, .csv y .json exportados correctamente en /data.")
        print("\narchivos exportados correctamente en:")
        print(f" - {ruta_txt}")
        print(f" - {ruta_csv}")
        print(f" - {ruta_json}")

    except Exception as error:
        registrar_log(f"error al exportar archivos: {error}")
        print(f"\nerror al exportar los archivos: {error}")

def importar_archivos():
    global REGISTROS_BIOMEDICOS

    print("\nseleccione el formato del archivo a importar:")
    print("1- TXT  (data/txt/registros_biomedicos.txt)")
    print("2- CSV  (data/csv/registros_biomedicos.csv)")
    print("3- JSON (data/json/registros_biomedicos.json)")
    opcion_formato = input("Opcion (1-3): ").strip()
    registros_leidos = []

    try:
        if opcion_formato == "1":
            ruta = Path("data/txt/registros_biomedicos.txt")
            with open(ruta, "r", encoding="utf-8") as f_txt:
                for linea in f_txt:
                    linea = linea.strip()
                    if linea:
                        partes = linea.split(" | ")
                        if len(partes) == 4:
                            reg = {
                                "id": partes[0].strip(),
                                "fr": partes[1].strip(),
                                "fc": partes[2].strip(),
                                "spo2": partes[3].strip()
                            }
                            registros_leidos.append(reg)

        elif opcion_formato == "2":
            ruta = Path("data/csv/registros_biomedicos.csv")
            with open(ruta, "r", encoding="utf-8") as f_csv:
                lector = csv.DictReader(f_csv)
                for fila in lector:
                    reg = {
                        "id": fila["id"].strip(),
                        "fr": fila["fr"].strip(),
                        "fc": fila["fc"].strip(),
                        "spo2": fila["spo2"].strip()
                    }
                    registros_leidos.append(reg)

        elif opcion_formato == "3":
            ruta = Path("data/json/registros_biomedicos.json")
            with open(ruta, "r", encoding="utf-8") as f_json:
                datos = json.load(f_json)
                for item in datos:
                    reg = {
                        "id": str(item["id"]).strip(),
                        "fr": str(item["fr"]).strip(),
                        "fc": str(item["fc"]).strip(),
                        "spo2": str(item["spo2"]).strip()
                    }
                    registros_leidos.append(reg)
        else:
            print("opcion no valida")
            return

        validos = []
        descartados = 0
        for reg in registros_leidos:
            if validar_patron_registro(reg):
                validos.append(reg)
            else:
                descartados += 1

        REGISTROS_BIOMEDICOS = ordenar_por_fc(validos)
        registrar_log(f"importacion desde {ruta}: {len(validos)} validos, {descartados} descartados")
        print(f"\nimportacion completada desde {ruta}:")
        print(f"registros validos cargados y ordenados: {len(validos)}")
        print(f"registros descartados por formato invalido: {descartados}")

    except FileNotFoundError:
        print("\nError: el archivo aun no existe. Exporte los datos primero")
    except KeyError as error:
        print(f"\nError: el archivo no tiene la columna o llave esperada ({error})")
    except json.JSONDecodeError:
        print("\nError: el archivo JSON esta mal estructurado y no se puede leer")
    except Exception as error:
        print(f"\nerror al importar: {error}")

MONGO_URI = "mongodb+srv://hanscardeno_db_user:DPeZeWIhWUlEztNb@firstdatabase-inf1-hans.jmn0wo8.mongodb.net/"
NOMBRE_BD = "monitoreo_biomedico"
NOMBRE_COLECCION = "registros_pacientes"

def conectar_mongodb():
    if "<usuario>" in MONGO_URI or "<password>" in MONGO_URI:
        print("\n[Aviso] Debes pegar tu enlace real de MongoDB Atlas en la variable MONGO_URI.")
        return None

    try:
        cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        cliente.admin.command("ping")
        bd = cliente[NOMBRE_BD]
        return bd[NOMBRE_COLECCION]
    except ConnectionFailure as error:
        registrar_log(f"Error de conexion con MongoDB Atlas: {error}")
        print(f"\nError: No se pudo conectar con MongoDB Atlas. Verifique su internet o URI.\nDetalle: {error}")
        return None
    except Exception as error:
        registrar_log(f"Error inesperado al conectar a MongoDB: {error}")
        print(f"\nError inesperado con MongoDB: {error}")
        return None

def guardar_en_mongodb():
    if not REGISTROS_BIOMEDICOS:
        print("\nNo hay registros en memoria para subir. Genere o importe datos primero.")
        return

    coleccion = conectar_mongodb()
    if coleccion is None:
        return

    try:
        documentos_limpios = []
        for reg in REGISTROS_BIOMEDICOS:
            if validar_patron_registro(reg):
                documentos_limpios.append({
                    "id": reg["id"],
                    "fr": reg["fr"],
                    "fc": reg["fc"],
                    "spo2": reg["spo2"]
                })

        if documentos_limpios:
            coleccion.delete_many({})
            resultado = coleccion.insert_many(documentos_limpios)
            cantidad = len(resultado.inserted_ids)
            registrar_log(f"MongoDB (CREATE): {cantidad} registros insertados en la nube.")
            print(f"\n-> Se guardaron {cantidad} registros en MongoDB Atlas exitosamente.")
    except Exception as error:
        registrar_log(f"Error al insertar en MongoDB: {error}")
        print(f"\nError al subir los datos a MongoDB: {error}")

def consultar_por_id_mongodb():
    coleccion = conectar_mongodb()
    if coleccion is None:
        return

    try:
        todos = list(coleccion.find({}, {"_id": 0}))
        
        if not todos:
            print("\nLa coleccion en MongoDB Atlas esta vacia.")
            return

        suma_fc = 0
        bajo_spo2 = []
        
        for doc in todos:
            fc_num = int(doc.get("fc", "0").replace("ppm", ""))
            spo2_num = int(doc.get("spo2", "100").replace("%", ""))
            
            suma_fc += fc_num
            if spo2_num < 94:
                bajo_spo2.append(doc)

        prom_val = suma_fc / len(todos) if todos else 0

        with open('resultados_mongo.json', 'w', encoding="utf-8") as f:
            json.dump({"promedio_fc": prom_val, "spo2_menor_94": bajo_spo2}, f, indent=4)
        
        print(f"\n-> Requisitos de rubrica ejecutados:")
        print(f"   - Promedio FC calculado: {prom_val:.2f}ppm.")
        print(f"   - Hay {len(bajo_spo2)} pacientes con SpO2 menor a 94%.")
        print("   - Resultados exportados a 'resultados_mongo.json'.")
        registrar_log("Consultas analiticas de MongoDB exportadas a JSON.")

        id_buscar = input("\nIngrese el ID del paciente a consultar (ej. ID-001): ").strip()
        paciente = coleccion.find_one({"id": id_buscar}, {"_id": 0})
        
        if paciente:
            print(f"\nPaciente Encontrado en MongoDB: {paciente}")
            registrar_log(f"Consulta en Mongo por ID: {id_buscar}")
        else:
            print(f"\nNo se encontro el paciente con ID {id_buscar} en la base de datos.")

    except Exception as error:
        registrar_log(f"Error al consultar MongoDB: {error}")
        print(f"\nError al consultar datos de MongoDB: {error}")

def menu_principal():
    preparar_carpetas()
    registrar_log("Inicio de sesion en el sistema de monitoreo biomedico.")

    while True:
        print("SISTEMA DE MONITOREO BIOMEDICO - TALLER 3".center(60))
        print("1- Generar 50 registros aleatorios")
        print("2- Ingresar datos (registro manual)")
        print("3- Validar datos")
        print("4- Exportar archivos (.txt, .csv, .json)")
        print("5- Importar archivos (.txt, .csv, .json)")
        print("6- Subir registros a MongoDB Atlas")
        print("7- Consultar en MongoDB (a traves del ID)")
        print("8- Salir del sistema")
        opcion = input("Seleccione una opcion (1-8): ").strip()

        if opcion == "1":
            generar_registros_aleatorios()
        elif opcion == "2":
            ingresar_registro_manual()
        elif opcion == "3":
            validar_todos_los_registros()
        elif opcion == "4":
            exportar_archivos()
        elif opcion == "5":
            importar_archivos()
        elif opcion == "6":
            guardar_en_mongodb()
        elif opcion == "7":
            consultar_por_id_mongodb()
        elif opcion == "8":
            registrar_log("cierre del sistema")
            print("\nsaliendo del sistema. Todos los eventos quedaron registrados en log.txt.")
            break
        else:
            print("\nopcion invalida. Por favor ingrese un numero entre 1 y 8.")

if __name__ == "__main__":
    menu_principal()

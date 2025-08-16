import requests
import schedule
import time
import mysql.connector
from urllib.parse import quote
from datetime import datetime

import json

with open("usuario_quien_ingresa.json", "r") as archivo:
    datos = json.load(archivo)

username_cargado = datos["username"]# Aquí puedes asignarlo dinámicamente según quién inicia sesión
print("Usuario cargado:", username_cargado)




# Datos de autenticación y remitente
username = ""
password = ""
from_number = ""  # Tu número verificado


# Conexión a la base de datos
def obtener_datos_justvoip(usuario):
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='colegio'
        )
        cursor = conexion.cursor()
        query = """
        SELECT usuario_justVoip, contraseña_justVoip, numero_justVoip
        FROM usuarios
        WHERE username = %s
        """
        cursor.execute(query, (usuario,))
        resultado = cursor.fetchone()
        if resultado:
            return {
                "username": resultado[0],
                "password": resultado[1],
                "from_number": resultado[2]
            }
        else:
            print("Usuario no encontrado.")
            return None
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Obtener los datos
datos_voip = obtener_datos_justvoip(username_cargado)

if datos_voip:
    username = datos_voip['username']
    password = datos_voip['password']
    from_number = datos_voip['from_number']

    print("Datos cargados correctamente:")
    print(f"Usuario VoIP: {username}")
    print(f"Número: {from_number}")
else:
    print("No se pudieron obtener los datos VoIP.")


# Conectar a la base de datos
def obtener_telefonos(salon):
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='colegio'
        )
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT telefono_padres
            FROM estudiantes
            WHERE salon = %s
        """, (salon,))
        telefonos = cursor.fetchall()
        conexion.close()
        # Agregar el prefijo +57 a cada número de teléfono
        telefonos_con_prefijo = [f"+57{telefono[0]}" for telefono in telefonos]
        return telefonos_con_prefijo
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return []

# Obtener el último registro de la tabla historial_de_mensajes
def obtener_ultimo_registro():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='colegio'
        )
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT salon, mensaje
            FROM historial_de_mensajes
            ORDER BY id DESC LIMIT 1
        """)
        ultimo_registro = cursor.fetchone()
        conexion.close()
        return ultimo_registro
    except mysql.connector.Error as err:
        print(f"Error al obtener el último registro: {err}")
        return None

# Obtener los números de teléfono de los padres del salón correspondiente
def obtener_recipients():
    ultimo_registro = obtener_ultimo_registro()
    if ultimo_registro:
        salon, mensaje = ultimo_registro
        print(f"Nuevo mensaje en el salón {salon}: {mensaje}")
        recipients = obtener_telefonos(salon)
        if recipients:
            return recipients, mensaje
        else:
            print(f"No se encontraron números de teléfono para el salón {salon}.")
            return [], None
    else:
        print("No se encontraron registros en la tabla historial_de_mensajes.")
        return [], None

# Función para enviar SMS
def send_sms():
    recipients, message = obtener_recipients()
    if recipients and message:
        encoded_message = quote(message)
        for to_number in recipients:

            url = f'https://www.justvoip.com/myaccount/sendsms.php?username={username}&password={password}&from={from_number}&to={to_number}&text={encoded_message}'
            if not username:
                print("Error: El parámetro 'username' está vacío.")
                return

            try:
                response = requests.get(url)
                print(f'URL solicitada: {url}')
                print(f'Código de estado HTTP: {response.status_code}')
                print(f'Contenido de la respuesta: {response.text}')
            except Exception as e:
                print(f'Error al enviar mensaje a {to_number}: {e}')

def obtener_ultimo_mensaje():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='colegio'
        )
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT fecha_envio, mensaje
            FROM historial_de_mensajes
            ORDER BY id DESC
            LIMIT 1
        """)
        ultimo_registro = cursor.fetchone()
        conexion.close()
        if ultimo_registro:
            fecha_envio, mensaje = ultimo_registro
            return fecha_envio, mensaje
        else:
            return None, None
    except mysql.connector.Error as err:
        print(f"Error al obtener el último mensaje: {err}")
        return None, None

# Obtener y mostrar el último mensaje y su fecha de envío
fecha_envio, mensaje = obtener_ultimo_mensaje()
if fecha_envio and mensaje:
    print(f"Último mensaje enviado el {fecha_envio}: {mensaje}")
else:
    print("No se encontraron registros en la tabla historial_de_mensajes.")

# Fecha y hora programada para el envío (formato: 'YYYY-MM-DD HH:MM')
scheduled_time = fecha_envio

# Convertir la fecha y hora programada a un objeto datetime
scheduled_datetime = fecha_envio

# Calcular el tiempo restante hasta el envío
time_until_send = (scheduled_datetime - datetime.now()).total_seconds()

# Programar el envío solo si el tiempo restante es positivo
if time_until_send > 0:
    schedule.every(time_until_send).seconds.do(send_sms)
    print(f'El mensaje se enviará a las {scheduled_time}.')
else:
    print('La hora programada ya ha pasado.')

# Mantener el script en ejecución
while True:
    schedule.run_pending()
    time.sleep(1)

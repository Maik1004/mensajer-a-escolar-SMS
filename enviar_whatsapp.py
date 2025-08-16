
import mysql.connector
import json
import datetime
import time
import pywhatkit

def enviar_sms_por_whatsapp():
    print("📡 Iniciando proceso de envío de WhatsApp...")

    # 1. Cargar el usuario que inició sesión
    try:
        with open("usuario_quien_ingresa.json", "r") as archivo:
            datos_usuario = json.load(archivo)
        username_cargado = datos_usuario["username"]
        print(f"✅ Usuario cargado desde JSON: {username_cargado}")
    except Exception as e:
        print(f"❌ Error al cargar el usuario: {e}")
        return

    # 2. Obtener el último mensaje programado
    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="colegio")
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT salon, mensaje, fecha_envio
            FROM historial_de_mensajes
            ORDER BY id DESC LIMIT 1
        """)
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not resultado:
            print("❌ No se encontró mensaje programado.")
            return

        salon, mensaje, fecha_envio = resultado
        print(f"🕓 Último mensaje programado para el salón '{salon}' a las {fecha_envio}")
        print(f"📨 Contenido del mensaje: {mensaje}")

        # Esperar hasta la hora programada
        ahora = datetime.datetime.now()
        diferencia = (fecha_envio - ahora).total_seconds()
        if diferencia > 0:
            print(f"⏳ Esperando {round(diferencia)} segundos hasta la hora programada...")
            time.sleep(diferencia)
        else:
            print("⚠️ La hora programada ya pasó. Enviando de inmediato...")

    except mysql.connector.Error as err:
        print(f"❌ Error al obtener el último mensaje: {err}")
        return

    # 3. Obtener teléfonos
    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="colegio")
        cursor = conexion.cursor()
        cursor.execute("SELECT telefono_padres FROM estudiantes WHERE salon = %s", (salon,))
        telefonos = [f"+57{t[0]}" for t in cursor.fetchall()]
        cursor.close()
        conexion.close()

        if not telefonos:
            print("⚠️ No se encontraron teléfonos para el salón.")
            return

        print(f"📱 Números a los que se enviará el mensaje por WhatsApp: {telefonos}")
    except mysql.connector.Error as err:
        print(f"❌ Error al obtener teléfonos: {err}")
        return

    # 4. Enviar por WhatsApp usando pywhatkit
    hora = datetime.datetime.now().hour
    minuto = datetime.datetime.now().minute + 1

    for numero in telefonos:
        if minuto >= 60:
            minuto -= 60
            hora += 1
            if hora >= 24:
                hora = 0

        print(f"⏳ Programando envío a {numero} a las {hora}:{minuto:02d}...")
        try:
            pywhatkit.sendwhatmsg(numero, mensaje, hora, minuto, wait_time=10)
        except Exception as e:
            print(f"❌ Error enviando a {numero}: {e}")

        minuto += 1
        time.sleep(3)  # pausa para no saturar

    print("✅ Todos los mensajes fueron programados en WhatsApp.")



if __name__ == "__main__":
    enviar_sms_por_whatsapp()


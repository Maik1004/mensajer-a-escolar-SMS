import hashlib
import json
import os
import subprocess
import time
from datetime import datetime
from threading import Thread
from urllib.parse import quote

import mysql.connector
import requests
from flask import (Flask, flash, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

# Constantes globales
ARCHIVO_CONFIG = "configuracion_mensajes.json"
ARCHIVO_USUARIO = "usuario_quien_ingresa.json"

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'colegio'
}

# Estructura de salones
SALONES_POR_GRADO = {
    str(g): [f"{g}-{i}" for i in range(1, 7)] for g in range(1, 13)
}

# Funciones de utilidad
def crear_conexion():
    """Crea y retorna una conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)

def cargar_configuracion():
    """Carga la configuración desde el archivo JSON"""
    try:
        with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Convertir la fecha a objeto datetime
        fecha = datetime(
            year=config["fecha"]["year"],
            month=config["fecha"]["month"],
            day=config["fecha"]["day"],
            hour=config["fecha"]["hour"],
            minute=config["fecha"]["minute"]
        )

        return {
            "grado": config["grado"],
            "salon": config["salon"],
            "fecha": fecha,
            "fecha_guardado": config["fecha_guardado"],
            "mensaje": config.get("mensaje", ""),
        }

    except FileNotFoundError:
        return None
    except Exception as e:
        print("Error al cargar configuración:", e)
        return None

def guardar_configuracion(grado, salon, fecha_programada, mensaje=""):
    """Guarda la configuración en un archivo JSON"""
    config = {
        "grado": grado,
        "salon": salon,
        "fecha": {
            "year": fecha_programada.year,
            "month": fecha_programada.month,
            "day": fecha_programada.day,
            "hour": fecha_programada.hour,
            "minute": fecha_programada.minute
        },
        "mensaje": mensaje,
        "fecha_guardado": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# Rutas de autenticación
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        contrasena = request.form["contrasena"].strip()

        if not usuario or not contrasena:
            error = "Todos los campos son obligatorios"
        else:
            contrasena_hash = hashlib.sha1(contrasena.encode()).hexdigest()
            try:
                conn = crear_conexion()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM usuarios WHERE username = %s AND password = %s", 
                    (usuario, contrasena_hash)
                )
                resultado = cursor.fetchone()
                cursor.close()
                conn.close()

                if resultado:
                    datos = {"username": resultado["username"]}
                    with open(ARCHIVO_USUARIO, "w") as f:
                        json.dump(datos, f)
                    return redirect(url_for("menu_principal"))
                else:
                    error = "Usuario o contraseña incorrectos"

            except mysql.connector.Error as e:
                error = f"Error de conexión: {str(e)}"

    return render_template("login.html", error=error)

@app.route("/menu")
def menu_principal():
    with open(ARCHIVO_USUARIO) as f:
        datos = json.load(f)
    return render_template("menu.html", usuario=datos.get("username", "Invitado"))

# Rutas de mensajería
@app.route("/historial")
def historial():
    try:
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, grado, salon, mensaje,
                   DATE_FORMAT(fecha_envio, '%Y-%m-%d %H:%i') as fecha,
                   estado
            FROM historial_de_mensajes
            ORDER BY fecha_envio DESC
            LIMIT 200
        """)
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        datos = []
        print("Error al cargar historial:", e)

    return render_template("historial.html", datos=datos)

@app.route("/escribir_mensaje", methods=["GET", "POST"])
def escribir_mensaje():
    config = cargar_configuracion()
    return render_template("escribir_mensaje.html", config=config)

@app.route("/escribir_mensaje_whatsapp", methods=["GET", "POST"])
def escribir_mensaje_whatsapp():
    config = cargar_configuracion()
    return render_template("escribir_mensaje_whatsapp.html", config=config)

@app.route('/mensaje', methods=['GET', 'POST'])
def mensaje():
    if request.method == 'POST':
        mensaje = request.form['mensaje']
        config = cargar_configuracion()
        if config:
            guardar_configuracion(config['grado'], config['salon'], config['fecha'], mensaje)
            return render_template("escribir_mensaje.html", 
                                mensaje_confirmacion="GUARDADO CORRECTAMENTE")
    return render_template("escribir_mensaje.html")

@app.route('/mensaje_whatsapp', methods=['GET', 'POST'])
def mensaje_whatsapp():
    if request.method == 'POST':
        mensaje = request.form['mensaje']
        config = cargar_configuracion()
        if config:
            guardar_configuracion(config['grado'], config['salon'], config['fecha'], mensaje)
            return render_template("escribir_mensaje_whatsapp.html", 
                                mensaje_confirmacion="GUARDADO CORRECTAMENTE")
    return render_template("escribir_mensaje_whatsapp.html")

# Rutas de programación
@app.route("/programacion", methods=["GET", "POST"])
def programacion_mensaje():
    return _procesar_programacion("programacion_del_mensaje.html")

@app.route("/programacion_mensaje_whatsapp", methods=["GET", "POST"])
def programacion_mensaje_whatsapp():
    return _procesar_programacion("programacion_del_mensaje_whatsapp.html")

def _procesar_programacion(template):
    """Función auxiliar para procesar la programación de mensajes"""
    mensaje_alerta = None
    redirigir = False

    if request.method == "POST":
        grado = request.form.get("grado")
        salon = request.form.get("salon")
        dia = request.form.get("dia")
        mes = request.form.get("mes")
        anio = request.form.get("anio")
        hora = request.form.get("hora")
        minuto = request.form.get("minuto")

        try:
            fecha = datetime(
                year=int(anio), month=int(mes), day=int(dia),
                hour=int(hora), minute=int(minuto)
            )
            ahora = datetime.now()
            if fecha > ahora:
                guardar_configuracion(grado, salon, fecha)
                mensaje_alerta = (
                    f"Mensaje programado correctamente.   "
                    f"   .Grado: {grado}  "
                    f"   .Salon: {salon}  "
                    f"   Fecha Programada:{fecha.strftime('%d/%m/%Y %H:%M')}"
                )
                redirigir = True
            else:
                mensaje_alerta = "La fecha y hora seleccionadas ya han pasado."
        except Exception as e:
            mensaje_alerta = f"Error en la fecha: {e}"

    return render_template(
        template,
        salones_por_grado=SALONES_POR_GRADO,
        mensaje_alerta=mensaje_alerta,
        redirigir=redirigir
    )

# Rutas de configuración
@app.route("/ver_configuracion")
def ver_configuracion():
    return _procesar_ver_configuracion(es_whatsapp=False)

@app.route("/ver_configuracion_whatsapp")
def ver_configuracion_whatsapp():
    return _procesar_ver_configuracion(es_whatsapp=True)

def _procesar_ver_configuracion(es_whatsapp):
    """Función auxiliar para procesar la visualización de configuración"""
    try:
        with open(ARCHIVO_CONFIG, "r") as archivo:
            datos = json.load(archivo)

        if not datos:
            flash("No se encontró información en el archivo de configuración.", "warning")
            return redirect(url_for("menu_principal"))

        grado = datos.get("grado", "")
        salon = datos.get("salon", "")
        mensaje = datos.get("mensaje", "")
        fecha_json = datos.get("fecha", {})
        fecha_guardado = datos.get("fecha_guardado", "")
        fecha_registro = datetime.strptime(fecha_guardado, "%d/%m/%Y %H:%M:%S")

        if not fecha_json:
            flash("La fecha de envío no está definida en el archivo.", "warning")
            return redirect(url_for("menu_principal"))

        fecha_envio = datetime(
            int(fecha_json["year"]),
            int(fecha_json["month"]),
            int(fecha_json["day"]),
            int(fecha_json["hour"]),
            int(fecha_json["minute"])
        )

        # Guardar en la base de datos
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO historial_de_mensajes (grado, salon, mensaje, fecha_envio, fecha_registro)
            VALUES (%s, %s, %s, %s, %s)
        """, (grado, salon, mensaje, fecha_envio, fecha_registro))
        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Configuración cargada y guardada en la base de datos.", "success")

        # Lanzar envío en segundo plano
        Thread(target=login_whatsapp if es_whatsapp else enviar_sms_justvoip).start()

        template = "whatsapp_login.html" if es_whatsapp else "ver_configuracion.html"
        return render_template(template, datos=datos)

    except Exception as e:
        flash(f"Error al leer el JSON o guardar en la base de datos: {e}", "danger")
        return redirect(url_for("menu_principal"))

# Rutas de WhatsApp
@app.route('/login_whatsapp')
def login_whatsapp():
    try:
        # Ejecutar el script Python al abrir esta ruta
        subprocess.Popen([
            r"C:\Users\USUARIO\Documents\Proyecto\Proyecto en Desarrollo\.venv\Scripts\python.exe",
            "enviar_whatsapp.py"
        ])
        print("✅ Script 'enviar_whatsapp.py' lanzado correctamente.")
    except Exception as e:
        print(f"❌ Error al lanzar el script: {e}")

    return render_template("whatsapp_login.html")

# Rutas de gestión de contactos
@app.route('/configuracion_salones')
def configuracion_salones():
    return render_template('contactos_padres.html', salones_por_grado=SALONES_POR_GRADO)

@app.route('/')
def index():
    return render_template('index.html', salones_por_grado=SALONES_POR_GRADO)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    numero = request.form['numero']
    grado = request.form['grado']
    salon = request.form['salon']

    if not all([nombre, apellido, numero, grado, salon]):
        flash("Por favor complete todos los campos", "warning")
        return render_template("contactos_padres.html", salones_por_grado=SALONES_POR_GRADO)

    try:
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO estudiantes (nombre, apellido, telefono_padres, grado, salon)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, numero, int(grado), salon))
        conexion.commit()

        # Obtener lista actualizada de contactos
        cursor.execute("""
            SELECT nombre, apellido, telefono_padres, grado, salon
            FROM estudiantes
            WHERE grado = %s AND salon = %s
            ORDER BY apellido, nombre
        """, (grado, salon))
        estudiantes = cursor.fetchall()
        conexion.close()

        flash("Estudiante agregado correctamente", "success")
        return render_template(
            "contactos_padres.html",
            salones_por_grado=SALONES_POR_GRADO,
            estudiantes=estudiantes
        )
    except Exception as e:
        flash(f"No se pudo agregar: {e}", "danger")
        return render_template("contactos_padres.html", salones_por_grado=SALONES_POR_GRADO)

@app.route('/mostrar', methods=['POST'])
def mostrar():
    grado = request.form['grado']
    salon = request.form.get('salon', '').strip()

    conexion = crear_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT nombre, apellido, telefono_padres, grado, salon 
        FROM estudiantes 
        WHERE grado = %s AND salon = %s
        ORDER BY apellido, nombre
    """, (grado, salon))
    estudiantes = cursor.fetchall()
    conexion.close()

    return render_template(
        'contactos_padres.html',
        estudiantes=estudiantes,
        salones_por_grado=SALONES_POR_GRADO
    )

@app.route('/eliminar', methods=['POST'])
def eliminar():
    numero = request.form['numero']

    if not numero:
        flash("Por favor ingrese un número de teléfono", "warning")
        return render_template("contactos_padres.html", salones_por_grado=SALONES_POR_GRADO)

    try:
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM estudiantes WHERE telefono_padres = %s", (numero,))
        resultado = cursor.fetchone()

        if not resultado:
            flash("No se encontró ningún contacto con ese número", "info")
        else:
            cursor.execute("DELETE FROM estudiantes WHERE telefono_padres = %s", (numero,))
            conexion.commit()
            flash("Contacto eliminado correctamente", "success")

        conexion.close()
    except Exception as e:
        flash(f"No se pudo eliminar el contacto: {e}", "danger")

    return render_template("contactos_padres.html", salones_por_grado=SALONES_POR_GRADO)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        email = request.form['email'].strip()
        contrasena = request.form['contrasena'].strip()
        confirmar = request.form['confirmar'].strip()
        user_voip = request.form['usuario_justvoip'].strip()
        pass_voip = request.form['contrasena_justvoip'].strip()
        numero_voip = request.form['numero_justvoip'].strip()

        # Validaciones
        if not all([usuario, email, contrasena, confirmar, user_voip, pass_voip, numero_voip]):
            flash("Todos los campos son obligatorios", "warning")
            return redirect(url_for('registro'))

        if contrasena != confirmar:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for('registro'))

        if len(contrasena) < 6:
            flash("La contraseña debe tener al menos 6 caracteres", "danger")
            return redirect(url_for('registro'))

        if not numero_voip.replace("+57", "").isdigit():
            flash("El número JustVoip debe contener solo dígitos", "danger")
            return redirect(url_for('registro'))

        if not numero_voip.startswith("+57"):
            numero_voip = "+57" + numero_voip.lstrip("0")

        contrasena_hash = hashlib.sha1(contrasena.encode()).hexdigest()

        try:
            conexion = crear_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT username FROM usuarios WHERE username = %s", (usuario,))
            if cursor.fetchone():
                flash("El nombre de usuario ya existe", "danger")
                return redirect(url_for('registro'))

            cursor.execute("""
                INSERT INTO usuarios (
                    username, password, email, fecha_registro,
                    usuario_justVoip, contraseña_justVoip, numero_justVoip
                )
                VALUES (%s, %s, %s, NOW(), %s, %s, %s)
            """, (usuario, contrasena_hash, email, user_voip, pass_voip, numero_voip))

            conexion.commit()
            flash("Usuario registrado exitosamente", "success")
        except mysql.connector.Error as e:
            flash(f"Error al registrar usuario: {e}", "danger")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

        return redirect(url_for('registro'))

    return render_template('registro.html')

# Funciones de envío de mensajes
def enviar_sms_justvoip():
    print("📡 Iniciando proceso de envío de SMS...")

    # 1. Cargar el usuario que inició sesión
    try:
        with open(ARCHIVO_USUARIO, "r") as archivo:
            datos_usuario = json.load(archivo)
        username_cargado = datos_usuario["username"]
        print(f"✅ Usuario cargado desde JSON: {username_cargado}")
    except Exception as e:
        print(f"❌ Error al cargar el usuario: {e}")
        return

    # 2. Obtener datos de JustVoip desde la BD
    try:
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT usuario_justVoip, contraseña_justVoip, numero_justVoip
            FROM usuarios WHERE username = %s
        """, (username_cargado,))
        datos_voip = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not datos_voip:
            print("❌ No se encontraron credenciales VoIP.")
            return

        username, password, from_number = datos_voip
        print(f"✅ Datos VoIP cargados: {username}, {from_number}")
    except mysql.connector.Error as err:
        print(f"❌ Error al obtener datos VoIP: {err}")
        return

    # 3. Obtener el último mensaje programado
    try:
        conexion = crear_conexion()
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
        ahora = datetime.now()
        diferencia = (fecha_envio - ahora).total_seconds()
        if diferencia > 0:
            print(f"⏳ Esperando {round(diferencia)} segundos hasta la hora programada...")
            time.sleep(diferencia)
        else:
            print("⚠️ La hora programada ya pasó. Enviando de inmediato...")

    except mysql.connector.Error as err:
        print(f"❌ Error al obtener el último mensaje: {err}")
        return

    # 4. Obtener teléfonos
    try:
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT telefono_padres FROM estudiantes WHERE salon = %s", (salon,))
        telefonos = [f"+57{t[0]}" for t in cursor.fetchall()]
        cursor.close()
        conexion.close()

        if not telefonos:
            print("⚠️ No se encontraron teléfonos para el salón.")
            return

        print(f"📱 Números a los que se enviará el SMS: {telefonos}")
    except mysql.connector.Error as err:
        print(f"❌ Error al obtener teléfonos: {err}")
        return

    # 5. Enviar mensaje
    mensaje_codificado = quote(mensaje)
    for numero in telefonos:
        url = (
            f"https://www.justvoip.com/myaccount/sendsms.php?"
            f"username={username}&password={password}&from={from_number}&to={numero}&text={mensaje_codificado}"
        )
        print(f"🌐 Enviando SMS a {numero}")
        print(f"🔗 URL: {url}")
        try:
            respuesta = requests.get(url)
            print(f"✅ Código HTTP: {respuesta.status_code}")
            print(f"📬 Respuesta: {respuesta.text}")
        except Exception as e:
            print(f"❌ Error al enviar a {numero}: {e}")

if __name__ == "__main__":
    app.run(debug=True)
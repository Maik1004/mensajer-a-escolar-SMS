
import subprocess

import json
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import mysql.connector
from mysql.connector import Error
from datetime import datetime

def guardar_en_historial_mysql(archivo_json="configuracion_mensajes.json"):
    """
    Guarda los datos del JSON en la base de datos MySQL en XAMPP
    Tabla: historial_de_mensajes (debe tener las columnas: grado, salon, mensaje, fecha_envio, estado, fecha_registro)
    """
    try:
        # Cargar datos del JSON
        with open(archivo_json, 'r') as f:
            config = json.load(f)

        # Conexión a MySQL
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',  # Usuario por defecto en XAMPP
            password='',  # Contraseña por defecto en XAMPP (vacía)
            database='colegio'
        )

        if conexion.is_connected():
            cursor = conexion.cursor()

            # Preparar datos
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            fecha_envio = datetime(
                year=config['fecha']['year'],
                month=config['fecha']['month'],
                day=config['fecha']['day'],
                hour=config['fecha']['hour'],
                minute=config['fecha']['minute']
            ).strftime('%Y-%m-%d %H:%M:%S')

            # Consulta SQL para insertar - CORRECCIÓN: 6 parámetros para 6 valores
            query = """INSERT INTO historial_de_mensajes
                      (grado, salon, mensaje, fecha_envio, estado, fecha_registro)
                      VALUES (%s, %s, %s, %s, %s, %s)"""

            valores = (
                config['grado'],
                config['salon'],
                config.get('mensaje', ''),
                fecha_envio,
                'enviado',  # Estado por defecto
                fecha_actual
            )

            cursor.execute(query, valores)
            conexion.commit()

            return True

    except Error as e:
        print(f"Error de MySQL: {e}")
        return False
    except json.JSONDecodeError:
        print("Error: Archivo JSON corrupto o mal formateado")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()



def cargar_configuracion(archivo_json="configuracion_mensajes.json"):
    """Carga la configuración desde el archivo JSON"""
    try:
        with open(archivo_json, 'r') as f:
            config = json.load(f)
            fecha_data = config['fecha']
            fecha = datetime(
                year=fecha_data['year'],
                month=fecha_data['month'],
                day=fecha_data['day'],
                hour=fecha_data['hour'],
                minute=fecha_data['minute']
            )
            return {
                'grado': config['grado'],
                'salon': config['salon'],
                'fecha': fecha,
                'fecha_guardado': config['fecha_guardado'],
                'mensaje': config.get('mensaje', '')  # Añade esta línea
            }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar la configuración: {e}")
        return None

def mostrar_configuracion(parent_window, archivo_json="configuracion_mensajes.json"):
    """Muestra la configuración guardada en una nueva ventana"""
    config = cargar_configuracion(archivo_json)
    ventana_config = tk.Toplevel(parent_window)
    ventana_config.title("Configuración Guardada")
    ventana_config.geometry("350x300")  # Aumentamos el tamaño para el mensaje
    ventana_config.resizable(False, False)
    ventana_config.configure(bg="#f0f0f0")
    ventana_config.iconbitmap("2.ico")

    if config:
        tk.Label(ventana_config, text="CONFIGURACIÓN GUARDADA",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        frame = tk.Frame(ventana_config, bg="#f0f0f0")
        frame.pack(pady=10, padx=20)

        # Mostrar los datos en un formato organizado
        tk.Label(frame, text="Grado:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text=config['grado'], font=("Arial", 12),
                 bg="#f0f0f0").grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Salón:", font=("Arial",12, "bold"),
                 bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        tk.Label(frame, text=config['salon'], font=("Arial", 12),
                 bg="#f0f0f0").grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Fecha programada:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        tk.Label(frame, text=config['fecha'].strftime('%d/%m/%Y %H:%M'),
                 font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="Guardado el:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0").grid(row=3, column=0, sticky="w")
        tk.Label(frame, text=config['fecha_guardado'], font=("Arial", 12),
                 bg="#f0f0f0").grid(row=3, column=1, sticky="w")


def mostrar_configuracion_enviar(parent_window, archivo_json="configuracion_mensajes.json"):
    """Muestra la configuración guardada en una nueva ventana modal con botón Enviar"""
    config = cargar_configuracion(archivo_json)
    ventana_config = tk.Toplevel(parent_window)
    ventana_config.title("Configuración Guardada")
    ventana_config.geometry("560x550")
    ventana_config.resizable(False, False)
    ventana_config.configure(bg="#f0f0f0")
    ventana_config.iconbitmap("2.ico")

    # Hacer la ventana completamente modal
    ventana_config.grab_set()
    ventana_config.transient(parent_window)
    ventana_config.focus_set()

    def on_close():
        ventana_config.grab_release()
        parent_window.attributes('-disabled', False)
        ventana_config.destroy()
        ventana.destroy()
        subprocess.run(["python", "envio_a_la_web.py"])
        subprocess.run(["python", "menu_principal.py"])

    ventana_config.protocol("WM_DELETE_WINDOW", on_close)
    parent_window.attributes('-disabled', True)

    # Frame principal para organizar contenido
    main_frame = tk.Frame(ventana_config, bg="#f0f0f0")
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    if config:
        tk.Label(main_frame, text="CONFIGURACIÓN GUARDADA",
                 font=("Arial", 15, "bold"), bg="#f0f0f0").pack(pady=10)

        frame = tk.Frame(main_frame, bg="#f0f0f0")
        frame.pack(pady=10, fill="x")

        # Mostrar los datos en un formato organizado
        tk.Label(frame, text="Grado:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text=config['grado'], font=("Arial", 12),
                 bg="#f0f0f0").grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Salón:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        tk.Label(frame, text=config['salon'], font=("Arial", 12),
                 bg="#f0f0f0").grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Fecha programada:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        tk.Label(frame, text=config['fecha'].strftime('%d/%m/%Y %H:%M'),
                 font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="Guardado el:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0").grid(row=3, column=0, sticky="w")
        tk.Label(frame, text=config['fecha_guardado'], font=("Arial", 12),
                 bg="#f0f0f0").grid(row=3, column=1, sticky="w")

        # Añadimos la visualización del mensaje
        tk.Label(frame, text="Último mensaje:", font=("Arial", 12, "bold"),
                 bg="#f0f0f0").grid(row=4, column=0, sticky="nw")

        # Usamos un Text widget para mensajes largos con scrollbar
        frame_mensaje = tk.Frame(frame, bg="#f0f0f0")
        frame_mensaje.grid(row=5, column=0, columnspan=2, sticky="ew")

        scrollbar = tk.Scrollbar(frame_mensaje)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        mensaje_text = tk.Text(frame_mensaje, height=12, width=55, wrap=tk.WORD,
                               yscrollcommand=scrollbar.set, bg="#f0f0f0",
                               font=("Arial", 12))
        mensaje_text.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.config(command=mensaje_text.yview)

        mensaje_text.insert(tk.END, config.get('mensaje', 'Ningún mensaje guardado'))
        mensaje_text.config(state=tk.DISABLED)

        # Frame para el botón Enviar (AHORA DEFINIDO EN EL LUGAR CORRECTO)
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(side="bottom", pady=20)

        # Botón de "Enviar" al final de la ventana
        boton_enviar = tk.Button(button_frame, text="Enviar", font=("Arial", 15, "bold"),
                                 bg="#4CAF50", fg="white", width=15, height=2,
                                 command=lambda: [guardar_en_historial_mysql(), on_close()])
        boton_enviar.pack()

    else:
        tk.Label(main_frame, text="No hay configuración guardada",
                 font=("Arial", 12), bg="#f0f0f0").pack(pady=50)

    ventana_config.bind('<Destroy>', lambda e: parent_window.attributes('-disabled', False))

#funcion para ir atras
def ventana_anterior():
    ventana.destroy()
    subprocess.run(["python", "menu_principal.py"])

# Funciones para manejar el archivo JSON
def guardar_configuracion(grado, salon, fecha, mensaje=""):
    """Guarda la configuración en un archivo JSON incluyendo el mensaje"""
    config = {
        'grado': grado,
        'salon': salon,
        'fecha': {
            'year': fecha.year,
            'month': fecha.month,
            'day': fecha.day,
            'hour': fecha.hour,
            'minute': fecha.minute
        },
        'fecha_guardado': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'mensaje': mensaje  # Añadimos el mensaje al diccionario
    }

    try:

        with open("configuracion_mensajes.json", 'w') as f:
            json.dump(config, f, indent=4)

        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")
        return False


# Función para enviar mensaje
def enviar_mensaje():
    mensaje = cuadro_texto.get("1.0", tk.END).strip()
    if mensaje:
        # Cargamos la configuración existente
        config = cargar_configuracion()

        if config:
            # Guardamos el mensaje junto con la configuración existente
            if guardar_configuracion(
                    grado=config['grado'],
                    salon=config['salon'],
                    fecha=config['fecha'],
                    mensaje=mensaje
            ):
                # Verificación adicional
                try:
                    with open("configuracion_mensajes.json", 'r') as f:
                        contenido = json.load(f)
                        print("Contenido actual del JSON:", contenido)  # Para depuración
                except Exception as e:
                    print("Error leyendo JSON:", e)

                messagebox.showinfo("Mensaje enviado", f"Mensaje guardado y enviado:\n\n{mensaje}")
                mostrar_configuracion_enviar(ventana)
        else:
            messagebox.showwarning("Configuración faltante", "No hay configuración de grado/salón/fecha establecida")

        cuadro_texto.delete("1.0", tk.END)
    else:
        messagebox.showwarning("Mensaje vacío", "Por favor, escribe un mensaje antes de enviar.")

# Función para mostrar información--------------------




#Crear ventana principal----------------------------------------------------------
ventana = tk.Tk()
ventana.iconbitmap("SMS2.ico")
ventana.title("Notificación por SMS escolar")
ventana.geometry("700x400")

ventana.resizable(False, False)  # No permitir redimensionar

# Botón de "Enviar"
boton_atras = tk.Button(text="↩", font=("Arial", 12, "bold"), bg="#da2913", fg="white",
                         width=3, command=lambda :ventana_anterior())
boton_atras.place(relx=0.03,rely=0.03)

# Encabezado
Encabezado = tk.Label(ventana, text="", font=("Arial", 16, "bold"))
Encabezado.pack(pady=4)

# titulo
titulo = tk.Label(ventana, text="Notificación por SMS escolar", font=("Arial", 16, "bold"))
titulo.pack(pady=5)


# Subtítulo
subtitulo = tk.Label(ventana, text="Escribir el mensaje:", font=("Arial", 12))
subtitulo.pack(padx=0,pady=5)



# Frame para organizar el cuadro de texto y botones
frame = tk.Frame(ventana)
frame.pack(pady=10)

# Cuadro de texto (lado izquierdo)
cuadro_texto = tk.Text(frame, width=40, height=13, font=("Arial", 12), wrap="word")
cuadro_texto.grid(row=0, column=0, padx=10, sticky="n")

# Frame para los botones (lado derecho)
frame_botones = tk.Frame(frame)
frame_botones.grid(row=0, column=1, padx=20, sticky="n")

# Botón de "Enviar"
boton_enviar = tk.Button(frame_botones, text="Enviar", font=("Arial", 15, "bold"),
                        bg="#4CAF50", fg="white", width=15, height=2,
                        command=enviar_mensaje)

boton_enviar.pack()

# Frame espaciador - PRIMERA OPCIÓN (recomendada)
# Ajusta el height para cambiar la separación
espaciador = tk.Frame(frame_botones, height=50)  # 20 píxeles de separación
espaciador.pack()
# Botón de "Información" con texto multilínea bien formateado
boton_info = tk.Button(
    frame_botones,
    text="Fecha y hora\nestablecida",  # Usar \n para salto de línea explícito
    font=("Arial", 15, "bold"),
    bg="#2196F3",
    fg="white",
    width=15,
    height=3,
    wraplength=150,  # Define el ancho máximo antes de saltar línea (en píxeles)
    justify="center",  # Centra el texto
    command=lambda: mostrar_configuracion(ventana)
)
boton_info.pack(pady=10)  # Añade espacio vertical alrededor del botón

# Alternativa SEGUNDA OPCIÓN (combinando pady y espaciador)
# boton_enviar.pack(pady=(0, 5))  # 5 píxeles abajo
# espaciador = tk.Frame(frame_botones, height=10)  # 10 píxeles adicionales
# espaciador.pack()
# boton_info.pack(pady=(5, 0))  # 5 píxeles arriba

# Ejecutar ventana
ventana.mainloop()

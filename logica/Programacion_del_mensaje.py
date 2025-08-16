import json
import tkinter as tk
import subprocess
from datetime import datetime
from tkinter import ttk, messagebox

# Archivo de configuración
CONFIG_FILE = "configuracion_mensajes.json"

# Diccionario con los grados y sus respectivos salones
salones_por_grado = {
    "1": ["1-1", "1-2", "1-3", "1-4", "1-5", "1-6"],
    "2": ["2-1", "2-2", "2-3", "2-4", "2-5", "2-6"],
    "3": ["3-1", "3-2", "3-3", "3-4", "3-5", "3-6"],
    "4": ["4-1", "4-2", "4-3", "4-4", "4-5", "4-6"],
    "5": ["5-1", "5-2", "5-3", "5-4", "5-5", "5-6"],
    "6": ["6-1", "6-2", "6-3", "6-4", "6-5", "6-6"],
    "7": ["7-1", "7-2", "7-3", "7-4", "7-5", "7-6"],
    "8": ["8-1", "8-2", "8-3", "8-4", "8-5", "8-6"],
    "9": ["9-1", "9-2", "9-3", "9-4", "9-5", "9-6"],
    "10": ["10-1", "10-2", "10-3", "10-4", "10-5", "10-6"],
    "11": ["11-1", "11-2", "11-3", "11-4", "11-5", "11-6"],
}


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

def cargar_configuracion():
    """Carga la configuración desde el archivo JSON"""
    try:
        with open(CONFIG_FILE, 'r') as f:
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
                'fecha_guardado': config['fecha_guardado']
            }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar la configuración: {e}")
        return None


def mostrar_configuracion():
    """Muestra la configuración guardada en una nueva ventana"""
    config = cargar_configuracion()
    ventana_config = tk.Toplevel(ventana)
    ventana_config.title("Configuración Guardada")
    ventana_config.geometry("400x250")
    ventana_config.resizable(False, False)
    ventana_config.configure(bg="#f0f0f0")

    if config:
        tk.Label(ventana_config, text="CONFIGURACIÓN GUARDADA",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        frame = tk.Frame(ventana_config, bg="#f0f0f0")
        frame.pack(pady=10, padx=20)

        # Mostrar los datos en un formato organizado
        tk.Label(frame, text="Grado:", font=("Arial", 10, "bold"),
                 bg="#f0f0f0", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text=config['grado'], font=("Arial", 10),
                 bg="#f0f0f0").grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Salón:", font=("Arial", 10, "bold"),
                 bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        tk.Label(frame, text=config['salon'], font=("Arial", 10),
                 bg="#f0f0f0").grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Fecha programada:", font=("Arial", 10, "bold"),
                 bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        tk.Label(frame, text=config['fecha'].strftime('%d/%m/%Y %H:%M'),
                 font=("Arial", 10), bg="#f0f0f0").grid(row=2, column=1, sticky="w")

        tk.Label(frame, text="Guardado el:", font=("Arial", 10, "bold"),
                 bg="#f0f0f0").grid(row=3, column=0, sticky="w")
        tk.Label(frame, text=config['fecha_guardado'], font=("Arial", 10),
                 bg="#f0f0f0").grid(row=3, column=1, sticky="w")
    else:
        tk.Label(ventana_config, text="No hay configuración guardada",
                 font=("Arial", 12), bg="#f0f0f0").pack(pady=50)


# Funciones de la interfaz principal


def actualizar_salones(event):
    grado_seleccionado = grado_var.get()
    salon_menu["values"] = salones_por_grado.get(grado_seleccionado, [])
    salon_var.set("")


def aplicar_mensaje():
    # Obtener los valores seleccionados
    grado = grado_var.get()
    salon = salon_var.get()

    # Validar selección de grado y salón
    if not grado or not salon:
        messagebox.showwarning("Advertencia", "Seleccione un grado y un salón")
        return

    # Obtener fecha y hora seleccionadas
    try:
        fecha_seleccionada = datetime(
            year=int(year_var.get()),
            month=int(mes_var.get()),
            day=int(dia_var.get()),
            hour=int(hora_var.get()),
            minute=int(minuto_var.get())
        )
    except ValueError as e:
        messagebox.showerror("Error", f"Fecha u hora inválida: {e}")
        return

    # Obtener fecha y hora actual
    ahora = datetime.now()

    # Comparar fechas
    if fecha_seleccionada > ahora:
        # Guardar la configuración en JSON
        if guardar_configuracion(grado, salon, fecha_seleccionada):
            messagebox.showinfo("Éxito",
                                f"Mensaje programado correctamente para:\n"
                                f"Grado: {grado}, Salón: {salon}\n"
                                f"Fecha: {fecha_seleccionada.strftime('%d/%m/%Y %H:%M')}")
            ventana.destroy()
            subprocess.run(["python", "ventana_de_envio_SMS.py"])
    else:
        messagebox.showwarning("Fecha no válida",
                               "La fecha y hora seleccionadas ya han pasado.\n"
                               "Por favor seleccione una fecha y hora futuras.")


# Crear ventana principal
ventana = tk.Tk()
ventana.iconbitmap("tuerca.ico")
ventana.title("Programación del mensaje SMS")
ventana.geometry("550x400")
ventana.resizable(False, False)
ventana.configure(bg="#f0f0f0")

# Variables de control
grado_var = tk.StringVar()
salon_var = tk.StringVar()
dia_var = tk.StringVar(value=str(datetime.now().day))
mes_var = tk.StringVar(value=str(datetime.now().month))
year_var = tk.StringVar(value=str(datetime.now().year))
hora_var = tk.StringVar(value=f"{datetime.now().hour:02d}")
minuto_var = tk.StringVar(value=f"{datetime.now().minute:02d}")

# Interfaz gráfica


# Título
tk.Label(ventana, text="Programación del mensaje SMS", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#333").pack(pady=5)

# Subtítulo
tk.Label(ventana, text="Seleccione los datos para el mensaje:", font=("Arial", 12), bg="#f0f0f0", fg="#555").pack(
    pady=2)

# Frame para organizar etiquetas y opciones
frame = tk.Frame(ventana, bg="#f0f0f0")
frame.pack(pady=16)

# ----------------- Selección de Grado y Salón -----------------
tk.Label(frame, text="GRADO:", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333").grid(row=0, column=0, padx=10,
                                                                                         pady=8, sticky="w")
grado_var = tk.StringVar()
grados = list(salones_por_grado.keys())
grados_menu = ttk.Combobox(frame, textvariable=grado_var, values=grados, state="readonly", font=("Arial", 10))
grados_menu.grid(row=0, column=1, padx=10, pady=8)
grados_menu.bind("<<ComboboxSelected>>", actualizar_salones)

tk.Label(frame, text="SALÓN:", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333").grid(row=1, column=0, padx=10,
                                                                                         pady=8, sticky="w")
salon_var = tk.StringVar()
salon_menu = ttk.Combobox(frame, textvariable=salon_var, state="readonly", font=("Arial", 10))
salon_menu.grid(row=1, column=1, padx=10, pady=8)

# ----------------- Selección de Fecha -----------------
tk.Label(frame, text="FECHA:", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333").grid(row=2, column=0, padx=10,
                                                                                         pady=8, sticky="w")
frame_fecha = tk.Frame(frame, bg="#f0f0f0")
frame_fecha.grid(row=2, column=1, padx=10, pady=8)

tk.OptionMenu(frame_fecha, dia_var, *[str(d) for d in range(1, 32)]).pack(side="left")
tk.OptionMenu(frame_fecha, mes_var, *[str(m) for m in range(1, 13)]).pack(side="left")
tk.OptionMenu(frame_fecha, year_var, *[str(a) for a in range(datetime.now().year, datetime.now().year + 5)]).pack(
    side="left")

# ----------------- Selección de Hora -----------------
tk.Label(frame, text="HORA:", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333").grid(row=3, column=0, padx=10,
                                                                                        pady=8, sticky="w")
frame_hora = tk.Frame(frame, bg="#f0f0f0")
frame_hora.grid(row=3, column=1, padx=10, pady=8)

tk.OptionMenu(frame_hora, hora_var, *[f"{h:02d}" for h in range(24)]).pack(side="left")
tk.Label(frame_hora, text=":", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333").pack(side="left")
tk.OptionMenu(frame_hora, minuto_var, *[f"{m:02d}" for m in range(60)]).pack(side="left")

# ----------------- Botones -----------------
frame_botones = tk.Frame(ventana, bg="#f0f0f0")
frame_botones.pack(pady=10)

boton_aplicar = tk.Button(frame_botones, text="Aplicar", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                          width=15, relief="raised", bd=3, command=aplicar_mensaje)
boton_aplicar.pack(side="left", padx=10)



# Ejecutar ventana
ventana.mainloop()
import subprocess
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
import hashlib
import os

def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='colegio'
        )
        return conexion
    except Error as e:
        messagebox.showerror("Error", f"No se pudo conectar a MySQL: {e}")
        return None

def registrar_usuario():
    nuevo_usuario = entrada_usuario.get().strip()
    nueva_contrasena = entrada_contrasena.get().strip()
    confirmacion = entrada_confirmacion.get().strip()
    email = entrada_email.get().strip()
    usuario_justvoip = entrada_usuario_justvoip.get().strip()
    contrasena_justvoip = entrada_contrasena_justvoip.get().strip()
    numero_justvoip = entrada_numero_justvoip.get().strip()

    if (not nuevo_usuario or not nueva_contrasena or not confirmacion or not email or
        not usuario_justvoip or not contrasena_justvoip or not numero_justvoip):
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return

    if nueva_contrasena != confirmacion:
        messagebox.showerror("Error", "Las contraseñas no coinciden")
        return

    if len(nueva_contrasena) < 6:
        messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
        return

    if not numero_justvoip.replace("+57", "").isdigit():
        messagebox.showerror("Error", "El número JustVoip debe contener solo dígitos")
        return

    if not numero_justvoip.startswith("+57"):
        numero_justvoip = "+57" + numero_justvoip.lstrip("0")

    contrasena_hash = hashlib.sha1(nueva_contrasena.encode()).hexdigest()

    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT username FROM usuarios WHERE username = %s", (nuevo_usuario,))
            if cursor.fetchone():
                messagebox.showerror("Error", "El nombre de usuario ya existe")
                return

            query = """
            INSERT INTO usuarios (
                username, password, email, fecha_registro,
                usuario_justVoip, contraseña_justVoip, numero_justVoip
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
            """
            cursor.execute(query, (
                nuevo_usuario, contrasena_hash, email,
                usuario_justvoip, contrasena_justvoip, numero_justvoip
            ))
            conexion.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            limpiar_campos()

        except Error as e:
            conexion.rollback()
            messagebox.showerror("Error", f"Error al registrar usuario: {e}")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

def limpiar_campos():
    entrada_usuario.delete(0, tk.END)
    entrada_contrasena.delete(0, tk.END)
    entrada_confirmacion.delete(0, tk.END)
    entrada_email.delete(0, tk.END)
    entrada_usuario_justvoip.delete(0, tk.END)
    entrada_contrasena_justvoip.delete(0, tk.END)
    entrada_numero_justvoip.delete(0, tk.END)

def volver_atras():
    ventana.destroy()
    subprocess.run(["python", "LOGIN.py"])

ventana = tk.Tk()
ventana.title("Registro de Usuario")
ventana.geometry("500x600")
ventana.resizable(False, False)
ventana.configure(bg='#f0f0f0')

try:
    ventana.iconbitmap("llave.ico")
except:
    pass

btn_atras = tk.Button(ventana, text="← Atrás", font=("Arial", 13, "bold"),
                      bg="#f0f0f0", fg="#333", bd=0, command=volver_atras)
btn_atras.place(x=10, y=10, width=80, height=30)

try:
    ruta_logo = os.path.join(os.path.dirname(__file__), "proteger.png")
    imagen_logo = tk.PhotoImage(file=ruta_logo)
    imagen_logo = imagen_logo.subsample(5, 5)
    marco_imagen = tk.Frame(ventana)
    marco_imagen.place(relx=0.5, rely=0.13, anchor="center")
    label_logo = tk.Label(marco_imagen, image=imagen_logo)
    label_logo.pack(padx=2, pady=2)
    ventana.image = imagen_logo
except Exception as e:
    print(f"Error cargando imagen: {e}")

fuente_label = ("Arial", 12)
fuente_entry = ("Arial", 11)
ancho_entry = 30
pad_y = 5

y_pos = 0.25
incremento = 0.08

# Usuario
tk.Label(ventana, text="Usuario:", font=fuente_label, bg='#f0f0f0').place(relx=0.1, rely=y_pos)
entrada_usuario = tk.Entry(ventana, font=fuente_entry, width=ancho_entry)
entrada_usuario.place(relx=0.4, rely=y_pos)

# Email
y_pos += incremento
tk.Label(ventana, text="Email:", font=fuente_label, bg='#f0f0f0').place(relx=0.1, rely=y_pos)
entrada_email = tk.Entry(ventana, font=fuente_entry, width=ancho_entry)
entrada_email.place(relx=0.4, rely=y_pos)

# Contraseña
y_pos += incremento
tk.Label(ventana, text="Contraseña:", font=fuente_label, bg='#f0f0f0').place(relx=0.1, rely=y_pos)
entrada_contrasena = tk.Entry(ventana, font=fuente_entry, show="*", width=ancho_entry)
entrada_contrasena.place(relx=0.4, rely=y_pos)

# Confirmar
y_pos += incremento
tk.Label(ventana, text="Confirmar:", font=fuente_label, bg='#f0f0f0').place(relx=0.1, rely=y_pos)
entrada_confirmacion = tk.Entry(ventana, font=fuente_entry, show="*", width=ancho_entry)
entrada_confirmacion.place(relx=0.4, rely=y_pos)

# Usuario JustVoip
y_pos += incremento
tk.Label(ventana, text="Usuario JustVoip:", font=fuente_label, bg='#f0f0f0').place(relx=0.1, rely=y_pos)
entrada_usuario_justvoip = tk.Entry(ventana, font=fuente_entry, width=ancho_entry)
entrada_usuario_justvoip.place(relx=0.4, rely=y_pos)

# Contraseña JustVoip
y_pos += incremento
tk.Label(ventana, text="Contraseña JustVoip:", font=fuente_label, bg='#f0f0f0').place(relx=0.1, rely=y_pos)
entrada_contrasena_justvoip = tk.Entry(ventana, font=fuente_entry, show="*", width=ancho_entry)
entrada_contrasena_justvoip.place(relx=0.4, rely=y_pos)

# Número JustVoip
y_pos += incremento
tk.Label(ventana, text="Número JustVoip:", font=fuente_label, bg='#f0f0f0').place(relx=0.1, rely=y_pos)
entrada_numero_justvoip = tk.Entry(ventana, font=fuente_entry, width=ancho_entry)
entrada_numero_justvoip.place(relx=0.4, rely=y_pos)

# Botón registrar
btn_registro = tk.Button(ventana, text="REGISTRAR USUARIO", width=25, height=2,
                         font=("Arial", 15, "bold"), bg="#4CAF50", fg="white",
                         command=registrar_usuario)
btn_registro.place(relx=0.5, rely=0.93, anchor="center")

ventana.mainloop()

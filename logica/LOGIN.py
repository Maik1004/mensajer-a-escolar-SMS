import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import mysql.connector
from mysql.connector import Error
import hashlib
import json




def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',  # Usuario de MySQL
            password='',  # Contraseña de MySQL
            database='colegio'  # Nombre de tu base de datos
        )
        return conexion
    except Error as e:
        messagebox.showerror("Error", f"No se pudo conectar a MySQL: {e}")
        return None





def validar_login():
    usuario = entrada_usuario.get().strip()
    contrasena = entrada_contrasena.get().strip()

    # Validar campos vacíos
    if not usuario or not contrasena:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return

    # Crear hash SHA-1 de la contraseña
    contrasena_hash = hashlib.sha1(contrasena.encode()).hexdigest()

    # Establecer conexión con la base de datos
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)

            # Consulta SQL para verificar usuario y contraseña
            query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (usuario, contrasena_hash))

            resultado = cursor.fetchone()

            if resultado:
                # Usuario a guardar
                username = None

                username = resultado['username']
                # Diccionario con los datos
                datos = {"username": username}

                # Guardar en archivo JSON con el nuevo nombre
                with open("usuario_quien_ingresa.json", "w") as archivo:
                    json.dump(datos, archivo)

                print("Usuario guardado en usuario_quien_ingresa.json", username)





                messagebox.showinfo("Éxito", f"Bienvenido {resultado['username']}")
                ventana.destroy()  # Cierra la ventana de login
                abrir_proyecto()  # Abre el menú principal


            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        except Error as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos: {e}")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()







def abrir_proyecto():
    ruta = os.path.join(os.path.dirname(__file__), "menu_principal.py")
    subprocess.run(["python", ruta])







# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Login")
ventana.geometry("500x600")
ventana.resizable(False, False)

# Configuración del icono
try:
    ventana.iconbitmap("3.ico")
except:
    pass

# Configuración del logo
try:
    ruta_logo = os.path.join(os.path.dirname(__file__), "logo.png")
    imagen_logo = tk.PhotoImage(file=ruta_logo)
    label_logo = tk.Label(ventana, image=imagen_logo)
    label_logo.pack(pady=5)
    ventana.image = imagen_logo
except:
    pass

# Campo de usuario
tk.Label(ventana, text="Usuario:", font=("Arial", 18)).place(relx=0.4, rely=0.42)
entrada_usuario = tk.Entry(ventana, font=("Arial", 16))
entrada_usuario.place(relx=0.27, rely=0.49)

# Campo de contraseña
tk.Label(ventana, text="Contraseña:", font=("Arial", 18)).place(relx=0.36, rely=0.56)
entrada_contrasena = tk.Entry(ventana, font=("Arial", 16), show="*")
entrada_contrasena.place(relx=0.27, rely=0.63)

# Botón de inicio de sesión
btn_login = tk.Button(ventana, text="Iniciar sesión", width=20, height=2,
                      font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                      command=validar_login)
btn_login.place(relx=0.31, rely=0.75)

ventana.mainloop()
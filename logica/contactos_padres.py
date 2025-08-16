import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import Error


# Conexión a MySQL
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Coloca tu contraseña si tienes una
        database="colegio"
    )


# Función para insertar datos
def insertar_datos():
    nombre = entry_nombre.get()
    apellido = entry_apellido.get()
    numero = entry_numero.get()
    grado = menu_grado.get()
    salon = menu_salon.get()

    if nombre and apellido and numero and grado and salon:
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            consulta = "INSERT INTO estudiantes (nombre, apellido, telefono_padres, grado, salon) VALUES (%s, %s, %s, %s, %s)"
            datos = (nombre, apellido, numero, int(grado), salon)
            cursor.execute(consulta, datos)
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Estudiante agregado correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar: {e}")
    else:
        messagebox.showwarning("Campos vacíos", "Completa todos los campos")


def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_apellido.delete(0, tk.END)
    entry_numero.delete(0, tk.END)


def mostrar_contactos():
    grado = grado_var.get()
    salon = salon_var.get()

    if not grado or not salon:
        messagebox.showwarning("Selección requerida", "Por favor seleccione un grado y un salón")
        return

    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT nombre, apellido, telefono_padres, grado, salon 
            FROM estudiantes 
            WHERE grado = %s AND salon = %s
            ORDER BY apellido, nombre
        """, (grado, salon))

        estudiantes = cursor.fetchall()

        if not estudiantes:
            messagebox.showinfo("Información", "No se encontraron estudiantes para el grado y salón seleccionados.")
            return

        # Crear ventana emergente
        ventana = tk.Toplevel(root)
        ventana.title(f"Contactos - Grado {grado} Salón {salon}")
        ventana.iconbitmap("contacto.ico")
        ventana.geometry("800x400")
        ventana.resizable(False, False)

        # Frame para la tabla
        frame_tabla = tk.Frame(ventana)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview para mostrar los datos
        tree = ttk.Treeview(frame_tabla, columns=("Nombre", "Apellido", "Teléfono Padres", "Grado", "Salón"),
                            show="headings")

        # Configurar columnas
        tree.heading("Nombre", text="Nombre")
        tree.heading("Apellido", text="Apellido")
        tree.heading("Teléfono Padres", text="Teléfono Padres")
        tree.heading("Grado", text="Grado")
        tree.heading("Salón", text="Salón")

        tree.column("Nombre", width=150)
        tree.column("Apellido", width=150)
        tree.column("Teléfono Padres", width=150)
        tree.column("Grado", width=80)
        tree.column("Salón", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        # Insertar datos
        for estudiante in estudiantes:
            tree.insert("", tk.END, values=estudiante)

        conexion.close()
    except Error as e:
        messagebox.showerror("Error", f"Error al obtener estudiantes: {e}")


def eliminar_contacto():
    numero = entry_eliminar.get()

    if not numero:
        messagebox.showwarning("Campo vacío", "Por favor ingrese un número de teléfono a eliminar")
        return

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar si existe el contacto
        cursor.execute("SELECT * FROM estudiantes WHERE telefono_padres = %s", (numero,))
        resultado = cursor.fetchone()

        if not resultado:
            messagebox.showinfo("Información", "No se encontró ningún contacto con ese número")
            return

        # Confirmar eliminación
        respuesta = messagebox.askyesno("Confirmar",
                                        f"¿Está seguro que desea eliminar el contacto con número {numero}?")

        if respuesta:
            cursor.execute("DELETE FROM estudiantes WHERE telefono_padres = %s", (numero,))
            conexion.commit()
            messagebox.showinfo("Éxito", "Contacto eliminado correctamente")
            entry_eliminar.delete(0, tk.END)

        conexion.close()
    except Error as e:
        messagebox.showerror("Error", f"No se pudo eliminar el contacto: {e}")


def actualizar_salones(event):
    grado = grado_var.get()
    menu_salon['values'] = salones_por_grado.get(grado, [])
    if salones_por_grado.get(grado):
        menu_salon.current(0)


def cerrar_ventana():
    root.destroy()
    subprocess.run(["python", "menu_principal.py"])


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

root = tk.Tk()
root.title("Gestión de contactos padres de familia")
root.iconbitmap("contacto.ico")
root.geometry("600x550")
root.resizable(False, False)

# Botón Atrás
btn_atras = tk.Button(root, text="↩", bg="red", fg="white", font=("Arial", 12, "bold"), width=5, command=cerrar_ventana)
btn_atras.place(x=3, y=3)

# Título y subtítulo
tk.Label(root, text="Gestión de Contactos", font=("Arial", 16, "bold")).pack()
tk.Label(root, text="Padres de familia", font=("Arial", 14)).pack(pady=5)

# Marco para grado y salón (ahora arriba del frame de agregar)
frame_seleccion = tk.Frame(root, bd=2, relief="ridge", padx=10, pady=10)
frame_seleccion.pack(pady=5)

tk.Label(frame_seleccion, text="Seleccione Grado y Salón:", font=("Arial", 12, "bold")).grid(row=0, column=0,
                                                                                             columnspan=2, pady=5)

tk.Label(frame_seleccion, text="Grado:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
grado_var = tk.StringVar()
menu_grado = ttk.Combobox(frame_seleccion, textvariable=grado_var, values=list(salones_por_grado.keys()),
                          state="readonly", width=10)
menu_grado.grid(row=1, column=1, padx=5, pady=5, sticky="w")
grado_var.set("Seleccione")
menu_grado.bind("<<ComboboxSelected>>", actualizar_salones)

tk.Label(frame_seleccion, text="Salón:", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
salon_var = tk.StringVar()
menu_salon = ttk.Combobox(frame_seleccion, textvariable=salon_var, state="readonly", width=10)
menu_salon.grid(row=2, column=1, padx=5, pady=5, sticky="w")

btn_mostrar = tk.Button(frame_seleccion, text="Mostrar Contactos", bg="orange", fg="white", font=("Arial", 12, "bold"),
                        width=15, relief="raised", bd=3, command=mostrar_contactos)
btn_mostrar.grid(row=3, column=0, columnspan=2, pady=10)

# Marco principal (ahora solo contiene los frames de agregar y eliminar)
frame_principal = tk.Frame(root)
frame_principal.pack(pady=10)

# Marco para agregar contacto
frame_agregar = tk.Frame(frame_principal, bd=3, relief="ridge", padx=10, pady=10)
frame_agregar.grid(row=0, column=0, padx=10)

tk.Label(frame_agregar, text="Agregar Nuevo Contacto:", font=("Arial", 12, "bold")).pack(pady=5)

tk.Label(frame_agregar, text="Nombre:", font=("Arial", 12)).pack()
entry_nombre = tk.Entry(frame_agregar, font=("Arial", 12), width=22)
entry_nombre.pack(pady=2)

tk.Label(frame_agregar, text="Apellido:", font=("Arial", 12)).pack()
entry_apellido = tk.Entry(frame_agregar, font=("Arial", 12), width=22)
entry_apellido.pack(pady=2)

tk.Label(frame_agregar, text="Número:", font=("Arial", 12)).pack()
entry_numero = tk.Entry(frame_agregar, font=("Arial", 12), width=22)
entry_numero.pack(pady=2)

btn_agregar = tk.Button(frame_agregar, text="Agregar", bg="green", fg="white", font=("Arial", 12, "bold"), width=15,
                        relief="raised", bd=5, command=insertar_datos)
btn_agregar.pack(pady=10)

# Marco para eliminar contacto
frame_eliminar = tk.Frame(frame_principal, bd=3, relief="ridge", padx=10, pady=10)
frame_eliminar.grid(row=0, column=1, padx=10)

tk.Label(frame_eliminar, text="Eliminar Contacto:", font=("Arial", 12, "bold")).pack(pady=5)

tk.Label(frame_eliminar, text="Ingrese número a eliminar:", font=("Arial", 12)).pack()
entry_eliminar = tk.Entry(frame_eliminar, font=("Arial", 12), width=22)
entry_eliminar.pack(pady=5)

btn_eliminar = tk.Button(frame_eliminar, text="Eliminar", bg="red", fg="white", font=("Arial", 12, "bold"), width=15,
                         relief="raised", bd=5, command=eliminar_contacto)
btn_eliminar.pack(pady=10)

root.mainloop()
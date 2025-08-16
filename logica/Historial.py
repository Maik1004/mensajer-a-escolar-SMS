import tkinter as tk
import subprocess
import mysql.connector
from mysql.connector import Error
from tkinter import ttk, messagebox
from datetime import datetime


class HistorialMensajes:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.mostrar_historial()

    def setup_ui(self):
        """Configura la interfaz gráfica"""
        self.root.title("Historial de mensajería")
        self.root.geometry("950x700")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f2f5")

        # Frame principal con borde sutil
        main_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Barra superior
        top_frame = tk.Frame(main_frame, bg="#ffffff")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # Botón Volver (estilo moderno)
        btn_volver = tk.Button(top_frame, text="← Volver", font=("Arial", 10, "bold"),
                               bg="#f44336", fg="white", bd=0, padx=15, pady=5,
                               activebackground="#d32f2f", command=self.volver_atras)
        btn_volver.pack(side=tk.LEFT)

        # Título centrado
        tk.Label(top_frame, text="Historial de Mensajes", bg="#ffffff",
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT, expand=True)

        # Botón Actualizar (estilo moderno y atractivo)
        btn_actualizar = tk.Button(top_frame, text="↻↺ Actualizar", font=("Arial", 10, "bold"),
                                   bg="#4CAF50", fg="white", bd=0, padx=15, pady=5,
                                   activebackground="#388E3C", command=self.mostrar_historial)
        btn_actualizar.pack(side=tk.RIGHT)

        # Frame para el árbol (con sombra sutil)
        tree_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SUNKEN)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Treeview con estilo mejorado
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#333333",
                        rowheight=25,
                        fieldbackground="#ffffff",
                        font=("Arial", 10))

        style.configure("Treeview.Heading",
                        font=("Arial", 10, "bold"),
                        background="#4CAF50",
                        foreground="white")

        style.map("Treeview", background=[("selected", "#2196F3")])

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Grado", "Salón", "Mensaje", "Fecha", "Estado"),
                                 show="headings", selectmode="extended")

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configurar columnas
        columns = [
            ("ID", 60, "center"),
            ("Grado", 90, "center"),
            ("Salón", 90, "center"),
            ("Mensaje", 350, "w"),
            ("Fecha", 150, "center"),
            ("Estado", 100, "center")
        ]

        for col, width, anchor in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)

        # Configuración de grid para expansión
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Bind doble click
        self.tree.bind("<Double-1>", self.mostrar_detalle_completo)

    # [Resto de los métodos permanecen igual...]
    def conectar_db(self):
        """Establece conexión con la base de datos"""
        try:
            return mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='colegio',
                connect_timeout=5
            )
        except Error as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
            return None

    def obtener_datos_historial(self):
        """Obtiene datos del historial desde MySQL"""
        conn = self.conectar_db()
        if not conn:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, grado, salon, mensaje, 
                       DATE_FORMAT(fecha_envio, '%Y-%m-%d %H:%i') as fecha, 
                       estado
                FROM historial_de_mensajes 
                ORDER BY fecha_envio DESC
                LIMIT 200
            """)
            return cursor.fetchall()
        except Error as e:
            messagebox.showerror("Error en consulta", f"Error al obtener historial:\n{e}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def mostrar_historial(self):
        """Muestra los datos en el Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        datos = self.obtener_datos_historial()

        if not datos:
            self.tree.insert("", "end", values=("Sin datos", "", "", "", "", ""))
            return

        for registro in datos:
            mensaje = (registro['mensaje'][:75] + '...') if len(registro['mensaje']) > 75 else registro['mensaje']
            self.tree.insert("", "end", values=(
                registro['id'],
                registro['grado'],
                registro['salon'],
                mensaje,
                registro['fecha'],
                registro['estado']
            ))

    def mostrar_detalle_completo(self, event):
        """Muestra el mensaje completo al hacer doble click"""
        item = self.tree.focus()
        if not item:
            return

        item_data = self.tree.item(item)
        if item_data['values'][0] == "Sin datos":
            return

        conn = self.conectar_db()
        if not conn:
            return

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT mensaje, fecha_envio 
                FROM historial_de_mensajes 
                WHERE id = %s
            """, (item_data['values'][0],))

            mensaje = cursor.fetchone()
            if mensaje:
                detalle = f"Mensaje completo:\n\n{mensaje['mensaje']}\n\n" \
                          f"Fecha de envío: {mensaje['fecha_envio']}"
                messagebox.showinfo("Detalle del mensaje", detalle)
        except Error as e:
            messagebox.showerror("Error", f"No se pudo obtener el mensaje:\n{e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def volver_atras(self):
        """Regresa al menú principal"""
        self.root.destroy()
        subprocess.run(["python", "menu_principal.py"])


if __name__ == "__main__":
    root = tk.Tk()
    app = HistorialMensajes(root)
    root.mainloop()
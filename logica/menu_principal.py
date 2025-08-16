import tkinter as tk
import os
import subprocess



# Ventana para Enviar SMS
def ventana_sms():
    ventana.destroy()
    subprocess.run(["python", "Programacion_del_mensaje.py"])

# Ventana para Historial de Mensajería
def ventana_historial():
    ventana.destroy()
    subprocess.run(["python", "Historial.py"])


# Ventana para Configuración de Salones
def ventana_config():
    ventana.destroy()
    subprocess.run(["python", "contactos_padres.py"])

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Menú SMS")
ventana.geometry("500x500")
ventana.resizable(False, False)



#icono de la ventana----------------------------------
ventana.iconbitmap("2.ico")



# Logo en formato PNG
ruta_logo = os.path.join(os.path.dirname(__file__), "login.png")
if os.path.exists(ruta_logo):
    logo = tk.PhotoImage(file=ruta_logo)
    tk.Label(ventana, image=logo).pack(pady=10)
    ventana.iconphoto(True, logo)  # Para cambiar el icono de la ventana

# Botones
btn_sms = tk.Button(ventana, text="Enviar SMS", font=("Arial", 15, "bold"), bg="#4CAF50", fg="white", command=lambda:ventana_sms())
btn_sms.place(relx=0.38, rely=0.55)

btn_historial = tk.Button(ventana, text="Historial de mensajería", font=("Arial", 15, "bold"), bg="#2196F3", fg="white", command=lambda:ventana_historial())
btn_historial.place(relx=0.28, rely=0.68)

btn_config = tk.Button(ventana, text="Configuración de salones", font=("Arial", 15, "bold"), bg="#FFC107", fg="white", command=lambda:ventana_config())
btn_config.place(relx=0.255, rely=0.82)

# Mantener referencia de la imagen para evitar que se borre de memoria
ventana.image = logo

# Mostrar ventana
ventana.mainloop()


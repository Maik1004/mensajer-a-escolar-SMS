import mysql.connector
from mysql.connector import Error
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Configuración de logging
logging.basicConfig(
    filename='sms_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'colegio'
}


class SMSsender:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Configura el navegador Chrome para Google Messages"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("user-data-dir=C:/Users/TuUsuario/AppData/Local/Google/Chrome/User Data/Default")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.get("https://messages.google.com/web")
            time.sleep(10)  # Tiempo para escanear QR inicial
        except Exception as e:
            logging.error(f"Error configurando Chrome: {str(e)}")
            raise

    def obtener_mensajes_pendientes(self):
        """Obtiene mensajes no enviados de la base de datos"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT id, salon, mensaje, fecha_envio 
            FROM historial_de_mensajes 
           WHERE estado = 'pendiente' AND fecha_envio <= NOW()
            """
            cursor.execute(query)
            return cursor.fetchall()

        except Error as e:
            logging.error(f"Error de base de datos: {str(e)}")
            return []
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()

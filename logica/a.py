from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import urllib.parse

numero = "573165641004"  # sin el "+" pero con el código de país
mensaje = "Hola, este es un mensaje automático enviado con Selenium 🤖"

# Codifica el mensaje para que se pase como parámetro
mensaje_codificado = urllib.parse.quote(mensaje)

# URL con el mensaje
url = f"https://web.whatsapp.com/send?phone={numero}&text={mensaje_codificado}"

# Inicializar el navegador
driver = webdriver.Chrome()  # Asegúrate de tener chromedriver.exe
driver.get(url)

print("🔄 Esperando que escanees el código QR de WhatsApp Web...")
time.sleep(20)  # Tiempo para escanear el QR (ajusta si ya estás logueado)

try:
    print("⏳ Esperando a que el campo de texto esté listo...")
    time.sleep(10)  # Esperar a que cargue la conversación

    # Presionar ENTER para enviar el mensaje
    input_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
    input_box.send_keys(Keys.ENTER)

    print("✅ Mensaje enviado con éxito.")

except Exception as e:
    print("❌ Ocurrió un error:", e)

# No cerrar inmediatamente el navegador
time.sleep(10)
driver.quit()

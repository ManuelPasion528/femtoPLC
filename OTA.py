import network
import urequests
import machine
import time

# Configuración WiFi
SSID = "CUARTO PISO"
PASSWORD = "N64D9542CC1AC"

def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Conectando a WiFi...")
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        
        # Esperar hasta que se conecte
        for _ in range(20):  # Intentar durante 20 segundos
            if sta_if.isconnected():
                break
            time.sleep(1)
        
        if not sta_if.isconnected():
            print("Error: No se pudo conectar a WiFi")
            return False
        else:
            print("Conectado a WiFi!", sta_if.ifconfig())
            return True
    else:
        print("Ya conectado a WiFi!", sta_if.ifconfig())
        return True

# Descargar actualización desde Flask
def update_firmware():
    url = "http://192.168.18.48:5000/update"  # Cambia por la IP de tu servidor Flask
    try:
        response = urequests.get(url)
        with open("main.py", "w") as f:
            f.write(response.text)
        response.close()
        print("Actualización completada! Reiniciando...")
        machine.reset()  # Reinicia el ESP32 para ejecutar la actualización
    except Exception as e:
        print("Error en OTA:", e)

# Ejecutar el proceso
if connect_wifi():
    update_firmware()
else:
    print("No se pudo conectar a WiFi. Verifica la configuración.")
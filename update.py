import machine
import time
led = machine.Pin(25, machine.Pin.OUT)
while True:
    led.value(1)
    print("Prendido")
    time.sleep(1)
    led.value(0)
    print("apagado")
    time.sleep(1)

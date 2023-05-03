import serial
import time

arduino = serial.Serial('/dev/cu.SLAB_USBtoUART', 115200)
time.sleep(1);

while(True):
    comando = input("Cosa posso fare per te? ").encode()
    arduino.write(comando)
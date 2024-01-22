import serial
import time

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)


def read():
    time.sleep(1)
    data = arduino.readline()
    return  data


while True:
    value  = read()
    if value:
        print(value)

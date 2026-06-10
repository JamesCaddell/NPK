#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
from pymodbus.client import ModbusSerialClient

RE_PIN = 17
DE_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(RE_PIN, GPIO.OUT)
GPIO.setup(DE_PIN, GPIO.OUT)

def receive_mode():
    GPIO.output(DE_PIN, GPIO.LOW)
    GPIO.output(RE_PIN, GPIO.LOW)

def transmit_mode():
    GPIO.output(DE_PIN, GPIO.HIGH)
    GPIO.output(RE_PIN, GPIO.HIGH)

class RS485Client(ModbusSerialClient):
    def send(self, request):
        transmit_mode()
        time.sleep(0.01)

        result = super().send(request)

        self.socket.flush()
        time.sleep(0.01)
        receive_mode()

        return result

receive_mode()

client = RS485Client(
    port="/dev/serial0",
    baudrate=9600,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=2,
)

try:
    if not client.connect():
        print("Could not connect to serial port")
        exit()

    print("Connected. Reading JXCT sensor...")

    while True:
        # Try slave/device address 1
        # Read 7 registers starting at address 0
        result = client.read_holding_registers(
            address=0,
            count=7,
            slave=1
        )

        if result.isError():
            print("Modbus error / no response")
        else:
            print("Raw registers:", result.registers)

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped.")

finally:
    client.close()
    receive_mode()
    GPIO.cleanup()

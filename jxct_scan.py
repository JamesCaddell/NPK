!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
from pymodbus.client import ModbusSerialClient

# MAX485 control pins
RE_PIN = 17
DE_PIN = 27

# Things to test
BAUD_RATES = [4800, 9600, 19200, 38400]
DEVICE_IDS = list(range(1, 11)) + [255]

# Common register starts for sensors
REGISTER_STARTS = [0, 1, 6, 256]
REGISTER_COUNT = 7

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
    def send(self, request, **kwargs):
        transmit_mode()
        time.sleep(0.01)

        result = super().send(request, **kwargs)

        try:
            self.socket.flush()
        except Exception:
            pass

        time.sleep(0.03)
        receive_mode()

        return result

def try_read(baudrate, device_id, address):
    receive_mode()

    client = RS485Client(
        port="/dev/serial0",
        baudrate=baudrate,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
        retries=1,
    )

    try:
        if not client.connect():
            return None

        result = client.read_holding_registers(
            address=address,
            count=REGISTER_COUNT,
            device_id=device_id
        )

        if result.isError():
            return None

        return result.registers

    except Exception:
        return None

    finally:
        client.close()
        receive_mode()

try:
    print("Starting JXCT Modbus scan...")
    print("Testing baud rates:", BAUD_RATES)
    print("Testing device IDs:", DEVICE_IDS)
    print("Testing register starts:", REGISTER_STARTS)
    print()

    found = False

    for baud in BAUD_RATES:
        print(f"--- Testing baudrate {baud} ---")

        for device_id in DEVICE_IDS:
            for address in REGISTER_STARTS:
                print(f"Trying baud={baud}, device_id={device_id}, address={address}...")

                registers = try_read(baud, device_id, address)

                if registers is not None:
                    found = True
                    print()
                    print("FOUND POSSIBLE SENSOR RESPONSE")
                    print(f"Baudrate:   {baud}")
                    print(f"Device ID:  {device_id}")
                    print(f"Address:    {address}")
                    print(f"Registers:  {registers}")
                    print()

                    # Keep going in case there are multiple valid register areas

        print()

    if not found:
        print("No sensor response found.")
        print("Now manually swap A/B wires and run this script again.")

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    receive_mode()
    GPIO.cleanup()

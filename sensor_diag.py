import serial
import time
import RPi.GPIO as GPIO

RE_PIN = 17
DE_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(RE_PIN, GPIO.OUT)
GPIO.setup(DE_PIN, GPIO.OUT)

def crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def build_request(addr):
    msg = bytearray([
        addr,      # slave address
        0x03,      # read holding register
        0x00, 0x12,# humidity register
        0x00, 0x01 # read one register
    ])

    crc = crc16(msg)
    msg.append(crc & 0xFF)
    msg.append((crc >> 8) & 0xFF)

    return bytes(msg)

ports = [
    "/dev/ttyS0",
    "/dev/ttyAMA0"
]

bauds = [
    9600,
    4800,
    2400
]

addresses = range(1, 11)

for port in ports:

    print("\n" + "="*60)
    print(f"TESTING PORT: {port}")
    print("="*60)

    try:

        for baud in bauds:

            print(f"\nBaud: {baud}")

            ser = serial.Serial(
                port=port,
                baudrate=baud,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )

            for addr in addresses:

                request = build_request(addr)

                GPIO.output(RE_PIN, 1)
                GPIO.output(DE_PIN, 1)

                time.sleep(0.01)

                ser.reset_input_buffer()
                ser.write(request)
                ser.flush()

                time.sleep(0.02)

                GPIO.output(RE_PIN, 0)
                GPIO.output(DE_PIN, 0)

                response = ser.read(32)

                if len(response) > 0:
                    print(
                        f"FOUND RESPONSE! "
                        f"port={port} "
                        f"baud={baud} "
                        f"addr={addr}"
                    )
                    print("TX:", request.hex())
                    print("RX:", response.hex())
                else:
                    print(
                        f"No response "
                        f"(addr={addr})"
                    )

            ser.close()

    except Exception as e:
        print(f"ERROR on {port}: {e}")

GPIO.cleanup()

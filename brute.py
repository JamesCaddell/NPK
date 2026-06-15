import serial, time

PORT = '/dev/ttyUSB0'

def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFF, (crc >> 8) & 0xFF

ser = serial.Serial(PORT, 9600, bytesize=8, parity='N', stopbits=1, timeout=1)
time.sleep(0.1)

# Just test the registers we KNOW work first
KNOWN = [0x001E, 0x001F, 0x0020, 0x0012, 0x0014, 0x0015, 0x0006]

print("Testing known working registers first...\n")
for reg in KNOWN:
    ser.flushInput()
    frame = [0x01, 0x03, (reg >> 8) & 0xFF, reg & 0xFF, 0x00, 0x01]
    lo, hi = crc16(frame)
    frame += [lo, hi]
    print(f"Sending 0x{reg:04X}: {' '.join(f'{b:02X}' for b in frame)}")
    ser.write(bytes(frame))
    time.sleep(0.5)
    resp = ser.read(10)
    print(f"Response ({len(resp)} bytes): {' '.join(f'{b:02X}' for b in resp)}\n")

ser.close()

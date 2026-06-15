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

# Scan 0x0000 to 0x0040
print(f"{'REG':>6}  {'RAW':>6}  RESPONSE")
print("-" * 40)

for reg in range(0x0000, 0x0041):
    ser.flushInput()
    frame = [0x01, 0x03, (reg >> 8) & 0xFF, reg & 0xFF, 0x00, 0x01]
    lo, hi = crc16(frame)
    frame += [lo, hi]
    ser.write(bytes(frame))
    time.sleep(0.2)
    resp = ser.read(10)

    if len(resp) >= 7 and resp[1] == 0x03 and resp[2] == 0x02:
        raw = int.from_bytes(resp[3:5], 'big')
        print(f"  0x{reg:04X}  {raw:>6}  ✓ VALID")
    elif len(resp) >= 3 and resp[1] == 0x83:
        pass  # skip exceptions, too noisy
    else:
        pass  # skip no response

ser.close()
print("\nDone — paste the VALID lines above")

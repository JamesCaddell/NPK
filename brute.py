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

REGS = {
    0x0000: 'Humidity',
    0x0001: 'Temperature',
    0x0002: 'Conductivity',
    0x0003: 'pH',
    0x0004: 'Nitrogen',
    0x0005: 'Phosphorus',
    0x0006: 'Potassium',
    0x0007: 'Salinity',
    0x0008: 'TDS',
}

for func in [0x03, 0x04]:
    print(f"\n=== Function code 0x{func:02X} ===")
    for reg, name in REGS.items():
        ser.flushInput()
        frame = [0x01, func,
                 (reg >> 8) & 0xFF, reg & 0xFF,
                 0x00, 0x01]  # read 1 register
        lo, hi = crc16(frame)
        frame += [lo, hi]
        ser.write(bytes(frame))
        time.sleep(0.3)
        resp = ser.read(20)
        hex_resp = ' '.join(f'{b:02X}' for b in resp)

        # Valid response = 5 bytes: addr + func + 0x02 + 2 data bytes + 2 CRC
        if len(resp) >= 5 and resp[1] == func:
            val = int.from_bytes(resp[3:5], 'big')
            print(f"  reg 0x{reg:04X} {name:12s}: RAW={val}  → {hex_resp}")
        else:
            print(f"  reg 0x{reg:04X} {name:12s}: exception/no resp → {hex_resp}")

ser.close()

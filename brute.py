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
    0x001E: ('Nitrogen',     1,  'mg/kg'),
    0x001F: ('Phosphorus',   1,  'mg/kg'),
    0x0020: ('Potassium',    1,  'mg/kg'),
    0x0014: ('Salinity',     1,  'mg/L'),
    0x0012: ('Humidity',     10, '%RH'),
    0x0015: ('Conductivity', 1,  'µS/cm'),
    0x0006: ('pH',           10, ''),
}

print("Reading registers...\n")
for reg, (name, divisor, unit) in REGS.items():
    ser.flushInput()
    frame = [0x01, 0x03, (reg >> 8) & 0xFF, reg & 0xFF, 0x00, 0x01]
    lo, hi = crc16(frame)
    frame += [lo, hi]
    ser.write(bytes(frame))
    time.sleep(0.3)
    resp = ser.read(10)
    hex_resp = ' '.join(f'{b:02X}' for b in resp)

    if len(resp) >= 7 and resp[1] == 0x03 and resp[2] == 0x02:
        raw = int.from_bytes(resp[3:5], 'big')
        val = raw / divisor
        print(f"  {name:14s}: {val} {unit}  (raw={raw})")
    elif len(resp) >= 3 and resp[1] in [0x83, 0x84]:
        print(f"  {name:14s}: EXCEPTION code={resp[2]:02X} → {hex_resp}")
    else:
        print(f"  {name:14s}: no response → {hex_resp}")

ser.close()

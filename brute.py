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

ser = serial.Serial(PORT, 4800, bytesize=8, parity='N', stopbits=1, timeout=1)
time.sleep(0.1)
ser.flushInput()

# ── Step 1: Broadcast slave ID enquiry (page 7) ──────────────────────────
# Works regardless of slave address - good sanity check
print("=== Step 1: Broadcast slave ID enquiry ===")
broadcast = bytes([0xFF, 0x03, 0x07, 0xD0, 0x00, 0x01, 0x91, 0x59])
ser.write(broadcast)
time.sleep(0.5)
resp = ser.read(20)
print(f"Response: {' '.join(f'{b:02X}' for b in resp)}")
# Expected: FF 03 02 00 01 50 50
# byte[3:5] = slave address

if len(resp) >= 5:
    slave = resp[4]
    print(f"Sensor slave address = {slave}")
else:
    slave = 1
    print("No response to broadcast - check A/B wiring, trying slave=1 anyway")

# ── Step 2: Read all 7 registers using exact datasheet frame ─────────────
print("\n=== Step 2: Read humidity+temp+EC+pH+N+P+K ===")
# Exact frame from page 4: 01 03 00 00 00 07 04 08
read_all = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x07, 0x04, 0x08])
ser.flushInput()
ser.write(read_all)
time.sleep(0.5)
resp2 = ser.read(25)
print(f"Raw: {' '.join(f'{b:02X}' for b in resp2)}")
# Expected: 01 03 0E [14 bytes data] [2 bytes CRC]

if len(resp2) >= 19 and resp2[0] == 0x01 and resp2[1] == 0x03:
    d = resp2[3:17]
    humidity     = int.from_bytes(d[0:2],  'big') / 10
    temperature  = int.from_bytes(d[2:4],  'big') / 10
    conductivity = int.from_bytes(d[4:6],  'big')
    ph           = int.from_bytes(d[6:8],  'big') / 10
    nitrogen     = int.from_bytes(d[8:10], 'big')
    phosphorus   = int.from_bytes(d[10:12],'big')
    potassium    = int.from_bytes(d[12:14],'big')

    print(f"\n  Humidity:     {humidity} %RH")
    print(f"  Temperature:  {temperature} °C")
    print(f"  Conductivity: {conductivity} µS/cm")
    print(f"  pH:           {ph}")
    print(f"  Nitrogen:     {nitrogen} mg/kg")
    print(f"  Phosphorus:   {phosphorus} mg/kg")
    print(f"  Potassium:    {potassium} mg/kg")
else:
    print("No valid response - try swapping A/B wires then rerun")

ser.close()

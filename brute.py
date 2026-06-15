import serial, time

PORT   = '/dev/ttyUSB0'
BAUD   = 9600
SLAVE  = 0x01

ser = serial.Serial(PORT, BAUD, bytesize=8, parity='N', stopbits=1, timeout=1)
time.sleep(0.1)
ser.flushInput()

# Exact frame: slave=01, func=03, start=0x0000, count=7 registers
# CRC recalculated for count=7 at 9600
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

frame = [0x01, 0x03, 0x00, 0x00, 0x00, 0x07]
lo, hi = crc16(frame)
frame += [lo, hi]
print(f"Sending: {' '.join(f'{b:02X}' for b in frame)}")

ser.write(bytes(frame))
time.sleep(0.5)
resp = ser.read(50)
print(f"Raw response ({len(resp)} bytes): {' '.join(f'{b:02X}' for b in resp)}")

# Expected: 01 03 0E [14 bytes] [2 CRC] = 19 bytes total
if len(resp) >= 19 and resp[0] == 0x01 and resp[1] == 0x03 and resp[2] == 0x0E:
    d = resp[3:17]
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
    print(f"\nShort/unexpected response - raw bytes above")
    print("Paste the raw line and we'll decode it manually")

ser.close()

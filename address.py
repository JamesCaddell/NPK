import serial, time

ser = serial.Serial('/dev/ttyUSB0', 4800, timeout=1)

# Function code 0x03, start 0x0000, read 9 registers
# CRC calculated correctly for this frame
frame_03 = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x09, 0xC5, 0xCD])

print("Trying function code 0x03...")
ser.write(frame_03)
time.sleep(0.5)
resp = ser.read(23)  # 9 registers = 18 data bytes + 5 overhead
print(' '.join(f'{b:02X}' for b in resp))

if len(resp) >= 5:
    # Parse each register (big-endian 16-bit)
    data = resp[3:-2]  # strip header and CRC
    regs = [int.from_bytes(data[i:i+2], 'big') for i in range(0, len(data), 2)]
    labels = ['Humidity(x0.1%RH)', 'Temp(x0.1°C)', 'EC(µS/cm)', 
              'pH(x0.1)', 'N(mg/kg)', 'P(mg/kg)', 'K(mg/kg)',
              'Salinity(mg/L)', 'TDS(mg/L)']
    for label, val in zip(labels, regs):
        print(f"  {label}: {val}")
else:
    print("No valid response with 0x03, trying 0x30...")
    ser.flushInput()
    # Same frame but with 0x30 function code — CRC will differ
    frame_30 = bytes([0x01, 0x30, 0x00, 0x00, 0x00, 0x09, 0xC1, 0xF4])
    ser.write(frame_30)
    time.sleep(0.5)
    resp2 = ser.read(23)
    print(' '.join(f'{b:02X}' for b in resp2))

ser.close()

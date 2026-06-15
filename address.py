import serial, time

ser = serial.Serial('/dev/ttyUSB0', 4800, timeout=2)
ser.flushInput()

# Just listen for 3 seconds - any traffic at all?
print("Listening for any data on the bus...")
time.sleep(0.1)
ser.write(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x09, 0xC5, 0xCD]))
time.sleep(1)
raw = ser.read(50)
print(f"Received {len(raw)} bytes: {' '.join(f'{b:02X}' for b in raw)}")
ser.close()

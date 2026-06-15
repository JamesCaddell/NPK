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
    low  = crc & 0xFF
    high = (crc >> 8) & 0xFF
    return low, high

def build_frame(slave, func, reg, count):
    frame = [slave, func, (reg >> 8) & 0xFF, reg & 0xFF,
             (count >> 8) & 0xFF, count & 0xFF]
    lo, hi = crc16(frame)
    frame += [lo, hi]
    return bytes(frame)

BAUDS    = [4800, 9600, 2400, 19200, 38400, 1200]
SLAVES   = [0x01, 0x02, 0xFF]
FUNCS    = [0x03, 0x04]
REGS     = [0x0000]
COUNT    = 9

print(f"{'BAUD':>8} {'SLAVE':>6} {'FUNC':>5} {'REG':>5} {'BYTES':>6}  RESPONSE")
print("-" * 70)

found = []

for baud in BAUDS:
    try:
        ser = serial.Serial(PORT, baud, bytesize=8,
                            parity='N', stopbits=1, timeout=1)
    except Exception as e:
        print(f"Could not open port: {e}")
        break

    for slave in SLAVES:
        for func in FUNCS:
            for reg in REGS:
                ser.flushInput()
                frame = build_frame(slave, func, reg, COUNT)
                ser.write(frame)
                time.sleep(0.5)
                resp = ser.read(50)

                hex_resp = ' '.join(f'{b:02X}' for b in resp)
                n = len(resp)

                print(f"{baud:>8} {hex(slave):>6} {hex(func):>5} {hex(reg):>5} {n:>6}  {hex_resp}")

                # A valid response starts with slave+func and has >3 bytes
                if n >= 5 and resp[0] == slave and resp[1] == func:
                    print(f"\n  *** VALID RESPONSE FOUND ***")
                    print(f"  Baud={baud}, Slave={hex(slave)}, Func={hex(func)}")

                    # Try to parse register values
                    data = resp[3:3 + resp[2]]

import serial
import time

# Change COM5 to the port not used by Proteus (e.g., if Proteus uses COM4, use COM5 here)
port = 'COM5'
baud = 9600

try:
    ser = serial.Serial(port, baud, timeout=1)
    print(f"Listening on {port} at {baud} baud...")
    time.sleep(2)  # Wait for serial connection to stabilize

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print("Received:", line)
except serial.SerialException as e:
    print("Serial error:", e)
except KeyboardInterrupt:
    print("Exiting.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()

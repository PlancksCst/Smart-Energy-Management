import serial
import time

# Mapping: circuit_id -> priority (1 = highest, 5 = lowest)
circuit_priorities = {
    1: 2,
    2: 1,
    3: 4,
    4: 3
}

# Current threshold in mA (e.g., 10000 mA = 10 A)
CURRENT_THRESHOLD = 10000

# Track state of circuits (True = ON, False = OFF)
circuit_states = {1: True, 2: True, 3: True, 4: True}

# Initialize serial connection to Arduino
ser = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)
print("Connected to Arduino")

def parse_line(line):
    try:
        parts = line.strip().decode().split(',')
        data = {}
        for part in parts:
            k, v = part.split('=')
            data[k.strip()] = float(v)
        return data
    except Exception as e:
        print("Parsing error:", e)
        return None

def turn_off_circuit(circuit_id):
    if circuit_states[circuit_id]:
        cmd = f"OFF{circuit_id}\n"
        ser.write(cmd.encode())
        print(f"Sent command to turn OFF circuit {circuit_id}")
        circuit_states[circuit_id] = False
        

def turn_on_all_circuits():
    for cid in circuit_states:
        if not circuit_states[cid]:
            cmd = f"ON{cid}\n"
            ser.write(cmd.encode())
            circuit_states[cid] = True

while True:
    try:
        line = ser.readline()
        if not line:
            continue

        print("Received:", line.strip().decode())

        data = parse_line(line)
        if not data:
            continue

        circuit_id = int(data["ID"])
        current = data["I"]

        # Store latest current per circuit
        circuit_states[circuit_id] = True  # Mark as active if sending data
        total_current = 0

        # Recalculate total current only from active circuits
        current_values = {circuit_id: current}
        for cid in range(1, 5):
            if cid != circuit_id and circuit_states[cid]:
                current_values[cid] = 0  # You can improve this by caching values

        total_current = sum(current_values.values())
        print(f"Total current: {total_current:.2f} mA")

        # If threshold exceeded, turn off lowest-priority circuits first
        if total_current > CURRENT_THRESHOLD:
            print(" Overcurrent detected. Shutting down low-priority circuits.")
            for cid, priority in sorted(circuit_priorities.items(), key=lambda x: -x[1]):
                if circuit_states[cid]:
                    turn_off_circuit(cid)
                    break  # Turn off one at a time

        # Optional: Auto-recover after load drops
        elif total_current < CURRENT_THRESHOLD * 0.8:
            turn_on_all_circuits()

        time.sleep(0.5)

    except KeyboardInterrupt:
        print("Exiting...")
        break

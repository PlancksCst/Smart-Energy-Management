from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
import sqlite3
from fastapi import HTTPException
from datetime import datetime, timedelta



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    init_db()
    yield
    # Code to run on shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)  

# controller.py
class CircuitController:
    @staticmethod
    def get_circuit_status(circuit_id: int):
        conn = sqlite3.connect("energy.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.priority, c.max_consumption_Wh, sr.current, sr.voltage
            FROM circuits c
            LEFT JOIN (
                SELECT circuit_id, current, voltage
                FROM sensor_readings
                WHERE circuit_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ) sr ON c.id = sr.circuit_id
            WHERE c.id = ?
        """, (circuit_id, circuit_id))

        result = cursor.fetchone()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Circuit not found")

        priority, max_consumption, current, voltage = result
        current_consumption = current * voltage if current and voltage else 0

        return {
            "priority": priority,
            "current_consumption": current_consumption,
            "max_consumption": max_consumption,
            "recommendation": CircuitController.get_priority_action(
                priority, current_consumption, max_consumption
            )
        }


def add_new_circuit(circuit_id, name, priority, is_critical, running_ratio, temperature, avg_cons, max_cons, timestamp=None):
    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO circuits (
            id, name, priority, is_critical,
            average_continuous_running_hours_ratio, temperature,
            average_consumption_Wh, max_consumption_Wh, peak_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (circuit_id, name, priority, is_critical, running_ratio, temperature, avg_cons, max_cons, timestamp))
    conn.commit()
    circuit_id = cursor.lastrowid
    conn.close()
    return circuit_id

# this is to be removed it only used for testing, replaced by ltspice input
def add_sensor_reading(circuit_id, voltage, current, temperature, timestamp):
    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensor_readings (
            circuit_id, voltage, current, temperature, timestamp
        ) VALUES (?, ?, ?, ?, ?)
    """, (circuit_id, voltage, current, temperature, timestamp))
    
    cursor.execute("SELECT * FROM circuits ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    print("Inserted circuit:", row)
    
    conn.commit()
    conn.close()

import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()

    # Drop table if exists (optional, to start fresh)
    cursor.execute("DROP TABLE IF EXISTS circuits")

    # Create table with AUTOINCREMENT on id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS circuits (
            id INTEGER PRIMARY KEY ,
            name TEXT NOT NULL,
            priority INTEGER CHECK (priority BETWEEN 0 AND 5),
            is_critical BOOLEAN DEFAULT False,
            average_continuous_running_hours_ratio REAL DEFAULT 0,
            temperature REAL DEFAULT 25,
            average_consumption_Wh REAL,
            max_consumption_Wh REAL,
            peak_time TEXT DEFAULT 'None'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id INTEGER NOT NULL,
            voltage REAL,
            current REAL,
            temperature REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (circuit_id) REFERENCES circuits(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id INTEGER NOT NULL,
            voltage REAL,
            current REAL,
            temperature REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (circuit_id) REFERENCES circuits(id)
        );
    """)
    
    # Sample data WITHOUT id column (SQLite will assign ids automatically)

    appliances_df = pd.DataFrame([
        ["Refrigerator", 3, True, 0.95, 28.0, 150.0, 300.0, "all day"],
        ["HVAC (Heating)", 5, True, 0.8, 42.0, 2500.0, 3500.0, "all day"],
        ["Washing Machine", 4, False, 0.25, 33.0, 800.0, 1500.0, "morning"],
        ["LED Lights", 1, False, 0.6, 27.0, 10.0, 20.0, "evening"],
        ["Microwave", 2, False, 0.05, 35.0, 600.0, 1200.0, "night"],
        ["Dishwasher", 4, False, 0.15, 38.0, 1000.0, 2400.0, "morning"],
        ["Television", 2, False, 0.4, 31.0, 50.0, 200.0, "evening"],
        ["Laptop Charger", 1, False, 0.3, 29.0, 30.0, 90.0, "morning"],
        ["Electric Kettle", 3, False, 0.1, 45.0, 750.0, 1500.0, "night"],
        ["Hair Dryer", 2, False, 0.05, 47.0, 900.0, 1800.0, "night"]
    ], columns=[
        "name", "priority", "is_critical", 
        "average_continuous_running_hours_ratio", "temperature",
        "average_consumption_Wh", "max_consumption_Wh",
        "peak_time"
    ])

    insert_query = """
        INSERT INTO circuits (
            name, priority, is_critical,
            average_continuous_running_hours_ratio, temperature,
            average_consumption_Wh, max_consumption_Wh,
            peak_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """


    data_to_insert = appliances_df.to_records(index=False).tolist()

    cursor.executemany(insert_query, data_to_insert)
    conn.commit()
    conn.close()

# Call init_db() to create table and insert data
init_db()




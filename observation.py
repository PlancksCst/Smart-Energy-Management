import sqlite3
import pandas as pd
from rule_based_classifier import RuleBasedPriorityClassifier
from main import add_new_circuit
from datetime import datetime, timedelta

def process_circuit_observation(circuit_id: int):
    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()

    # Step 1: Check if already classified
    cursor.execute("SELECT id FROM circuits WHERE id = ?", (circuit_id,))
    if cursor.fetchone():
        print(f"Circuit ID {circuit_id} is already classified.")
        conn.close()
        return

    # Step 2: Calculate running ratio
    time_threshold = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        SELECT COUNT(*) FROM sensor_readings
        WHERE circuit_id = ? AND current > 0.1 AND timestamp >= ?
    """, (circuit_id, time_threshold))
    active_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM sensor_readings
        WHERE circuit_id = ? AND timestamp >= ?
    """, (circuit_id, time_threshold))
    total_count = cursor.fetchone()[0]

    running_ratio = active_count / total_count if total_count > 0 else 0
    
    if running_ratio>0.8:
        is_critical_flag = True
    else:
        is_critical_flag = False

    # Step 3: Fetch average parameters
    cursor.execute("""
        SELECT AVG(voltage), AVG(current), AVG(temperature), MAX(voltage * current)
        FROM sensor_readings
        WHERE circuit_id = ?
    """, (circuit_id,))
    v_avg, c_avg, t_avg , c_max = cursor.fetchone()
    avg_power = (v_avg or 0) * (c_avg or 0)
    max_power = c_max

    # # Step 4: Get circuit name from observation queue
    # cursor.execute("""
    #     SELECT temp_name, is_critical FROM observation_queue
    #     WHERE id = ? AND status = 'observing'
    # """, (circuit_id,))
    # row = cursor.fetchone()
    # if not row:
    #     print(f"Circuit ID {circuit_id} not found in observation queue or already processed.")
    #     conn.close()
    #     return

    # name, is_critical_flag = row

    
    # Step 5: Classify
    model = RuleBasedPriorityClassifier()

    features = pd.DataFrame([{
        "is_critical": is_critical_flag,
        "average_power": avg_power,
        "max_power": c_max,
        "running_ratio": running_ratio,
        "average_temp": t_avg or 25
    }])

    pred_priority = model.predict(features)[0]


    name='default_circuit'  # Placeholder for circuit name, can be replaced with actual logic
    
    

    # Step 7: Determine peak time
    if running_ratio > 0.8:
        peak_time = "all day"
        is_critical = True
    elif running_ratio < 0.02:
        peak_time = "no time"
        is_critical = False
    else:
        cursor.execute("""
            SELECT
                CASE
                    WHEN strftime('%H', timestamp) BETWEEN '05' AND '11' THEN 'morning'
                    WHEN strftime('%H', timestamp) BETWEEN '12' AND '16' THEN 'noon'
                    WHEN strftime('%H', timestamp) BETWEEN '17' AND '20' THEN 'evening'
                    ELSE 'night'
                END AS time_bucket,
                AVG(voltage * current) as avg_power
            FROM sensor_readings
            WHERE circuit_id = ?
            GROUP BY time_bucket
        """, (circuit_id,))
        results = cursor.fetchall()
        peak_time = max(results, key=lambda x: x[1])[0] if results else "no time"
        is_critical = False

    print("Inserting new circuit into database:")
    print(f"  Name: {name}")
    print(f"  circuit ID: {circuit_id}")
    print(f"  Priority: {pred_priority}")
    print(f"  Is Critical: {is_critical}")
    print(f"  Running Ratio: {running_ratio}")
    print(f"  Temperature: {t_avg}")
    print(f"  Avg Consumption: {avg_power}")
    print(f"  Max Consumption: {max_power}")
    print(f"  Peak Time: {peak_time}")
    
    cursor.execute("""
        UPDATE circuits SET peak_time = ?, is_critical = ?
        WHERE id = ?
    """, (peak_time, is_critical, circuit_id))
    conn.commit()
    conn.close()
    # # Step 8: Update observation status
    # cursor.execute("""
    #     UPDATE observation_queue SET status = 'classified'
    #     WHERE id = ?
    # """, (circuit_id,))
    
    # Step 6: Insert into circuits table
    add_new_circuit(circuit_id, name, pred_priority, is_critical_flag, running_ratio, t_avg or 25, avg_power, max_power,peak_time)
    
    
    print(f"Circuit {name} processed and classified with priority {pred_priority}, peak: {peak_time}")

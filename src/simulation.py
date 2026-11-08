import sqlite3
import json
from datetime import datetime

DB_PATH = "database/yottaflex.db"


def simulate_pump_flow(pump_id="PUMP-001", flow_multiplier=1.2):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get pump details
    cursor.execute(
        "SELECT facility_id, nominal_flow FROM pump WHERE pump_id = ?",
        (pump_id,)
    )

    pump = cursor.fetchone()

    if pump is None:
        print("Pump not found!")
        conn.close()
        return

    facility_id, nominal_flow = pump

    # Calculate simulated flow
    predicted_flow = nominal_flow * flow_multiplier

    # Check connected valve
    cursor.execute("""
        SELECT v.valve_id, v.valve_state
        FROM pipe p
        JOIN valve v ON p.target_node_id = v.valve_id
        WHERE p.source_node_id = ?
        LIMIT 1
    """, (pump_id,))

    valve = cursor.fetchone()

    if valve:
        valve_id, valve_state = valve
    else:
        valve_id = None
        valve_state = "UNKNOWN"

    if valve_state == "CLOSED":
        effective_flow = 0
        result = "FLOW_BLOCKED_BY_CLOSED_VALVE"
    else:
        effective_flow = predicted_flow
        result = "NORMAL_SIMULATED_FLOW"

    # Prepare simulation details
    simulation_data = {
        "input": {
            "pump_id": pump_id,
            "flow_multiplier": flow_multiplier,
            "nominal_flow": nominal_flow,
            "valve_id": valve_id,
            "valve_state": valve_state
        },
        "output": {
            "predicted_flow": round(predicted_flow, 2),
            "effective_flow": round(effective_flow, 2),
            "result": result
        }
    }

    # Generate simulation ID
    cursor.execute("""
        SELECT COUNT(*) FROM simulation_run
        WHERE simulation_id LIKE 'SIM-2026-%'
    """)

    count = cursor.fetchone()[0] + 1
    simulation_id = f"SIM-2026-{count:06d}"

    # Save simulation record
    cursor.execute("""
        INSERT INTO simulation_run
        (simulation_id, facility_id, configuration, run_status, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        simulation_id,
        facility_id,
        json.dumps(simulation_data),
        "COMPLETED",
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    print("Simulation completed successfully!")
    print("Simulation ID:", simulation_id)
    print("Pump ID:", pump_id)
    print("Nominal Flow:", nominal_flow)
    print("Predicted Flow:", round(predicted_flow, 2))
    print("Valve State:", valve_state)
    print("Effective Flow:", round(effective_flow, 2))
    print("Result:", result)


if __name__ == "__main__":
    simulate_pump_flow("PUMP-001", 1.2)
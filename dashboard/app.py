
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "yottaflex.db"

st.set_page_config(
    page_title="YottaFlex Industrial Monitoring",
    page_icon="🏭",
    layout="wide"
)


def load_data(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)


st.title("🏭 YottaFlex Industrial Monitoring")
st.caption("Industrial equipment, telemetry and anomaly monitoring")

if not DB_PATH.exists():
    st.error("Database file not found!")
    st.stop()

# KPI metrics
metrics = {
    "Facilities": "SELECT COUNT(*) FROM facility",
    "Pumps": "SELECT COUNT(*) FROM pump",
    "Tanks": "SELECT COUNT(*) FROM tank",
    "Valves": "SELECT COUNT(*) FROM valve",
    "Sensors": "SELECT COUNT(*) FROM sensor",
    "Telemetry Readings": "SELECT COUNT(*) FROM telemetry",
    "Alarms": "SELECT COUNT(*) FROM alarm",
    "Simulations": "SELECT COUNT(*) FROM simulation_run"
}

values = {}
for name, query in metrics.items():
    values[name] = load_data(query).iloc[0, 0]

cols = st.columns(4)
for col, name in zip(cols, list(metrics.keys())[:4]):
    col.metric(name, f"{values[name]:,}")

cols = st.columns(4)
for col, name in zip(cols, list(metrics.keys())[4:]):
    col.metric(name, f"{values[name]:,}")

st.divider()

# Telemetry chart
st.subheader("📊 Telemetry Overview")

telemetry = load_data("""
    SELECT t.reading_time, s.sensor_type,
           AVG(t.reading_value) AS average_reading
    FROM telemetry t
    JOIN sensor s ON t.sensor_id = s.sensor_id
    GROUP BY t.reading_time, s.sensor_type
    ORDER BY t.reading_time
""")

if not telemetry.empty:
    fig = px.line(
        telemetry,
        x="reading_time",
        y="average_reading",
        color="sensor_type",
        title="Average Sensor Readings Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No telemetry data available.")

st.divider()

# Alarm summary
st.subheader("🚨 Alarm Summary")

alarms = load_data("""
    SELECT issue_type, COUNT(*) AS total
    FROM alarm
    GROUP BY issue_type
    ORDER BY total DESC
""")

if not alarms.empty:
    fig = px.bar(
        alarms,
        x="issue_type",
        y="total",
        title="Detected Alarms by Type"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(alarms, use_container_width=True)
else:
    st.info("No alarms detected.")

st.divider()

# Latest alarm records
st.subheader("Latest Alarm Records")

latest_alarms = load_data("""
    SELECT alarm_id, facility_id, issue_type,
           severity, ground_truth, created_at
    FROM alarm
    ORDER BY created_at DESC
    LIMIT 10
""")

st.dataframe(latest_alarms, use_container_width=True)

st.divider()

# Simulation records
st.subheader("⚙️ Simulation History")

simulations = load_data("""
    SELECT simulation_id, facility_id,
           run_status, configuration, created_at
    FROM simulation_run
    ORDER BY created_at DESC
""")

st.dataframe(simulations, use_container_width=True)

st.caption("YottaFlex Industrial Monitoring | Powered by Python, SQLite and Streamlit")

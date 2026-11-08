# YottaFlex Industrial Monitoring System

## Project Overview

This project is a Python-based industrial monitoring system for monitoring water facility equipment, sensor readings, operational conditions, and anomaly indicators.

It models facilities, pumps, tanks, valves, pipes, sensors, telemetry, alarms, operating modes, and simulation runs. It also includes ground-truth labels for testing anomaly detection.

## Technology Stack

- Python
- SQLite
- Pandas
- NumPy
- Streamlit
- Plotly

## Project Dataset

The current dataset contains:

| Entity | Records |
|---|---:|
| Facilities | 3 |
| Pumps | 20 |
| Tanks | 30 |
| Valves | 60 |
| Pipe segments | 40 |
| Sensors | 130 |
| Telemetry readings | 100,000 |
| Alarms | 4 |
| Operating modes | 6 |
| Simulation runs | 1 |
| Ground-truth records | 4 |

Random data generation uses seed `20261022`.

## Main Features

1. Master data generation for industrial equipment.
2. Pump-to-valve-to-tank topology generation.
3. Sensor and telemetry data generation.
4. Anomaly injection and rule-based anomaly detection.
5. Operating mode management.
6. Basic pump-flow simulation.
7. Ground-truth creation and telemetry linking.
8. Database and CSV/JSON exports.
9. Data validation and checksum verification.
10. Streamlit dashboard for monitoring records and alarms.

## Detected Anomaly Scenarios

- LEAK_INDICATION
- PRESSURE_ANOMALY
- PUMP_DEGRADATION
- SENSOR_FAULT

These are rule-based indicators and test scenarios, not proof of real-world equipment failures.

## Project Structure

```text
YottaFlex_Industrial_Monitoring/
│
├── database/
│   └── yottaflex.db
│
├── dashboard/
│   └── app.py
│
├── src/
│   ├── database.py
│   ├── masterdata.py
│   ├── topology.py
│   ├── sensors_telemetry.py
│   ├── operating_modes.py
│   ├── inject_anomalies.py
│   ├── anomaly_detection.py
│   ├── simulation.py
│   ├── link_simulation_mode.py
│   ├── ground_truth.py
│   ├── link_ground_truth.py
│   ├── validate_ground_truth.py
│   ├── compare_results.py
│   ├── validation.py
│   ├── export_data.py
│   ├── verify_exports.py
│   └── reproducibility_check.py
│
├── exports/
│   ├── csv/
│   ├── json/
│   ├── source_manifest.json
│   ├── checksum_manifest.json
│   ├── ground_truth.csv
│   └── ground_truth.json
│
├── README.md
└── requirements.txt
```

## Installation

Create and activate a Python virtual environment:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install pandas numpy streamlit plotly
```

## Execution Order

Run the following commands from the project root directory on a fresh database:

```bash
python -m src.database
python -m src.masterdata
python -m src.topology
python -m src.sensors_telemetry
python -m src.operating_modes
python -m src.inject_anomalies
python -m src.anomaly_detection
python -m src.simulation
python -m src.link_simulation_mode
python -m src.ground_truth
python -m src.link_ground_truth
python -m src.validate_ground_truth
python -m src.compare_results
python -m src.validation
python -m src.export_data
python -m src.verify_exports
python -m src.reproducibility_check
```

**Important:** Some generation scripts overwrite or reset existing records. Run the generation sequence on a fresh database; do not rerun it on the completed project database without taking a backup.

## Dashboard

Start the dashboard using:

```bash
python -m streamlit run dashboard/app.py
```

The dashboard displays database metrics, telemetry trends, alarm summaries, and simulation history.

## Validation Results

The current project validation confirmed:

- Facility, pump, tank, valve, pipe, sensor, and telemetry record counts.
- Foreign-key integrity.
- Pipe endpoint validation.
- Sensor equipment validation.
- Tank capacity validation.
- Telemetry relationship validation.
- Ground-truth validation: 4 out of 4 passed.
- Expected versus detected anomaly counts: all four categories passed.
- Export verification: all 11 CSV files matched database record counts.
- Checksum verification: all 11 CSV files matched the saved baseline on a second check.

## Assumptions and Limitations

- The topology currently contains 40 pipe segments connecting 20 pump-to-valve-to-tank paths. Not all 60 valves are represented in the topology.
- Pipe endpoint references are validated by application logic rather than database foreign keys.
- Leak indication is based on a sudden tank-level decrease and does not establish a confirmed physical leak.
- The pump simulation is a simplified flow calculation, not a hydraulic network solver.
- The current checksum test verifies that exported files remain unchanged between checks. It does not prove that a complete fresh data-generation run produces identical output.
- Alarm-to-ground-truth comparison currently checks anomaly category counts, not exact alarm-to-equipment matches.
- Some generation and detection scripts overwrite existing data instead of maintaining a complete immutable event history.

## AI Assistance

AI assistance was used for learning, code generation, debugging, and documentation. The implementation and validation outputs were reviewed during development.

Prompt history and a description of AI-assisted work should be included in a separate project document.

## Conclusion

This project demonstrates a basic industrial monitoring workflow using Python, SQLite, sensor telemetry, rule-based anomaly detection, simulation, validation, data exports, and a Streamlit dashboard.
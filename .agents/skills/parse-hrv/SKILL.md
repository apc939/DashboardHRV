---
name: parse-hrv
description: >-
  Use this skill to parse one or more Kubios HRV CSV reports (using the format DDMMYYYY.csv)
  for a patient and update their historical data and the active dashboard.
---

# Parse HRV CSV reports

This skill runs a Python script to parse HRV CSV files from Kubios HRV and compile them into a unified JSON/JS format for the clinical dashboard.

## Steps

1. Run the parser script on a single CSV file or a folder of CSV files:
   * To process a single session:
     `python3 scripts/parse_hrv.py <path_to_csv>`
     *(e.g., `python3 scripts/parse_hrv.py Pacientes/AndresParraCharris_HRV/31082026.csv`)*
   * To process all sessions in a patient folder:
     `python3 scripts/parse_hrv.py <path_to_patient_folder>`
     *(e.g., `python3 scripts/parse_hrv.py Pacientes/AndresParraCharris_HRV/`)*

2. Verify that the file `data.json` and `data.js` are updated inside the patient folder (e.g. `Pacientes/<Paciente>_HRV/data.json`) and a copy is placed in the root directory.

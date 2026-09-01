---
name: parse-hrv
description: >-
  Use this skill to parse Kubios HRV CSV reports (DDMMYYYY.csv), audit clinical conclusions (_conclusiones.txt),
  and synchronize morning subjective/readiness questionnaires from Google Forms/Sheets (--sync, --set-url, or local CSV)
  to update patient historical data and the active dashboard.
---

# Parse HRV & Synchronize Patient Data

This skill runs Python scripts to parse HRV CSV files from Kubios HRV, process clinical audit conclusions, and synchronize subjective morning readiness reports from Google Forms/Sheets into unified JSON/JS for the clinical dashboard.

## Workflows

### 1. Process Kubios HRV Reports & Conclusiones
* **All sessions in patient folder**:
  `python3 scripts/parse_hrv.py Pacientes/<CarpetaPaciente>/`
* **Single session CSV**:
  `python3 scripts/parse_hrv.py Pacientes/<CarpetaPaciente>/DDMMYYYY.csv`
* **Single session conclusion file**:
  `python3 scripts/parse_hrv.py Pacientes/<CarpetaPaciente>/DDMMYYYY_conclusiones.txt`
* **Single session subjective file**:
  `python3 scripts/parse_hrv.py Pacientes/<CarpetaPaciente>/DDMMYYYY_subjetivo.txt`

### 2. Synchronize Google Forms / Sheets (Subjective & Readiness)
* **One-time Setup - Save Google Sheets URL for a patient**:
  `python3 scripts/import_google_forms.py --set-url "<GOOGLE_SHEETS_URL>" Pacientes/<CarpetaPaciente>/`
* **Automated Sync from Google Sheets (Daily routine)**:
  `python3 scripts/import_google_forms.py --sync Pacientes/<CarpetaPaciente>/`
* **Manual Local CSV Import**:
  `python3 scripts/import_google_forms.py <path_to_forms_csv> Pacientes/<CarpetaPaciente>/`

## Verification
Verify that `data.json` and `data.js` inside `Pacientes/<CarpetaPaciente>/` and in `data_dinamica/` are updated.

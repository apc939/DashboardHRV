#!/usr/bin/env python3
import os
import sys
import json
import re
from datetime import datetime

def parse_csv_file(filepath):
    filename = os.path.basename(filepath)
    # Validar formato de nombre DDMMYYYY.csv
    date_match = re.match(r"^(\d{2})(\d{2})(\d{4})\.csv$", filename)
    if not date_match:
        raise ValueError(f"El archivo {filename} debe tener el formato DDMMYYYY.csv (ej. 31082026.csv)")
    
    day, month, year = date_match.groups()
    session_date = f"{day}/{month}"
    full_date = f"{day}/{month}/{year}"
    
    # Determinar el nombre del paciente a partir de la carpeta contenedora
    parent_path = os.path.dirname(os.path.abspath(filepath))
    parent_dir = os.path.basename(parent_path)
    patient_name = parent_dir.replace("_HRV", "")
    # Añadir espacios antes de las mayúsculas (CamelCase a espacios)
    patient_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', patient_name).strip()
    
    # Mapeo de métricas requeridas
    metric_keys = {
        "PNS index:": "pns",
        "SNS index:": "sns",
        "Mean HR (beats/min):": "hr",
        "RMSSD (ms):": "rmssd",
        "LF/HF ratio:": "lfhf",
        "SD1 (ms):": "sd1",
        "SD2 (ms):": "sd2",
        "VLF (%):": "vlf",
        "LF (%):": "lf",
        "HF (%):": "hf",
        "SDNN (ms):": "sdnn",
        "Stress index:": "stress"
    }
    
    parsed_values = {key: None for key in metric_keys.values()}
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_str = line.strip()
            for key, json_key in metric_keys.items():
                if line_str.startswith(key):
                    # Dividir la línea por comas
                    parts = [p.strip() for p in line_str.split(",")]
                    # Los valores de las 6 fases están en los índices 1, 3, 5, 7, 9, 11
                    vals = []
                    for idx in [1, 3, 5, 7, 9, 11]:
                        if idx < len(parts) and parts[idx] != "":
                            val_str = parts[idx]
                            if val_str.lower() == "nan":
                                vals.append(None)
                            else:
                                try:
                                    val = float(val_str)
                                    if json_key in ["pns", "sns", "lfhf", "stress"]:
                                        val = round(val, 2)
                                    else:
                                        val = round(val, 1)
                                    vals.append(val)
                                except ValueError:
                                    vals.append(None)
                        else:
                            vals.append(None)
                    parsed_values[json_key] = vals
                    
    # Validar que se hayan parseado todas las métricas requeridas
    missing_metrics = [k for k, v in parsed_values.items() if v is None]
    if missing_metrics:
        raise ValueError(f"No se pudieron encontrar todas las métricas en {filename}. Faltantes: {missing_metrics}")
        
    session_data = {
        "date": session_date,
        "full_date": full_date,
        "hr": parsed_values["hr"],
        "rmssd": parsed_values["rmssd"],
        "pns": parsed_values["pns"],
        "sns": parsed_values["sns"],
        "vlf": parsed_values["vlf"],
        "lf": parsed_values["lf"],
        "hf": parsed_values["hf"],
        "lfhf": parsed_values["lfhf"],
        "sd1": parsed_values["sd1"],
        "sd2": parsed_values["sd2"],
        "sdnn": parsed_values["sdnn"],
        "stress": parsed_values["stress"]
    }
    
    return patient_name, parent_path, session_data

def calculate_suggested_conclusions(session):
    pns_basal = session["rmssd"][0]
    pns_peak = session["rmssd"][2]
    hf_peak = session["hf"][2]
    
    # PNS
    pns_text = (
        f"Marcada amplificación parasimpática durante la respiración pautada "
        f"(RMSSD de {pns_basal:.1f} a {pns_peak:.1f} ms y HF relativo de {hf_peak:.1f}%). "
        f"Confirma un acoplamiento cardiorrespiratorio normal y alta capacidad de modulación vagal."
    )
    
    # SNS
    hr_diff = session["hr"][3] - session["hr"][0]
    hr_diff_text = f"+{hr_diff:.1f}" if hr_diff >= 0 else f"{hr_diff:.1f}"
    sns_peak = session["sns"][4]
    sns_peak_text = f"+{sns_peak:.2f}" if sns_peak >= 0 else f"{sns_peak:.2f}"
    hr_peak = session["hr"][4]
    sns_text = (
        f"Respuesta barorrefleja intacta sin taquicardia postural patológica ({hr_diff_text} lpm). "
        f"Adecuada activación simpática durante las 30 sentadillas "
        f"(SNS index {sns_peak_text}, FC pico {hr_peak:.1f} lpm) con repliegue vagal transitorio."
    )
    
    # REC
    rec_rmssd = session["rmssd"][5]
    basal_rmssd = session["rmssd"][0]
    lfhf_rec = session["lfhf"][5]
    comparison = "superando" if rec_rmssd > basal_rmssd else "aproximándose a"
    rec_text = (
        f"Excelente reactivación vagal post-esfuerzo: el RMSSD recupera a {rec_rmssd:.1f} ms "
        f"{comparison} el valor basal ({basal_rmssd:.1f} ms) y el balance LF/HF se restablece a "
        f"{lfhf_rec:.2f} en los 6 minutos posteriores al ejercicio."
    )
    
    return pns_text, sns_text, rec_text

def read_conclusions_from_file(filepath):
    default_conclusions = {
        "pns": "No se ha realizado el análisis",
        "sns": "No se ha realizado el análisis",
        "rec": "No se ha realizado el análisis"
    }
    if not os.path.exists(filepath):
        return False, default_conclusions
        
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Comprobar si el archivo está marcado como revisado/aprobado por el médico
        reviewed_match = re.search(r"REVISADO:\s*(SI|SÍ|YES|TRUE|OK|APROBADO)", content, re.IGNORECASE)
        is_reviewed = bool(reviewed_match)
        
        if not is_reviewed:
            return False, default_conclusions
            
        conclusions = {}
        # Parse based on prefixes (soporta múltiples líneas y diferentes delimitadores)
        pns_match = re.search(r"Reserva Vagal:\s*(.*?)(?=(?:\n\s*(?:Tolerancia|Recuperacion|Recuperación):|\n\s*===|\n\s*---|\Z))", content, re.IGNORECASE | re.DOTALL)
        sns_match = re.search(r"Tolerancia:\s*(.*?)(?=(?:\n\s*(?:Reserva Vagal|Recuperacion|Recuperación):|\n\s*===|\n\s*---|\Z))", content, re.IGNORECASE | re.DOTALL)
        rec_match = re.search(r"(?:Recuperacion|Recuperación):\s*(.*?)(?=(?:\n\s*(?:Reserva Vagal|Tolerancia):|\n\s*===|\n\s*---|\Z))", content, re.IGNORECASE | re.DOTALL)
        
        conclusions["pns"] = pns_match.group(1).strip() if pns_match and pns_match.group(1).strip() else "No se ha realizado el análisis"
        conclusions["sns"] = sns_match.group(1).strip() if sns_match and sns_match.group(1).strip() else "No se ha realizado el análisis"
        conclusions["rec"] = rec_match.group(1).strip() if rec_match and rec_match.group(1).strip() else "No se ha realizado el análisis"
        
        return True, conclusions
    except Exception as e:
        print(f"Error al leer el archivo de conclusiones {filepath}: {e}")
        return False, default_conclusions

def save_patient_data(patient_name, parent_path, new_sessions, is_full_scan=False):
    patient_json_path = os.path.join(parent_path, "data.json")
    
    if is_full_scan:
        # Reconstrucción completa: el directorio actual es la fuente de la verdad
        sessions_by_date = {s["full_date"]: s for s in new_sessions}
    else:
        # Modo incremental: preservar historial existente y agregar/actualizar la nueva sesión
        existing_data = {"patient_name": patient_name, "sessions": []}
        if os.path.exists(patient_json_path):
            try:
                with open(patient_json_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception as e:
                print(f"Advertencia: No se pudo leer el archivo data.json existente: {e}. Creando uno nuevo.")
                
        # Mapear sesiones existentes por su fecha completa para evitar duplicados
        sessions_by_date = {s["full_date"]: s for s in existing_data["sessions"]}
        
        # Añadir o actualizar con las nuevas sesiones
        for session in new_sessions:
            sessions_by_date[session["full_date"]] = session
        
    # Ordenar las sesiones cronológicamente por fecha
    sorted_sessions = list(sessions_by_date.values())
    try:
        sorted_sessions.sort(key=lambda s: datetime.strptime(s["full_date"], "%d/%m/%Y"))
    except Exception as e:
        print(f"Advertencia al ordenar las sesiones cronológicamente: {e}")
        
    # Actualizar numeración consecutiva de las sesiones y procesar conclusiones .txt
    for idx, s in enumerate(sorted_sessions):
        s["session"] = idx + 1
        
        # Flujo de conclusiones .txt
        date_str = s["full_date"].replace("/", "")
        conclusiones_filename = f"{date_str}_conclusiones.txt"
        conclusiones_path = os.path.join(parent_path, conclusiones_filename)
        
        sug_pns, sug_sns, sug_rec = calculate_suggested_conclusions(s)
        
        if not os.path.exists(conclusiones_path):
            try:
                hr_ds = s['hr'][0]
                rmssd_ds = s['rmssd'][0]
                pns_ds = s['pns'][0]
                sns_ds = s['sns'][0]

                rmssd_rc12 = s['rmssd'][2]
                hf_rc12 = s['hf'][2]
                pns_rc12 = s['pns'][2]

                hr_ort = s['hr'][3]
                delta_hr_ort = hr_ort - hr_ds
                lfhf_ort = s['lfhf'][3]

                hr_ruff = s['hr'][4]
                sns_ruff = s['sns'][4]

                rmssd_rec = s['rmssd'][5]
                lfhf_rec = s['lfhf'][5]
                pns_rec = s['pns'][5]

                txt_content = (
                    "REVISADO: NO\n"
                    "======================================================================\n"
                    "📊 VALORES FISIOLÓGICOS DE LA SESIÓN (Referencia de apoyo)\n"
                    "======================================================================\n"
                    f"• FC Basal (DS): {hr_ds:.1f} lpm  |  RMSSD Basal: {rmssd_ds:.1f} ms  |  PNS: {pns_ds:+.2f}  |  SNS: {sns_ds:+.2f}\n"
                    f"• Pico Vagal (RC12): RMSSD {rmssd_rc12:.1f} ms  |  HF: {hf_rc12:.1f}%  |  PNS: {pns_rc12:+.2f}\n"
                    f"• Reto Ortostático (ORT): FC +{delta_hr_ort:.1f} lpm ({hr_ort:.1f} lpm)  |  LF/HF: {lfhf_ort:.2f}\n"
                    f"• Pico Simpático (RUFF): FC pico {hr_ruff:.1f} lpm  |  SNS index: {sns_ruff:+.2f}\n"
                    f"• Recuperación (REC): RMSSD {rmssd_rec:.1f} ms  |  LF/HF: {lfhf_rec:.2f}  |  PNS: {pns_rec:+.2f}\n"
                    "======================================================================\n"
                    "✍️ CONCLUSIONES CLÍNICAS (Edita el texto abajo según tu criterio):\n"
                    "======================================================================\n\n"
                    f"Reserva Vagal: {sug_pns}\n\n"
                    f"Tolerancia: {sug_sns}\n\n"
                    f"Recuperacion: {sug_rec}\n"
                )

                with open(conclusiones_path, "w", encoding="utf-8") as f:
                    f.write(txt_content)
                print(f"Creada plantilla de conclusiones sugeridas en: {conclusiones_path} (Estado: REVISADO: NO)")
            except Exception as e:
                print(f"Error al escribir la plantilla de conclusiones: {e}")
                
            s["reviewed"] = False
            s["conclusions"] = {
                "pns": "No se ha realizado el análisis",
                "sns": "No se ha realizado el análisis",
                "rec": "No se ha realizado el análisis"
            }
        else:
            is_reviewed, conclusions = read_conclusions_from_file(conclusiones_path)
            s["reviewed"] = is_reviewed
            s["conclusions"] = conclusions
            
    updated_data = {
        "patient_name": patient_name,
        "sessions": sorted_sessions
    }
    
    # Guardar en la carpeta del paciente (JSON y JS)
    with open(patient_json_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)
    
    patient_js_path = os.path.join(parent_path, "data.js")
    with open(patient_js_path, "w", encoding="utf-8") as f:
        f.write(f"const patientData = {json.dumps(updated_data, indent=4, ensure_ascii=False)};\n")
        
    print(f"Historial guardado exitosamente en: {parent_path} (JSON y JS, {len(sorted_sessions)} sesiones totales)")
    
    # Guardar copia activa en la subcarpeta data_dinamica/ del proyecto (leída por dashboard.html)
    root_dir = os.path.dirname(os.path.dirname(parent_path))
    data_dir = os.path.join(root_dir, "data_dinamica")
    os.makedirs(data_dir, exist_ok=True)
    
    root_json_path = os.path.join(data_dir, "data.json")
    root_js_path = os.path.join(data_dir, "data.js")
    root_active_txt = os.path.join(data_dir, "activo.txt")
    
    # Escribir archivos genéricos activos
    with open(root_json_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)
    with open(root_js_path, "w", encoding="utf-8") as f:
        f.write(f"const patientData = {json.dumps(updated_data, indent=4, ensure_ascii=False)};\n")
        
    # Escribir archivo de texto identificador
    with open(root_active_txt, "w", encoding="utf-8") as f:
        f.write(f"Paciente: {patient_name}\n")
        
    print(f"Copia activa creada en: {data_dir}")
    print(f"  -> Archivos de datos: data.json y data.js")
    print(f"  -> Identificador activo: activo.txt (Paciente: {patient_name})")

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  Procesar un archivo CSV o TXT: python parse_hrv.py Pacientes/<CarpetaPaciente>/DDMMYYYY.csv (o _conclusiones.txt)")
        print("  Procesar todos los archivos de un paciente: python parse_hrv.py Pacientes/<CarpetaPaciente>/")
        sys.exit(1)
        
    path_arg = sys.argv[1]
    
    if not os.path.exists(path_arg):
        print(f"Error: La ruta especificada no existe: {path_arg}")
        sys.exit(1)
        
    # Si el usuario pasó el archivo de conclusiones .txt, derivar su CSV correspondiente
    if path_arg.endswith("_conclusiones.txt"):
        csv_candidate = path_arg.replace("_conclusiones.txt", ".csv")
        if not os.path.exists(csv_candidate):
            print(f"Error: No se encontró el archivo CSV correspondiente ({csv_candidate}) para el archivo de conclusiones.")
            sys.exit(1)
        path_arg = csv_candidate
        
    new_sessions = []
    patient_name = None
    parent_path = None
    
    is_dir = os.path.isdir(path_arg)
    if is_dir:
        # Es un directorio, procesar todos los archivos CSV válidos dentro
        csv_files = []
        for f in os.listdir(path_arg):
            if f.endswith(".csv") and re.match(r"^\d{8}\.csv$", f):
                csv_files.append(os.path.join(path_arg, f))
                
        if not csv_files:
            print(f"No se encontraron archivos CSV con formato DDMMYYYY.csv en el directorio: {path_arg}")
            sys.exit(1)
            
        # Limpiar posibles archivos _conclusiones.txt huérfanos cuyos CSV ya no existan en el directorio
        valid_csv_stems = {os.path.basename(f).replace(".csv", "") for f in csv_files}
        for f in os.listdir(path_arg):
            if f.endswith("_conclusiones.txt"):
                stem = f.replace("_conclusiones.txt", "")
                if stem not in valid_csv_stems and re.match(r"^\d{8}$", stem):
                    try:
                        os.remove(os.path.join(path_arg, f))
                        print(f"Eliminado archivo de conclusiones huérfano: {f}")
                    except Exception:
                        pass
            
        print(f"Procesando {len(csv_files)} archivos CSV en el directorio {path_arg}...")
        for filepath in csv_files:
            try:
                p_name, p_path, session = parse_csv_file(filepath)
                new_sessions.append(session)
                patient_name = p_name
                parent_path = p_path
            except Exception as e:
                print(f"Error al procesar el archivo {filepath}: {e}")
    else:
        # Es un solo archivo
        try:
            p_name, p_path, session = parse_csv_file(path_arg)
            new_sessions.append(session)
            patient_name = p_name
            parent_path = p_path
        except Exception as e:
            print(f"Error al procesar el archivo {path_arg}: {e}")
            sys.exit(1)
            
    if new_sessions and patient_name and parent_path:
        save_patient_data(patient_name, parent_path, new_sessions, is_full_scan=is_dir)
    else:
        print("No se procesaron sesiones válidas.")
        sys.exit(1)

if __name__ == "__main__":
    main()

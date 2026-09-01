#!/usr/bin/env python3
import os
import sys
import csv
import re
from datetime import datetime

def find_column(headers, patterns):
    for p in patterns:
        for idx, h in enumerate(headers):
            clean_h = h.strip().lower()
            if re.search(p, clean_h, re.IGNORECASE):
                return idx
    return None

def detect_date_format(date_samples):
    month_first_evidence = 0
    day_first_evidence = 0
    
    for val in date_samples:
        if not val:
            continue
        val = val.strip().split(" ")[0]
        if re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$", val):
            return "YEAR_FIRST"
            
        m = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})$", val)
        if m:
            p1, p2, p3 = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if p1 > 12 and p2 <= 12:
                day_first_evidence += 1
            elif p2 > 12 and p1 <= 12:
                month_first_evidence += 1
                
    if month_first_evidence > 0 and day_first_evidence == 0:
        return "MONTH_FIRST"
    if day_first_evidence > 0 and month_first_evidence == 0:
        return "DAY_FIRST"
    return "DEFAULT"

def parse_date_str(val, date_pref="DEFAULT"):
    if not val:
        return None
    val = val.strip().split(" ")[0] # Remover posible hora
    
    if date_pref == "MONTH_FIRST":
        formats = ["%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"]
    elif date_pref == "YEAR_FIRST":
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y"]
    else:
        formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%y", "%d-%m-%y", "%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"]
        
    for fmt in formats:
        try:
            dt = datetime.strptime(val, fmt)
            return dt.strftime("%d%m%Y"), dt.strftime("%d/%m/%Y")
        except ValueError:
            continue
    return None

def get_patient_root_dir(path):
    abs_path = os.path.abspath(path)
    cur = os.path.dirname(abs_path) if os.path.isfile(abs_path) else abs_path
    if os.path.basename(cur) in ["reportes_kubios", "notas_clinicas", "config"]:
        return os.path.dirname(cur)
    if os.path.basename(cur).endswith("_HRV"):
        return cur
    check = cur
    while check and check != os.path.dirname(check):
        if os.path.basename(check).endswith("_HRV"):
            return check
        if os.path.basename(os.path.dirname(check)) == "Pacientes":
            return check
        if os.path.exists(os.path.join(check, "reportes_kubios")) or os.path.exists(os.path.join(check, "notas_clinicas")) or os.path.exists(os.path.join(check, "data.json")):
            return check
        check = os.path.dirname(check)
    return cur

def get_clinical_file_paths(patient_root, date_str):
    notas_dir = os.path.join(patient_root, "notas_clinicas")
    c_sub = os.path.join(notas_dir, f"{date_str}_conclusiones.txt")
    c_root = os.path.join(patient_root, f"{date_str}_conclusiones.txt")
    concl_path = c_sub if os.path.exists(c_sub) else (c_root if os.path.exists(c_root) else c_sub)

    s_sub = os.path.join(notas_dir, f"{date_str}_subjetivo.txt")
    s_root = os.path.join(patient_root, f"{date_str}_subjetivo.txt")
    subj_path = s_sub if os.path.exists(s_sub) else (s_root if os.path.exists(s_root) else s_sub)
    return concl_path, subj_path

def get_csv_content(source, patient_dir=None):
    # Si es una opción --sync
    if source == "--sync":
        if not patient_dir or not os.path.isdir(patient_dir):
            print("Error: Debes especificar el directorio del paciente para usar --sync.")
            sys.exit(1)
        patient_root = get_patient_root_dir(patient_dir)
        url_file = os.path.join(patient_root, "forms_url.txt")
        if not os.path.exists(url_file):
            print(f"Error: No se encontró archivo forms_url.txt en {patient_root}.")
            print("Puedes configurar la URL con: python3 scripts/import_google_forms.py --set-url <URL_GOOGLE_SHEETS> " + patient_root)
            sys.exit(1)
        with open(url_file, "r", encoding="utf-8") as f:
            source = f.read().strip()

    # Si es una URL (web / Google Sheets)
    if source.startswith("http://") or source.startswith("https://"):
        url = source
        # Convertir URL estándar de Google Sheets a export CSV directo
        # Ej: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0 -> .../export?format=csv
        sheet_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
        if sheet_match:
            sheet_id = sheet_match.group(1)
            # Extraer gid si existe
            gid_match = re.search(r"gid=([0-9]+)", url)
            gid_str = f"&gid={gid_match.group(1)}" if gid_match else ""
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv{gid_str}"
            
        print(f"Descargando respuestas desde Google Sheets: {url}...")
        try:
            import urllib.request
            import ssl
            
            try:
                import certifi
                ctx = ssl.create_default_context(cafile=certifi.where())
            except Exception:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                content = response.read().decode('utf-8-sig', errors='ignore')
                return content.splitlines()
        except Exception as e:
            print(f"Error al descargar la hoja de cálculo desde Google Sheets: {e}")
            print("Asegúrate de que la hoja de Google Sheets esté compartida como 'Cualquier persona con el enlace puede ver' o publicada en la web.")
            sys.exit(1)
            
    # Si es un archivo local
    if not os.path.exists(source):
        print(f"Error: No existe el archivo CSV especificado: {source}")
        sys.exit(1)
        
    with open(source, "r", encoding="utf-8-sig", errors="ignore") as f:
        return f.readlines()

def import_forms_csv(source, patient_dir):
    patient_root = get_patient_root_dir(patient_dir)
    if not os.path.isdir(patient_root):
        print(f"Error: No existe el directorio del paciente: {patient_root}")
        sys.exit(1)
        
    lines = get_csv_content(source, patient_root)
    if not lines:
        print("Error: El contenido CSV está vacío.")
        sys.exit(1)
        
    reader = csv.reader(lines)
    headers = next(reader, None)
    if not headers:
        print("Error: No se encontraron encabezados en el archivo CSV.")
        sys.exit(1)
        
    # Detectar índices de columnas en orden estricto de prioridad
    idx_date = find_column(headers, [r"fecha.*toma", r"fecha.*sesi[óo]n", r"fecha.*registro", r"fecha.*hrv", r"^fecha", r"date", r"marca temporal", r"timestamp"])
    idx_sleep_hours = find_column(headers, [r"horas.*sue[ñn]o", r"hours.*sleep", r"tiempo.*dormido"])
    idx_sleep_quality = find_column(headers, [r"calidad.*sue[ñn]o", r"calidad.*descanso", r"sleep.*quality"])
    idx_mood = find_column(headers, [r"[áa]nimo", r"mood", r"humor", r"energ[íi]a"])
    idx_pain_scale = find_column(headers, [r"escala.*dolor", r"nivel.*dolor", r"^dolor", r"pain"])
    idx_pain_detail = find_column(headers, [r"detalle.*dolor", r"zona.*dolor", r"ubicaci[óo]n.*dolor", r"tipo.*dolor"])
    idx_readiness = find_column(headers, [r"readiness", r"disposici[óo]n", r"preparaci[óo]n", r"recuperado.*entrenar"])
    idx_exercise = find_column(headers, [r"ejercicio.*previo", r"entrenamiento.*previo", r"actividad.*previa", r"ejercicio.*ayer"])
    idx_caffeine = find_column(headers, [r"cafe[íi]na", r"caf[ée]", r"caffeine"])
    idx_alcohol = find_column(headers, [r"alcohol", r"cerveza", r"vino", r"licor"])
    idx_symptoms = find_column(headers, [r"s[íi]ntomas", r"sensaciones", r"observaciones", r"notas", r"comentarios"])

    if idx_date is None:
        print("Error: El archivo no parece ser una encuesta válida. No se encontró ninguna columna de fecha.")
        sys.exit(1)

    rows = list(reader)
    date_samples = [row[idx_date] for row in rows if len(row) > idx_date]
    date_pref = detect_date_format(date_samples)

    imported_count = 0
    for row_idx, row in enumerate(rows, start=2):
        if not row or len(row) <= idx_date:
            continue
            
        date_raw = row[idx_date]
        parsed_d = parse_date_str(date_raw, date_pref)
        if not parsed_d:
            print(f"Fila {row_idx}: No se pudo interpretar la fecha '{date_raw}'. Omitiendo...")
            continue
            
        file_date, full_date = parsed_d
        _, subjetivo_filepath = get_clinical_file_paths(patient_root, file_date)
        os.makedirs(os.path.dirname(subjetivo_filepath), exist_ok=True)
        subjetivo_filename = os.path.basename(subjetivo_filepath)
        
        def get_val(idx, default=""):
            if idx is not None and idx < len(row) and row[idx].strip():
                return row[idx].strip()
            return default

        v_sleep_h = get_val(idx_sleep_hours)
        v_sleep_q = get_val(idx_sleep_quality)
        v_mood = get_val(idx_mood)
        v_pain_s = get_val(idx_pain_scale, "0")
        v_pain_d = get_val(idx_pain_detail, "Ninguno")
        v_readiness = get_val(idx_readiness)
        v_exercise = get_val(idx_exercise, "Ninguno")
        v_caffeine = get_val(idx_caffeine, "Ninguna")
        v_alcohol = get_val(idx_alcohol, "No")
        v_symptoms = get_val(idx_symptoms, "Ninguno")

        content = (
            "COMPLETADO: SI\n"
            "======================================================================\n"
            f"📋 DATOS SUBJETIVOS Y ESTADO MATUTINO ({full_date})\n"
            "======================================================================\n"
            f"• Horas de sueno: {v_sleep_h}\n"
            f"• Calidad del sueno (1-5): {v_sleep_q}\n"
            f"• Estado de animo (1-5): {v_mood}\n"
            f"• Nivel de dolor (0-10): {v_pain_s}\n"
            f"• Detalle de dolor: {v_pain_d}\n"
            f"• Percepcion de readiness (1-10): {v_readiness}\n"
            f"• Ejercicio previo: {v_exercise}\n"
            f"• Cafeina dia previo: {v_caffeine}\n"
            f"• Alcohol dia previo: {v_alcohol}\n"
            f"• Sintomas o sensaciones: {v_symptoms}\n"
            "======================================================================\n"
        )

        with open(subjetivo_filepath, "w", encoding="utf-8") as out_f:
            out_f.write(content)
        print(f"✓ Generado/Actualizado: {subjetivo_filename}")
        imported_count += 1

    print(f"\nImportación finalizada con éxito ({imported_count} registros subjetivos importados).")
    
    # Sincronizar automáticamente el dashboard del paciente
    print("\nSincronizando base de datos y dashboard del paciente...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parse_script = os.path.join(script_dir, "parse_hrv.py")
    os.system(f"python3 {parse_script} {patient_root}")

def main():
    if len(sys.argv) < 3:
        print("Uso:")
        print("  1. Importar archivo local:")
        print("     python3 scripts/import_google_forms.py <archivo.csv> Pacientes/<CarpetaPaciente>/")
        print("  2. Importar directo desde URL de Google Sheets:")
        print("     python3 scripts/import_google_forms.py '<URL_GOOGLE_SHEETS>' Pacientes/<CarpetaPaciente>/")
        print("  3. Configurar URL permanente para un paciente:")
        print("     python3 scripts/import_google_forms.py --set-url '<URL_GOOGLE_SHEETS>' Pacientes/<CarpetaPaciente>/")
        print("  4. Sincronización automática de paciente configurado:")
        print("     python3 scripts/import_google_forms.py --sync Pacientes/<CarpetaPaciente>/")
        sys.exit(1)
        
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    
    if arg1 == "--set-url":
        if len(sys.argv) < 4:
            print("Uso: python3 scripts/import_google_forms.py --set-url '<URL_GOOGLE_SHEETS>' Pacientes/<CarpetaPaciente>/")
            sys.exit(1)
        sheet_url = sys.argv[2]
        patient_dir = sys.argv[3]
        patient_root = get_patient_root_dir(patient_dir)
        if not os.path.isdir(patient_root):
            print(f"Error: No existe el directorio: {patient_root}")
            sys.exit(1)
        url_file = os.path.join(patient_root, "forms_url.txt")
        with open(url_file, "w", encoding="utf-8") as f:
            f.write(sheet_url.strip())
        print(f"✓ URL de Google Sheets guardada exitosamente en {url_file}")
        print(f"Ahora puedes sincronizar este paciente en cualquier momento con:")
        print(f"  python3 scripts/import_google_forms.py --sync {patient_root}")
        sys.exit(0)
        
    source_arg = arg1
    patient_dir_arg = arg2
    import_forms_csv(source_arg, patient_dir_arg)

if __name__ == "__main__":
    main()

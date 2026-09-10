#!/usr/bin/env python3
import os
import sys
import shutil
import tempfile
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from parse_hrv import read_subjective_from_file, parse_csv_file, save_patient_data, calculate_suggested_conclusions

class TestSubjectiveIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.patient_dir = os.path.join(self.test_dir, "JuanPerez_HRV")
        os.makedirs(self.patient_dir, exist_ok=True)
        
        self.sample_csv_path = os.path.join(self.patient_dir, "31082026.csv")
        sample_csv_content = (
            "PNS index:,-0.54,,-0.63,,1.23,,-0.56,,-2.16,,-0.02,\n"
            "SNS index:,-0.54,,-0.63,,-0.65,,-0.10,,3.13,,-0.21,\n"
            "Mean HR (beats/min):,60.4,,61.0,,61.7,,67.0,,91.8,,65.4,\n"
            "RMSSD (ms):,39.1,,75.2,,94.6,,30.2,,13.8,,42.3,\n"
            "LF/HF ratio:,20.98,,0.08,,0.10,,14.88,,19.33,,1.86,\n"
            "SD1 (ms):,27.7,,53.7,,67.4,,21.4,,9.8,,30.0,\n"
            "SD2 (ms):,78.5,,83.2,,87.1,,70.8,,43.2,,61.1,\n"
            "VLF (%):,0.6,,1.0,,1.4,,6.0,,35.2,,3.3,\n"
            "LF (%):,94.9,,7.0,,9.1,,88.1,,61.6,,62.9,\n"
            "HF (%):,4.5,,92.0,,89.6,,5.9,,3.2,,33.8,\n"
            "SDNN (ms):,58.8,,70.1,,77.3,,52.4,,31.2,,48.1,\n"
            "Stress index:,7.47,,7.69,,7.63,,7.40,,17.52,,8.13,\n"
            "VLF (ms^2):,18.3,,56.3,,92.3,,52.0,,519.4,,92.8,\n"
            "LF (ms^2):,3120.1,,378.2,,616.6,,768.2,,907.8,,1750.7,\n"
            "HF (ms^2):,148.7,,5002.0,,6088.2,,51.6,,47.0,,940.0,\n"
            "LF (n.u.):,95.4,,7.0,,9.2,,93.7,,95.1,,65.1,\n"
            "HF (n.u.):,4.5,,93.0,,90.8,,6.3,,4.9,,34.9,\n"
            "Total power (ms^2):,3287.1,,5436.8,,6798.6,,871.8,,1474.2,,2783.6,\n"
        )
        with open(self.sample_csv_path, "w", encoding="utf-8") as f:
            f.write(sample_csv_content)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_auto_generate_template_when_missing(self):
        p_name, p_path, session = parse_csv_file(self.sample_csv_path)
        save_patient_data(p_name, p_path, [session], is_full_scan=True)
        
        subjetivo_file = os.path.join(self.patient_dir, "notas_clinicas", "31082026_subjetivo.txt")
        self.assertTrue(os.path.exists(subjetivo_file), "Debe autogenerarse el archivo DDMMYYYY_subjetivo.txt en notas_clinicas/")
        
        with open(subjetivo_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("COMPLETADO: NO", content)
        self.assertIn("Horas de sueno:", content)
        self.assertIn("Percepcion de readiness (1-10):", content)
        
        json_path = os.path.join(self.patient_dir, "data.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["sessions"]), 1)
        sub = data["sessions"][0]["subjective"]
        self.assertFalse(sub["completed"])
        self.assertIsNone(sub["sleep_hours"])
        self.assertIsNone(sub["readiness"])

    def test_parse_completed_subjective_file(self):
        notas_dir = os.path.join(self.patient_dir, "notas_clinicas")
        os.makedirs(notas_dir, exist_ok=True)
        subjetivo_file = os.path.join(notas_dir, "31082026_subjetivo.txt")
        custom_content = (
            "COMPLETADO: SI\n"
            "======================================================================\n"
            "📋 DATOS SUBJETIVOS Y ESTADO MATUTINO (31/08/2026)\n"
            "======================================================================\n"
            "• Horas de sueño: 7.5\n"
            "• Calidad del sueño (1-5): 4\n"
            "• Estado de ánimo (1-5): 5\n"
            "• Nivel de dolor (0-10): 2\n"
            "• Detalle de dolor: Molestia leve en rodilla izquierda\n"
            "• Percepción de readiness (1-10): 8\n"
            "• Ejercicio previo: Fuerza tren inferior 50 min RPE 8\n"
            "• Cafeína día previo: 2 espressos por la mañana\n"
            "• Alcohol día previo: No\n"
            "• Síntomas o sensaciones: Ninguno relevante\n"
            "======================================================================\n"
        )
        with open(subjetivo_file, "w", encoding="utf-8") as f:
            f.write(custom_content)
            
        p_name, p_path, session = parse_csv_file(self.sample_csv_path)
        save_patient_data(p_name, p_path, [session], is_full_scan=True)
        
        json_path = os.path.join(self.patient_dir, "data.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sub = data["sessions"][0]["subjective"]
        
        self.assertTrue(sub["completed"])
        self.assertEqual(sub["sleep_hours"], 7.5)
        self.assertEqual(sub["sleep_quality"], 4)
        self.assertEqual(sub["mood"], 5)
        self.assertEqual(sub["pain_scale"], 2)
        self.assertEqual(sub["pain_detail"], "Molestia leve en rodilla izquierda")
        self.assertEqual(sub["readiness"], 8)
        self.assertEqual(sub["previous_exercise"], "Fuerza tren inferior 50 min RPE 8")
        self.assertEqual(sub["caffeine"], "2 espressos por la mañana")
        self.assertEqual(sub["alcohol"], "No")
        self.assertEqual(sub["symptoms"], "Ninguno relevante")

    def test_direct_subjective_argument_in_cli(self):
        notas_dir = os.path.join(self.patient_dir, "notas_clinicas")
        os.makedirs(notas_dir, exist_ok=True)
        subjetivo_file = os.path.join(notas_dir, "31082026_subjetivo.txt")
        with open(subjetivo_file, "w", encoding="utf-8") as f:
            f.write("COMPLETADO: SI\n• Horas de sueño: 8\n• Percepción de readiness (1-10): 9\n")
            
        script_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "parse_hrv.py"))
        ret = os.system(f'python3 "{script_p}" "{subjetivo_file}" > /dev/null 2>&1')
        self.assertEqual(ret, 0, "El script debe procesar el archivo _subjetivo.txt derivando su CSV")

    def test_google_forms_importer(self):
        csv_forms_path = os.path.join(self.test_dir, "forms_responses.csv")
        with open(csv_forms_path, "w", encoding="utf-8") as f:
            f.write(
                "Marca temporal,Fecha de toma,Horas de sueño,Calidad descanso (1-5),Estado de ánimo (1-5),Nivel de dolor (0-10),Detalle dolor,Readiness (1-10),Ejercicio previo,Consumo cafeína,Consumo alcohol,Notas o síntomas\n"
                "01/09/2026 08:30:00,31/08/2026,7.2,4,4,0,Ninguno,8,Fuerza torso 45min,1 taza matutina,No,Sensación de buen descanso\n"
            )
        script_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "import_google_forms.py"))
        ret = os.system(f'python3 "{script_p}" "{csv_forms_path}" "{self.patient_dir}" > /dev/null 2>&1')
        self.assertEqual(ret, 0)
        
        subjetivo_file = os.path.join(self.patient_dir, "notas_clinicas", "31082026_subjetivo.txt")
        self.assertTrue(os.path.exists(subjetivo_file))
        
        json_path = os.path.join(self.patient_dir, "data.json")
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sub = data["sessions"][0]["subjective"]
        self.assertTrue(sub["completed"])
        self.assertEqual(sub["sleep_hours"], 7.2)
        self.assertEqual(sub["sleep_quality"], 4)
        self.assertEqual(sub["readiness"], 8)

    def test_google_forms_importer_us_date_format(self):
        csv_forms_path = os.path.join(self.test_dir, "forms_responses_us.csv")
        with open(csv_forms_path, "w", encoding="utf-8") as f:
            f.write(
                "Timestamp,Fecha de la toma de HRV,Horas de sueño,Calidad del sueño (Sensación de descanso),Estado de ánimo y energía,Nivel de dolor corporal,Detalle o zona del dolor,Readiness / Disposición para entrenar hoy,Ejercicio realizado día previo,Consumo de cafeína día previo,Consumo de alcohol día previo,Otros síntomas o sensaciones\n"
                "9/1/2026 13:10:01,8/31/2026,7,3,4,0,Ninguno,9,Descanso,1 taza matutina,No,Ninguno\n"
            )
        script_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "import_google_forms.py"))
        ret = os.system(f'python3 "{script_p}" "{csv_forms_path}" "{self.patient_dir}" > /dev/null 2>&1')
        self.assertEqual(ret, 0)
        
        subjetivo_file = os.path.join(self.patient_dir, "notas_clinicas", "31082026_subjetivo.txt")
        self.assertTrue(os.path.exists(subjetivo_file))
        
        json_path = os.path.join(self.patient_dir, "data.json")
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sub = data["sessions"][0]["subjective"]
        self.assertTrue(sub["completed"])
        self.assertEqual(sub["sleep_hours"], 7.0)
        self.assertEqual(sub["sleep_quality"], 3)
        self.assertEqual(sub["readiness"], 9)
        self.assertEqual(sub["previous_exercise"], "Descanso")

    def test_set_url_configuration(self):
        fake_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        script_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "import_google_forms.py"))
        ret = os.system(f'python3 "{script_p}" --set-url "{fake_url}" "{self.patient_dir}" > /dev/null 2>&1')
        self.assertEqual(ret, 0)
        
        url_file = os.path.join(self.patient_dir, "forms_url.txt")
        self.assertTrue(os.path.exists(url_file))
        with open(url_file, "r", encoding="utf-8") as f:
            saved_url = f.read().strip()
        self.assertEqual(saved_url, fake_url)

    def test_subfolder_organization_and_parsing(self):
        # Crear subcarpetas funcionales
        kubios_dir = os.path.join(self.patient_dir, "reportes_kubios")
        notas_dir = os.path.join(self.patient_dir, "notas_clinicas")
        os.makedirs(kubios_dir, exist_ok=True)
        os.makedirs(notas_dir, exist_ok=True)
        
        # Mover CSV a reportes_kubios/
        csv_in_sub = os.path.join(kubios_dir, "31082026.csv")
        shutil.move(self.sample_csv_path, csv_in_sub)
        
        # Crear notas en notas_clinicas/
        concl_file = os.path.join(notas_dir, "31082026_conclusiones.txt")
        with open(concl_file, "w", encoding="utf-8") as f:
            f.write("REVISADO: SI\nReserva Vagal: Excelente\nTolerancia: Normal\nRecuperacion: Optima\n")
            
        subj_file = os.path.join(notas_dir, "31082026_subjetivo.txt")
        with open(subj_file, "w", encoding="utf-8") as f:
            f.write("COMPLETADO: SI\n• Horas de sueño: 8.5\n• Percepción de readiness (1-10): 10\n")
            
        # 1. Proceso de carpeta completa del paciente
        script_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "parse_hrv.py"))
        ret = os.system(f'python3 "{script_p}" "{self.patient_dir}" > /dev/null 2>&1')
        self.assertEqual(ret, 0)
        
        json_path = os.path.join(self.patient_dir, "data.json")
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["patient_name"], "Juan Perez")
        self.assertEqual(len(data["sessions"]), 1)
        self.assertTrue(data["sessions"][0]["reviewed"])
        self.assertEqual(data["sessions"][0]["subjective"]["sleep_hours"], 8.5)
        self.assertEqual(data["sessions"][0]["subjective"]["readiness"], 10)
        
        # 2. Proceso de archivo CSV individual dentro de reportes_kubios/
        ret_ind = os.system(f'python3 "{script_p}" "{csv_in_sub}" > /dev/null 2>&1')
        self.assertEqual(ret_ind, 0)

    def test_suggested_conclusions_robust_recovery(self):
        session = {
            "hr": [60.0, 60.5, 61.0, 66.0, 92.0, 62.0],
            "rmssd": [40.0, 65.0, 85.0, 32.0, 15.0, 48.0],
            "pns": [0.20, 1.10, 1.65, -0.40, -2.10, 0.50],
            "sns": [-0.50, -0.60, -0.70, 0.10, 3.20, -0.15],
            "hf": [5.0, 80.0, 88.5, 20.0, 15.0, 40.0],
            "lfhf": [15.0, 0.12, 0.08, 4.0, 5.5, 1.2]
        }
        pns_text, sns_text, rec_text = calculate_suggested_conclusions(session)
        self.assertIn("Marcada amplificación parasimpática", pns_text)
        self.assertIn("RC12 (12 rpm)", pns_text)
        self.assertIn("Respuesta barorrefleja intacta", sns_text)
        self.assertIn("+6.0 lpm", sns_text)
        self.assertIn("Marcada activación simpática", sns_text)
        self.assertIn("Excelente reactivación vagal post-esfuerzo", rec_text)
        self.assertIn("superando el valor basal", rec_text)

    def test_suggested_conclusions_depressed_recovery_and_atypical_response(self):
        # Caso similar a la sesión 02092026: caída post-esfuerzo severa y ortostatismo negativo
        session = {
            "hr": [57.5, 56.0, 55.0, 54.4, 74.6, 68.0],
            "rmssd": [39.5, 42.0, 47.0, 35.0, 12.0, 8.6],
            "pns": [0.36, 0.80, 1.17, -0.10, -1.80, -2.35],
            "sns": [-0.81, -0.90, -0.85, -0.50, 0.87, 1.45],
            "hf": [10.0, 60.0, 73.5, 15.0, 10.0, 8.0],
            "lfhf": [2.5, 0.30, 0.25, 0.64, 2.10, 7.87]
        }
        pns_text, sns_text, rec_text = calculate_suggested_conclusions(session)
        self.assertIn("Modesta amplificación parasimpática", pns_text)
        self.assertIn("Respuesta ortostática atípica con desaceleración cronotrópica (-3.1 lpm)", sns_text)
        self.assertIn("Respuesta simpática amortiguada", sns_text)
        self.assertIn("Recuperación vagal post-esfuerzo incompleta/lenta", rec_text)
        self.assertIn("predominio simpático persistente", rec_text)
        self.assertNotIn("+-", sns_text)

    def test_suggested_conclusions_rc10_peak_and_high_orthostatic_tachycardia(self):
        session = {
            "hr": [65.0, 66.0, 67.0, 98.0, 110.0, 70.0],
            "rmssd": [30.0, 80.0, 45.0, 20.0, 10.0, 25.0],
            "pns": [0.0, 1.8, 0.6, -1.2, -2.5, -0.2],
            "sns": [0.1, -0.2, 0.0, 2.5, 4.2, 0.8],
            "hf": [8.0, 85.0, 50.0, 10.0, 5.0, 25.0],
            "lfhf": [5.0, 0.1, 1.5, 8.0, 12.0, 2.8]
        }
        pns_text, sns_text, rec_text = calculate_suggested_conclusions(session)
        self.assertIn("RC10 (10 rpm)", pns_text)
        self.assertIn("Marcada taquicardia ortostática postural (+33.0 lpm)", sns_text)
        self.assertIn("Reactivación vagal post-esfuerzo en curso", rec_text)

if __name__ == "__main__":
    unittest.main()

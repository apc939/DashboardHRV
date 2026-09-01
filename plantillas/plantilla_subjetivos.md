# Plantilla y Guía de Datos Subjetivos (HRV)

Este documento describe el estándar de captura de **métricas subjetivas matutinas y readiness**, la estructura del archivo `DDMMYYYY_subjetivo.txt` y cómo integrarlo en el flujo de trabajo del paciente.

---

## 📋 Estructura de `DDMMYYYY_subjetivo.txt`

Cada sesión de HRV cuenta con su correspondiente archivo de datos subjetivos con el siguiente formato:

```text
COMPLETADO: SI
======================================================================
📋 DATOS SUBJETIVOS Y ESTADO MATUTINO (31/08/2026)
======================================================================
• Horas de sueno: 7.5
• Calidad del sueno (1-5): 4
• Estado de animo (1-5): 4
• Nivel de dolor (0-10): 0
• Detalle de dolor: Ninguno
• Percepcion de readiness (1-10): 8
• Ejercicio previo: Fuerza tren superior 45 min RPE 7
• Cafeina dia previo: 1 taza por la mañana
• Alcohol dia previo: No
• Sintomas o sensaciones: Ninguno
======================================================================
```

---

## 🩺 Variables y Escalas Estandarizadas

| Variable | Campo en `.txt` | Tipo / Rango | Descripción Clínica |
| :--- | :--- | :--- | :--- |
| **Estado de Verificación** | `COMPLETADO:` | `SI` / `NO` | Si está en `NO`, el dashboard muestra aviso de reporte pendiente. |
| **Horas de Sueño** | `• Horas de sueno:` | Numérico (ej. `7.5`) | Duración total de sueño reportada por el paciente. |
| **Calidad de Sueño** | `• Calidad del sueno (1-5):` | Entero `1 - 5` | Sensación de descanso al despertar (1: Pésimo, 5: Excelente). |
| **Estado de Ánimo** | `• Estado de animo (1-5):` | Entero `1 - 5` | Tono afectivo y energía matutina (1: Muy bajo, 5: Excelente). |
| **Nivel de Dolor** | `• Nivel de dolor (0-10):` | Entero `0 - 10` | Escala analógica visual de dolor (0: Sin dolor, 10: Insuperable). |
| **Detalle de Dolor** | `• Detalle de dolor:` | Texto libre | Ubicación o tipo de molestia (ej. *Molestia en rodilla derecha*). |
| **Readiness para Entrenar**| `• Percepcion de readiness (1-10):`| Entero `1 - 10` | Disposición y preparación física para tolerar carga hoy. |
| **Ejercicio Previo** | `• Ejercicio previo:` | Texto libre | Tipo, duración e intensidad del entrenamiento del día anterior. |
| **Consumo de Cafeína** | `• Cafeina dia previo:` | Texto libre | Cantidad o momento de ingesta de cafeína del día previo. |
| **Consumo de Alcohol** | `• Alcohol dia previo:` | Texto libre | Ingesta de bebidas alcohólicas la noche/día anterior. |
| **Síntomas / Sensaciones** | `• Sintomas o sensaciones:` | Texto libre | Notas adicionales (ej. congestión, estrés, dolor de cabeza). |

---

## 🚀 Flujo con Google Forms

1. **Crear Google Form**: Configurar las 9 preguntas anteriores en tu formulario de seguimiento matutino.
2. **Descargar Respuestas**: Exportar el archivo `.csv` desde Google Sheets / Google Forms.
3. **Importación Automática**:
   ```bash
   python3 scripts/import_google_forms.py respuestas_forms.csv Pacientes/AndresParraCharris_HRV/
   ```
   *Esto generará automáticamente los archivos `DDMMYYYY_subjetivo.txt` correspondientes a cada fecha y sincronizará el dashboard.*

4. **Edición Manual**:
   También puedes editar directamente el archivo `DDMMYYYY_subjetivo.txt` en la carpeta del paciente y ejecutar:
   ```bash
   python3 scripts/parse_hrv.py Pacientes/AndresParraCharris_HRV/DDMMYYYY_subjetivo.txt
   ```

# Dashboard HRV - Reporte de Evaluación Autonómica Cardiovascular

Sistema clínico interactivo para la visualización, análisis y seguimiento longitudinal de la Variabilidad de la Frecuencia Cardíaca (HRV) basado en reportes cuantitativos de **Kubios HRV**.

---

## 📋 Descripción General

Este proyecto permite a profesionales de la salud y fisiólogos analizar la función del Sistema Nervioso Autónomo (SNA) a través de un protocolo estandarizado de 6 fases (20 minutos):

1. **DS (Decúbito Supino)**: Reposo basal (5 min).
2. **RC10 (Respiración Pautada a 10 rpm)**: Estimulación vagal (2.5 min).
3. **RC12 (Respiración Pautada a 12 rpm)**: Evaluación de reactividad parasimpática (2.5 min).
4. **ORT (Reto Ortostático)**: Bipedestación y respuesta barorrefleja (5 min).
5. **RUFF (Test de Ruffier - 30 sentadillas)**: Carga dinámica y activación simpática (1 min).
6. **REC (Recuperación en Supino)**: Cinética de reactivación vagal post-esfuerzo (4 min).

El sistema genera un **Dashboard HTML interactivo** que funciona completamente fuera de línea (sin necesidad de servidores web locales) y ofrece dos modos de visualización:
* **Evaluación de la Sesión**: KPIs basales, tablas cuantitativas de las 6 fases, 4 gráficos SVG de respuesta autonómica y conclusiones clínicas auditadas.
* **Línea Base Longitudinal**: Seguimiento temporal de sesiones con bandas de normalidad (*Smallest Worthwhile Change*, SWC: $\pm 0.5\text{ SD}$) y media móvil de 7 días cuando se acumulan 7 o más pruebas.

---

## 📂 Estructura del Proyecto

```text
DashboardHRV/
├── Pacientes/
│   └── <NombrePaciente>_HRV/
│       ├── DDMMYYYY.csv             # Reporte CSV exportado desde Kubios HRV
│       ├── DDMMYYYY.pdf             # Reporte PDF original (opcional)
│       ├── DDMMYYYY_conclusiones.txt# Archivo editable de conclusiones y auditoría
│       ├── data.json                # Historial acumulado del paciente en JSON
│       └── data.js                  # Historial en JavaScript (bypass de CORS)
├── data_dinamica/                   # Subcarpeta de datos temporales del paciente activo
│   ├── data.json                    # Copia activa temporal en JSON
│   ├── data.js                      # Copia activa temporal en JS (leída por dashboard.html)
│   └── activo.txt                   # Muestra el nombre del paciente activo actual
├── plantillas/                      # Plantillas y guías de redacción clínica
│   └── plantilla_conclusiones.md    # Guía narrativa y fórmulas de referencia
├── scripts/
│   └── parse_hrv.py                 # Parser inteligente en Python
├── dashboard.html                   # Interfaz clínica del Dashboard
├── README.md                        # Documentación para usuarios y médicos
├── .GEMINI.md                       # Documentación técnica para modelos de IA (oculto)
└── .agents/                         # Configuración del entorno de IA (oculto)
    └── skills/
        └── parse-hrv/
            └── SKILL.md             # Custom Skill para asistentes de IA
```

---

## 🚀 Flujo de Trabajo y Modo de Uso

### 1. Agregar Nuevos Reportes
Crea una carpeta para el paciente dentro de `Pacientes/` siguiendo la convención:
`Pacientes/<NombrePaciente>_HRV/` (ej. `Pacientes/AndresParraCharris_HRV/`).

Coloca allí los archivos CSV exportados de Kubios con el formato de fecha `DDMMYYYY.csv` (ej. `31082026.csv`).

### 2. Procesar Datos con el Parser
Puedes ejecutar el script de Python de 3 formas según lo que necesites:

* **Opción A: Sincronizar carpeta completa (Reconstrucción/Limpieza)**:
  ```bash
  python3 scripts/parse_hrv.py Pacientes/AndresParraCharris_HRV/
  ```
  *Escanea todos los CSV de la carpeta, elimina del historial las sesiones que hayas borrado y limpia archivos `.txt` huérfanos.*

* **Opción B: Procesar o agregar un solo reporte CSV**:
  ```bash
  python3 scripts/parse_hrv.py Pacientes/AndresParraCharris_HRV/31082026.csv
  ```

* **Opción C: Procesar directamente el archivo de conclusiones**:
  ```bash
  python3 scripts/parse_hrv.py Pacientes/AndresParraCharris_HRV/31082026_conclusiones.txt
  ```

---

## 🩺 Flujo de Auditoría y Validación Médica (`.txt`)

Para asegurar el rigor clínico, la herramienta **nunca publica conclusiones sin la validación del médico**:

1. **Generación de Plantilla con Valores de Referencia**:
   Al procesar un nuevo CSV, el script crea automáticamente un archivo `DDMMYYYY_conclusiones.txt` con un encabezado de consulta rápida de los valores fisiológicos calculados y la propuesta de conclusiones:
   ```text
   REVISADO: NO
   ======================================================================
   📊 VALORES FISIOLÓGICOS DE LA SESIÓN (Referencia de apoyo)
   ======================================================================
   • FC Basal (DS): 60.4 lpm  |  RMSSD Basal: 39.1 ms  |  PNS: +0.15
   • Pico Vagal (RC12): RMSSD 94.6 ms  |  HF: 89.6%  |  PNS: +1.76
   • Reto Ortostático (ORT): FC +6.6 lpm (67.0 lpm)  |  LF/HF: 3.01
   • Pico Simpático (RUFF): FC pico 91.8 lpm  |  SNS index: +3.13
   • Recuperación (REC): RMSSD 42.3 ms  |  LF/HF: 1.86  |  PNS: -0.02
   ======================================================================
   ✍️ CONCLUSIONES CLÍNICAS (Edita el texto abajo según tu criterio):
   ======================================================================

   Reserva Vagal: Marcada amplificación parasimpática...

   Tolerancia: Respuesta barorrefleja intacta...

   Recuperacion: Excelente reactivación vagal...
   ```
   *Mientras diga `REVISADO: NO`, el Dashboard mostrará la etiqueta ámbar `⏳ Pendiente de Revisión Médica` y el texto "No se ha realizado el análisis".*

2. **Aprobación y Edición**:
   * Abre el archivo `.txt`, realiza los ajustes diagnósticos que consideres necesarios (manteniendo arriba tu tabla de consulta de métricas) y cambia la primera línea a **`REVISADO: SI`**.
   * Vuelve a ejecutar el parser (`python3 scripts/parse_hrv.py Pacientes/<Carpeta>/`).
   * El Dashboard se actualizará mostrando la etiqueta verde **`✓ Conclusiones Validadas por Médico`** y tu texto clínico aprobado.

3. **¿Cómo restaurar la plantilla si borraste valores por error?**:
   * Si en algún momento modificaste el `.txt` y quieres volver a la plantilla original calculada desde el CSV, **simplemente elimina el archivo `.txt`** y ejecuta nuevamente el script:
     ```bash
     python3 scripts/parse_hrv.py Pacientes/<Carpeta>/
     ```
   * El script detectará la ausencia del archivo y generará una copia nueva e intacta con todos los valores calculados de la sesión.

---

## 🖥️ Visualización en el Navegador

Simplemente haz doble clic sobre el archivo **`dashboard.html`** desde el explorador de archivos (Finder) para abrirlo en cualquier navegador (Chrome, Safari, Firefox, Edge). 

> [!NOTE]
> No requiere conexión a internet ni levantar servidores web locales (`localhost`). La carga de datos utiliza `data_dinamica/data.js` para operar libre de restricciones de seguridad (CORS).

---

## 📅 Selector Interactivo de Sesión Histórica

En la parte superior derecha de la cabecera encontrarás el menú desplegable **`📅 Sesión: [ DD/MM/AAAA - Sesión #X ▾ ]`**:
* **Comportamiento por Defecto**: Carga automáticamente la última sesión adquirida del paciente.
* **Consulta Histórica sin pérdida de Línea Base**: Si deseas evaluar una sesión previa, selecciónala en el menú desplegable. La pestaña *"Evaluación de la Sesión"* refrescará de inmediato todos sus KPIs, gráficos dinámicos, tabla cuantitativa y conclusiones clínicas de ese día específico, **sin alterar ni borrar el historial completo de la pestaña Longitudinal**.
* **Impresión Personalizada**: Al exportar a PDF, el dossier se generará evaluando la sesión que tengas seleccionada en ese momento.

---

## 📥 Exportación del Dossier Clínico en PDF (4 Páginas A4)

El Dashboard cuenta con una función nativa de exportación que convierte la interfaz interactiva en un **Dossier Médico Imprimible de 4 páginas**, limpio y en fondo claro:

1. **Cómo generar el PDF**:
   * Haz clic en el botón **`[ 📥 Descargar PDF ]`** ubicado en la cabecera superior derecha (o usa el atajo `Cmd + P`).
   * En el diálogo de impresión de tu navegador, selecciona **Guardar como PDF**.

2. **Estructura Estandarizada del Documento (4 Páginas)**:
   * **📄 Página 1 — Evaluación de la Sesión**: Cabecera del paciente, 4 KPIs basales y 4 gráficos SVG de respuesta autonómica.
   * **📄 Página 2 — Métricas Cuantitativas & Síntesis Clínica**: Tabla completa de las 6 fases y las 3 conclusiones clínicas auditadas por el médico.
   * **📄 Página 3 — Línea Base Longitudinal (Reposo & Respiración)**: Gráficos de seguimiento de Fase 1 (DS), Fase 2 (RC10) y Fase 3 (RC12, centrada).
   * **📄 Página 4 — Línea Base Longitudinal (Reto & Recuperación)**: Gráficos de Fase 4 (ORT), Fase 5 (RUFF), Fase 6 (REC, centrada) y Nota metodológica sobre el rango SWC.

> [!TIP]
> **Recomendación de Impresión**: Asegúrate de tener seleccionado el tamaño de papel **A4** y la opción **Gráficos de fondo / Background graphics: Activado** en los ajustes de impresión de tu navegador para preservar los colores de las líneas y badges.

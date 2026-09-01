# Plantilla y Automatización: Formulario Google Forms (HRV)

Esta plantilla documenta la creación automática del formulario matutino de **Registro y Readiness HRV**, su estructura de preguntas y el método de sincronización directa con el Dashboard.

---

## 🚀 1. Creación Automática en 1 Clic (Google Apps Script)

Puedes generar el formulario completo y su hoja de cálculo vinculada ejecutando este script en [script.google.com](https://script.google.com):

```javascript
function crearFormularioHRV() {
  const form = FormApp.create('Registro Matutino y Readiness HRV');
  form.setDescription('Completa este breve cuestionario (45 segundos) inmediatamente después de finalizar tu registro matutino de HRV.');

  // 1. Fecha de la toma
  form.addDateItem()
    .setTitle('Fecha de la toma de HRV')
    .setHelpText('Fecha correspondiente a la prueba matutina de HRV.')
    .setRequired(true);

  // 2. Horas de sueño
  const valNum = FormApp.createTextValidation()
    .requireNumberGreaterThanOrEqualTo(0)
    .setHelpText('Ingresa un número válido mayor o igual a 0.')
    .build();

  form.addTextItem()
    .setTitle('Horas de sueño')
    .setHelpText('Ejemplo: 7.5 (utiliza punto para decimales)')
    .setValidation(valNum)
    .setRequired(true);

  // 3. Calidad del sueño
  form.addScaleItem()
    .setTitle('Calidad del sueño (Sensación de descanso)')
    .setBounds(1, 5)
    .setLabels('Pésimo / Muy fatigado', 'Excelente / Totalmente descansado')
    .setRequired(true);

  // 4. Estado de ánimo
  form.addScaleItem()
    .setTitle('Estado de ánimo y energía')
    .setBounds(1, 5)
    .setLabels('Muy bajo / Apático', 'Excelente / Alta motivación')
    .setRequired(true);

  // 5. Nivel de dolor
  form.addScaleItem()
    .setTitle('Nivel de dolor corporal')
    .setBounds(0, 10)
    .setLabels('Sin dolor', 'Dolor incapacitante')
    .setRequired(true);

  // 6. Detalle del dolor
  form.addTextItem()
    .setTitle('Detalle o zona del dolor')
    .setHelpText('Si no tienes dolor escribe "Ninguno". Si tienes, indica la zona (ej. rodilla derecha).')
    .setRequired(false);

  // 7. Readiness
  form.addScaleItem()
    .setTitle('Readiness / Disposición para entrenar hoy')
    .setBounds(1, 10)
    .setLabels('Agotado / Solo descanso', 'Al 100% para máxima intensidad')
    .setRequired(true);

  // 8. Ejercicio previo
  form.addTextItem()
    .setTitle('Ejercicio realizado día previo')
    .setHelpText('Tipo y duración (ej. Fuerza torso 45 min RPE 7, o Descanso).')
    .setRequired(true);

  // 9. Cafeína
  form.addMultipleChoiceItem()
    .setTitle('Consumo de cafeína día previo')
    .setChoiceValues(['Ninguno', '1 taza matutina', '2 a 3 tazas', '>3 tazas o consumo en la tarde/noche'])
    .setRequired(true);

  // 10. Alcohol
  form.addMultipleChoiceItem()
    .setTitle('Consumo de alcohol día previo')
    .setChoiceValues(['No', '1 copa / cerveza (Leve)', '2 a 3 copas (Moderado)', '>3 copas (Alto)'])
    .setRequired(true);

  // 11. Otros síntomas
  form.addParagraphTextItem()
    .setTitle('Otros síntomas o sensaciones')
    .setHelpText('Opcional: estrés laboral, congestión nasal, etc. Si nada aplica, dejar en blanco o "Ninguno".')
    .setRequired(false);

  // Crear hoja vinculada
  const fechaHoy = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const ss = SpreadsheetApp.create('Respuestas_HRV_Matutino_' + fechaHoy);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('🔗 Enlace para el Paciente: ' + form.getPublishedUrl());
  Logger.log('📊 Hoja de Cálculo: ' + ss.getUrl());
}
```

---

## ⚡ 2. Sincronización Directa y Automática (1 Comando)

Para no tener que descargar el archivo CSV manualmente cada vez:

1. **Configurar la URL de la hoja de Google Sheets una sola vez**:
   ```bash
   python3 scripts/import_google_forms.py --set-url "https://docs.google.com/spreadsheets/d/TU_ID_DE_HOJA/edit" Pacientes/AndresParraCharris_HRV/
   ```
   *(Asegúrate de que el acceso de la hoja de Google Sheets esté configurado como "Cualquier persona con el enlace puede ver").*

2. **Sincronizar automáticamente en cualquier momento**:
   ```bash
   python3 scripts/import_google_forms.py --sync Pacientes/AndresParraCharris_HRV/
   ```
   *El script descarga las respuestas más recientes de Google Sheets, genera/actualiza los archivos `DDMMYYYY_subjetivo.txt` y refresca el Dashboard al instante.*

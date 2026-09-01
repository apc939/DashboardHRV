# Plantilla y Guía de Conclusiones Clínicas (HRV)

Este documento contiene la **narrativa clínica de referencia** y la estructura de las tres conclusiones automáticas generadas por el sistema para cada sesión de Kubios HRV (protocolo de 6 fases).

Puedes consultar este archivo en cualquier momento si modificaste tu archivo `_conclusiones.txt` y deseas recuperar la estructura narrativa original.

---

## 📋 Estructura de la Plantilla

Cada archivo `DDMMYYYY_conclusiones.txt` utiliza el siguiente formato:

```text
REVISADO: SI
--------------------------------------------------
Reserva Vagal: [Texto de Conclusión 1]

Tolerancia: [Texto de Conclusión 2]

Recuperacion: [Texto de Conclusión 3]
```

---

## 🩺 Las 3 Conclusiones de Referencia

### 1. Reserva Vagal y Acoplamiento Respiratorio
* **Texto de Referencia**:
  > *"Marcada amplificación parasimpática durante la respiración pautada (RMSSD de **[RMSSD_Basal]** a **[RMSSD_Pico_RC12]** ms y HF relativo de **[HF_Pico_RC12]**%). Confirma un acoplamiento cardiorrespiratorio normal y alta capacidad de modulación vagal."*
* **Variables Fisiológicas**:
  * **RMSSD_Basal**: Fase 1 (DS) - Decúbito Supino (`rmssd[0]`).
  * **RMSSD_Pico_RC12**: Fase 3 (RC12) - Respiración pautada a 12 rpm (`rmssd[2]`).
  * **HF_Pico_RC12**: Fase 3 (RC12) - Potencia relativa en Alta Frecuencia (`hf[2]`).

---

### 2. Tolerancia Ortostática y Carga Dinámica
* **Texto de Referencia**:
  > *"Respuesta barorrefleja intacta sin taquicardia postural patológica (**[Dif_FC_Ortostática]** lpm). Adecuada activación simpática durante las 30 sentadillas (SNS index **[SNS_Pico_Ruffier]**, FC pico **[FC_Pico_Ruffier]** lpm) con repliegue vagal transitorio."*
* **Variables Fisiológicas**:
  * **Dif_FC_Ortostática**: Diferencia de Frecuencia Cardíaca entre Fase 4 (ORT) y Fase 1 (DS) (`hr[3] - hr[0]`).
  * **SNS_Pico_Ruffier**: Índice SNS durante el test de sentadillas en Fase 5 (RUFF) (`sns[4]`).
  * **FC_Pico_Ruffier**: Frecuencia Cardíaca máxima alcanzada en Fase 5 (RUFF) (`hr[4]`).

---

### 3. Cinética de Restauración Homeostática
* **Texto de Referencia**:
  > *"Excelente reactivación vagal post-esfuerzo: el RMSSD recupera a **[RMSSD_Recuperación]** ms **[superando / aproximándose a]** el valor basal (**[RMSSD_Basal]** ms) y el balance LF/HF se restablece a **[LFHF_Recuperación]** en los 6 minutos posteriores al ejercicio."*
* **Variables Fisiológicas**:
  * **RMSSD_Recuperación**: Fase 6 (REC) - Recuperación en supino (`rmssd[5]`).
  * **RMSSD_Basal**: Fase 1 (DS) - Decúbito Supino (`rmssd[0]`).
  * **Comparación**: Dice *"superando"* si `RMSSD_REC > RMSSD_Basal`, o *"aproximándose a"* en caso contrario.
  * **LFHF_Recuperación**: Ratio LF/HF en Fase 6 (REC) (`lfhf[5]`).

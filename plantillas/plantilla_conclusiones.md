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

## 🩺 Las 3 Conclusiones Dinámicas de Referencia

### 1. Reserva Vagal y Acoplamiento Respiratorio
* **Variantes Narrativas Dinámicas**:
  * **Amplificación Alta** ($\Delta\text{RMSSD} \ge 20\text{ ms}$ o pico $\ge 1.5\times\text{basal}$):
    > *"Marcada amplificación parasimpática durante la respiración pautada en **[Fase_Pico]** (RMSSD de **[RMSSD_Basal]** a **[RMSSD_Pico]** ms y HF relativo de **[HF_Pico]**%). Confirma un acoplamiento cardiorrespiratorio normal y alta capacidad de modulación vagal."*
  * **Amplificación Moderada** ($\Delta\text{RMSSD} > 0\text{ ms}$):
    > *"Modesta amplificación parasimpática durante la respiración pautada en **[Fase_Pico]** (RMSSD de **[RMSSD_Basal]** a **[RMSSD_Pico]** ms y HF relativo de **[HF_Pico]**%). Refleja modulación vagal presente con respuesta amortiguada al estímulo respiratorio."*
  * **Respuesta Atenuada / Paradójica** ($\Delta\text{RMSSD} \le 0\text{ ms}$):
    > *"Respuesta vagal atenuada o paradójica durante la respiración pautada (RMSSD basal de **[RMSSD_Basal]** ms vs pico de **[RMSSD_Pico]** ms, HF relativo **[HF_Pico]**%). Sugiere baja reactividad parasimpática o interferencia autonómica en reposo."*
* **Variables Fisiológicas**:
  * **RMSSD_Basal**: Fase 1 (DS) - Decúbito Supino (`rmssd[0]`).
  * **Fase_Pico**: Detecta automáticamente la fase de mayor amplificación entre RC10 (`rmssd[1]`) y RC12 (`rmssd[2]`).
  * **HF_Pico**: Potencia relativa HF en la fase pico (`hf[1]` o `hf[2]`).

---

### 2. Tolerancia Ortostática y Carga Dinámica
* **Variantes Narrativas Dinámicas**:
  * **Ortostatismo**:
    * $0 \le \Delta\text{FC} < 30\text{ lpm}$: *"Respuesta barorrefleja intacta sin taquicardia postural patológica (**[Dif_FC_Ortostática]** lpm)."*
    * $\Delta\text{FC} \ge 30\text{ lpm}$: *"Marcada taquicardia ortostática postural (**[Dif_FC_Ortostática]** lpm), sugestiva de reactividad postural elevada."*
    * $\Delta\text{FC} < 0\text{ lpm}$: *"Respuesta ortostática atípica con desaceleración cronotrópica (**[Dif_FC_Ortostática]** lpm)."*
  * **Carga en Sentadillas (Ruffier)**:
    * $\text{SNS} \ge 3.0$: *"Marcada activación simpática durante las 30 sentadillas (SNS index **[SNS_Pico_Ruffier]**, FC pico **[FC_Pico_Ruffier]** lpm) con repliegue vagal transitorio."*
    * $1.0 \le \text{SNS} < 3.0$: *"Adecuada activación simpática durante las 30 sentadillas (SNS index **[SNS_Pico_Ruffier]**, FC pico **[FC_Pico_Ruffier]** lpm) con control hemodinámico."*
    * $\text{SNS} < 1.0$: *"Respuesta simpática amortiguada durante las sentadillas (SNS index **[SNS_Pico_Ruffier]**, FC pico **[FC_Pico_Ruffier]** lpm)."*

---

### 3. Cinética de Restauración Homeostática
* **Variantes Narrativas Dinámicas**:
  * **Restauración Completa** ($\text{RMSSD}_{\text{REC}} \ge \text{RMSSD}_{\text{Basal}}$):
    > *"Excelente reactivación vagal post-esfuerzo: el RMSSD recupera a **[RMSSD_Recuperación]** ms superando el valor basal (**[RMSSD_Basal]** ms, **[Ratio]%**) y el balance LF/HF se restablece a **[LFHF_Recuperación]** en los 6 minutos posteriores al ejercicio."*
  * **Recuperación Parcial** ($70\% \le \text{Ratio} < 100\%$):
    > *"Reactivación vagal post-esfuerzo en curso: el RMSSD alcanza **[RMSSD_Recuperación]** ms (**[Ratio]%** del valor basal de **[RMSSD_Basal]** ms) con balance LF/HF en **[LFHF_Recuperación]** a los 6 minutos del ejercicio."*
  * **Recuperación Incompleta / Retrasada** ($\text{Ratio} < 70\%$):
    > *"Recuperación vagal post-esfuerzo incompleta/lenta: el RMSSD desciende a **[RMSSD_Recuperación]** ms (**[Ratio]%** del valor basal de **[RMSSD_Basal]** ms) con predominio simpático persistente (LF/HF **[LFHF_Recuperación]**, PNS index **[PNS_Recuperación]**)."*


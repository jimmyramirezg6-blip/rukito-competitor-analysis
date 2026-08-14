# 🥩 Rukito vs. Competencia — Análisis de Reseñas de Google Maps

Proyecto de **Data Analytics & NLP** para realizar un benchmarking competitivo de **Rukito Grill&Drink (Alborada, Guayaquil)** frente a 7 parrillas competidoras, transformando opiniones no estructuradas de Google Maps en insights accionables de negocio.

---

## 📊 Vistas del Proyecto
![Dashboard Overview](https://rukito-competitor-analysis-dxqme59ou3th94wfwicoba.streamlit.app/)
![alt text](image.png)
---

## 🚀 Estado del Proyecto
- [x] **Fase 1: Recolección de Datos** — Scraping de +900 reseñas en Google Maps vía Apify.
- [x] **Fase 2: Limpieza y Preprocesamiento** — Normalización de texto y remoción de duplicados/ruido.
- [x] **Fase 3: Análisis de Sentimiento** — Clasificación de polaridad (POS / NEU / NEG) con `pysentimiento` (RoBERTa).
- [x] **Fase 4: Modelado de Temas (Topic Modeling)** — Extracción de aspectos clave (*carne, precio, ambiente, moro, porciones, tiempo_espera, atencion_servicio*).
- [x] **Fase 5: Dashboard Interactivo** — Aplicación web funcional en Streamlit para toma de decisiones.

---

## 🛠️ Stack Tecnológico
* **Recolección:** Apify (Google Maps Scraper)
* **Procesamiento de Datos:** Python (`pandas`, `numpy`, `pathlib`)
* **Procesamiento de Lenguaje Natural (NLP):** `pysentimiento` (Transformers en español)
* **Visualización & Dashboard:** Streamlit, Plotly Express & Graph Objects

---

## 💡 Principales Hallazgos (Business Insights)
* **Posicionamiento Relativo:** Rukito cuenta con una nota promedio de **4.25⭐** (puesto 6/8 en la zona), situándose por encima de la media de la competencia (4.20⭐), pero con una brecha de 0.20⭐ frente al líder (*MoroGrill*).
* **Fuga de Puntos (Fricción):** El **24% de las reseñas de Rukito son negativas**, duplicando la tasa de fricción de los competidores Top 3.
* **Ventajas Competitivas:** Rukito supera ampliamente a la competencia en **tiempo de espera (+0.52)**, **abundancia de porciones (+0.38)** y la satisfacción con sus **moros (+0.33)**.
* **Áreas de Oportunidad:** La principal brecha negativa está en la percepción de la **carne (-0.22)** y el **ambiente (-0.12)**.

---

## 📂 Estructura del Proyecto

```rukito-competitor-analysis/
│
├── data/
│   ├── raw/            ← CSVs originales de Apify, sin tocar nunca
│   ├── processed/       ← datos limpios (Fase 2)
│   └── final/            ← datos con sentimiento + temas listos para el dashboard
│
├── notebooks/            ← Jupyter notebooks 
│   ├── 01_scraping_check.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_sentiment_analysis.ipynb
│   ├── 04_topic_extraction.ipynb
│   └── 05_comparative_insights.ipynb
│
├── src/                   ← funciones reutilizables en .py
│   ├── cleaning.py
│   ├── sentiment.py
│   └── topics.py
│
├── dashboard/
│   └── app.py            ← tu app de Streamlit (Fase 6)
│
├── reports/    
│   └── summary/            ← reporte ejecutivo / README final
│
├── requirements.txt
├── README.md
└── .gitignore
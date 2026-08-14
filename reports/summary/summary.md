# 🥩 Rukito vs. Competencia — Análisis de Reseñas de Google Maps

Análisis comparativo de sentimiento y temas extraídos de reseñas de Google Maps, 
para identificar fortalezas y debilidades de **Rukito Grill&Drink (Alborada)** 
frente a 7 restaurantes de parrilla competidores en Guayaquil, Ecuador.

🔗 **[Ver Dashboard en vivo](https://rukito-competitor-analysis-dxqme59ou3th94wfwicoba.streamlit.app/)**

---

## 📌 Problema de negocio

¿Dónde está perdiendo Rukito frente a su competencia directa, y qué debería 
priorizar mejorar? Este proyecto responde esa pregunta usando NLP sobre miles 
de reseñas reales de Google Maps, en lugar de depender solo del rating promedio 
(que, como se documenta más abajo, esconde matices importantes).

## 🎯 Hallazgos clave

Basado en ~1,000+ reseñas en español, con un umbral mínimo de 15 menciones 
por (restaurante, tema) para garantizar significancia estadística:

| Tema | Hallazgo | Evidencia |
|---|---|---|
| 🔴 **Carne** | Debilidad más marcada. Rukito es el tercer restaurante con scrore promedio superado por restaurantes como MoroGrill, Casa Res, etc. | Brecha de -0.11 vs. promedio competencia|
| 🔴 **Ambiente e instalaciones** | Segunda debilidad más marcada. Rukito ocupa el penúltimo puesto en este tema, siendo uno de los más bajos co un 0.38 con respecto al 0.75 del restaurante que lidera esta categoría. | Brecha de -0.11 vs. promedio competencia|
| 🔴 **Atención al servicio** | Tercera debilidad más consistente, con la muestra más grande de todo el análisis | Brecha de -0.01 vs. promedio competencia|
| 🔴 **Sabor de la comida** | Tercera debilidad, con porcentaje negativo leve, pero con importancia en el análisis | Brecha de -0.01 vs. promedio competencia|
| 🟢 **Tiempo de espera** | Fortaleza relativa: la espera es un problema de **toda la industria** de parrillas en Guayaquil, pero Rukito lo maneja mejor que el promedio, en comparación con los resturantes Casa Resy y Tomahawk | Brecha de +0.52 vs. promedio competencia|
| 🟡 **Moro** | Ligeramente por encima del promedio, sin ser una fortaleza dramática | Brecha de +0.32 vs. promedio competencia|

**Conclusión central**: El desafío de Rukito es doble, enfrenta una debilidad crítica en su oferta central (calidad de la carne, brecha de -0.11) a la par de un déficit de experiencia física en el local (ambiente e instalaciones, brecha de -0.11). Su ventaja competitiva real no reside en la parrilla, sino en su eficiencia operativa (tiempos de espera liderando la zona con +0.52) y la consistencia de su moro (+0.32).

## 🛠️ Metodología

1. **Scraping**: reseñas de Google Maps extraídas vía Apify (Google Maps 
   Reviews Scraper), acotadas a 8 restaurantes de parrilla en Guayaquil.
2. **Limpieza**: unificación de fuentes, normalización de texto, filtrado 
   de reseñas entre 2020-2026 (ver *Decisiones metodológicas*).
3. **Análisis de sentimiento**: modelo `pysentimiento` (RoBERTuito, 
   específico para español), aplicado solo a reseñas detectadas como 
   español para evitar ruido de un modelo monolingüe.
4. **Extracción de temas**: diccionario de palabras clave por categoría 
   (sabor, carne, atención, tiempo de espera, ambiente, precio, etc.), 
   con matching por límites de palabra (`\b`) para evitar falsos positivos.
5. **Validación de confiabilidad**: solo se reportan conclusiones para 
   combinaciones (restaurante, tema) con ≥15 menciones.
6. **Dashboard**: visualización interactiva con Streamlit + Plotly.

## ⚠️ Decisiones metodológicas y limitaciones

Documentadas explícitamente por transparencia analítica:

- **Rango de fechas (2020-2026)**: el scraping trajo reseñas desde 2011, 
  pero se acotó el análisis a los últimos años para reflejar la experiencia 
  reciente del negocio, no su historial completo.
- **Filtro de idioma**: el análisis de sentimiento se aplicó únicamente a 
  reseñas en español; reseñas en otros idiomas (~2-3% del total) se 
  documentan aparte pero no se usan en las métricas comparativas.
- **Umbral de confiabilidad (n≥15)**: temas como `precio`  y `porciones`
  no alcanzaron suficientes menciones en algunos restaurantes 
  y se excluyeron de las conclusiones principales para evitar afirmaciones 
  basadas en muestras pequeñas.
- **Volumen desigual entre restaurantes**: Rukito (sucursal Alborada) tiene 
  significativamente más reseñas que algunos competidores; todas las 
  comparaciones se hacen en porcentajes/promedios, nunca en conteos absolutos.
- **Detección de idioma en textos cortos**: `langdetect` no es confiable 
  por debajo de ~20 caracteres; los textos cortos se asumen en español 
  dado el contexto geográfico del proyecto.

## 🧰 Stack técnico

- **Scraping**: Apify (Google Maps Reviews Scraper)
- **Procesamiento**: Python, Pandas
- **NLP**: pysentimiento (sentimiento), diccionario de keywords + regex (temas)
- **Dashboard**: Streamlit, Plotly
- **Control de versiones**: Git / GitHub
o

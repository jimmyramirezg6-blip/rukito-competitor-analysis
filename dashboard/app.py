from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st

# ===== CONFIGURACIÓN DE RUTAS Y PÁGINA =============
BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="Rukito vs. Competencia - Análisis de Reseñas",
    page_icon="🥩",
    layout="wide"
)

RUKITO = 'Rukito Grill&Drink - Alborada'
UMBRAL_MINIMO = 15

# ===== CARGA DE DATOS (con cache para performance) =============
@st.cache_data
def cargar_datos():
    ruta_reviews = BASE_DIR / 'data' / 'final' / 'reviews_with_topics.csv'
    ruta_long = BASE_DIR / 'data' / 'final' / 'reviews_topics_long.csv'
    
    if not ruta_reviews.exists():
        st.error(f"No se encontró el archivo: {ruta_reviews}. Ejecuta primero `python src/topics.py`.")
        st.stop()
        
    df = pd.read_csv(ruta_reviews)
    df_temas = pd.read_csv(ruta_long)
    return df, df_temas

df, df_temas = cargar_datos()

# ======= TÍTULO =======================
st.title("🥩 Rukito vs. Competencia - Análisis de Reseñas de Google Maps")
st.caption("Benchmarking de sentimiento y temas frente a 7 parrillas competidoras en Guayaquil")

# ====================================================
st.header("📊 Overview General")

col1, col2, col3, col4 = st.columns(4)

df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

rating_rukito = df[df['restaurante'] == RUKITO]['rating'].mean()
rating_promedio_competencia = df[df['restaurante'] != RUKITO]['rating'].mean()
n_reviews_rukito = len(df[df['restaurante'] == RUKITO])

# Ranking (1 es la nota más alta)
rankings = df.groupby('restaurante')['rating'].mean().rank(ascending=False)
posicion_rating = rankings.get(RUKITO, 0)

with col1:
    st.metric('Rating Rukito', f'{rating_rukito:.2f}⭐')

with col2:
    st.metric('Rating promedio competencia', f'{rating_promedio_competencia:.2f}⭐')

with col3: 
    st.metric('Reseñas analizadas (Rukito)', n_reviews_rukito)
    
with col4: 
    st.metric('Ranking', f'{int(posicion_rating)}/{len(rankings)}')

st.divider()

# Gráfico de barra: rating promedio por restaurante
# Ordenamos ascendente para que Plotly coloque el mayor arriba en horizontal
rating_por_restaurante = (
    df.groupby('restaurante')['rating']
    .mean()
    .sort_values(ascending=True)
    .reset_index()
)

rating_por_restaurante['color'] = rating_por_restaurante['restaurante'].apply(
    lambda x: '#E63946' if x == RUKITO else '#457B9D'
)

fig_overview = px.bar(
    rating_por_restaurante,
    x='rating',
    y='restaurante', 
    orientation='h', 
    title='Rating promedio por restaurante', 
    color='color',
    color_discrete_map='identity',
    text=rating_por_restaurante['rating'].round(2)
)
fig_overview.update_xaxes(range=[3.0, 5.0])  # Ajuste para visibilizar diferencias

st.plotly_chart(fig_overview, use_container_width=True)

# ====== SECCION 2 : SENTIMIENTO GENERAL ======================

st.header('💬 Sentimiento General por Restaurante')

sentimiento_pct = pd.crosstab(df_temas['restaurante'], df_temas['sentimiento'], normalize='index') * 100

# Asegurar que existan las tres columnas
for col_sent in ['NEG', 'NEU', 'POS']:
    if col_sent not in sentimiento_pct.columns:
        sentimiento_pct[col_sent] = 0.0

sentimiento_pct = sentimiento_pct[['NEG', 'NEU', 'POS']]

fig_sentimiento = go.Figure()
colores = {'NEG': '#E63946', 'NEU': '#F1C40F', 'POS': '#2A9D8F'}

for sent in ['NEG', 'NEU', 'POS']: 
    fig_sentimiento.add_trace(go.Bar(
        y=sentimiento_pct.index,
        x=sentimiento_pct[sent],
        name=sent,
        orientation='h',
        marker_color=colores[sent]
    ))
    
fig_sentimiento.update_layout(barmode='stack', title='Distribución de sentimiento (%)')
st.plotly_chart(fig_sentimiento, use_container_width=True)

# ====== SECCION 3 - COMPARADOR DE TEMAS ==========
st.header('🔍 Comparador de Temas')

temas_disponibles = sorted(df_temas['temas_detectados'].dropna().unique().tolist())
tema_seleccionado = st.selectbox('Selecciona un tema para comparar:', temas_disponibles)

# Filtramos y calculamos con el umbral de confiabilidad
df_tema_filtrado = df_temas[df_temas['temas_detectados'] == tema_seleccionado].copy()

# Fix del typo 'NEg' -> 'NEG'
mapa_sent = {'POS': 1, 'NEU': 0, 'NEG': -1}
df_tema_filtrado['score'] = df_tema_filtrado['sentimiento'].map(mapa_sent)

resumen_tema = df_tema_filtrado.groupby('restaurante').agg(
    score_promedio=('score', 'mean'),
    n_menciones=('score', 'count')
).reset_index()

resumen_tema['confiable'] = resumen_tema['n_menciones'] >= UMBRAL_MINIMO
resumen_tema = resumen_tema.sort_values('score_promedio', ascending=True)

fig_tema = px.bar(
    resumen_tema, 
    x='score_promedio', 
    y='restaurante', 
    orientation='h', 
    color='confiable', 
    color_discrete_map={True: '#457B9D', False: '#CCCCCC'},
    hover_data=['n_menciones'], 
    title=f'Sentimiento promedio: {tema_seleccionado}'
)

st.plotly_chart(fig_tema, use_container_width=True)

if not resumen_tema['confiable'].all(): 
    st.caption('⚪ Barras en gris = menos de 15 menciones (resultado no concluyente).')

# ====== SECCION 4 - RUKITO VS. COMPETENCIA =============

st.header('🎯 Rukito vs. Competencia: Brechas por tema')

# Ruta corregida a brechas_competencia.csv
ruta_brechas = BASE_DIR / 'data' / 'final' / 'rukito_vs_competencia.csv'

if ruta_brechas.exists():
    comparacion = pd.read_csv(ruta_brechas, index_col=0).dropna()

    fig_brecha = go.Figure()
    colores_brecha = ['#2A9D8F' if x > 0 else '#E63946' for x in comparacion['brecha']]

    fig_brecha.add_trace(go.Bar(
        x=comparacion['brecha'], 
        y=comparacion.index, 
        orientation='h', 
        marker_color=colores_brecha
    ))

    fig_brecha.update_layout(
        title='Brecha de sentimiento: Rukito vs. Promedio Competencia',
        xaxis_title='<- Rukito peor | Rukito mejor ->'
    )

    st.plotly_chart(fig_brecha, use_container_width=True)

    st.markdown("""
        **Cómo leer este gráfico:**
        * 🟢 **Barras verdes (derecha):** Temas donde Rukito supera al promedio de la competencia.
        * 🔴 **Barras rojas (izquierda):** Áreas de oportunidad donde Rukito está por debajo de la competencia.
    """)
else:
    st.warning("No se encontró el archivo de brechas competitivas. Ejecuta `python src/topics.py` para generarlo.")

# ===== SECCIÓN 5 - EXPLORADOR DE RESEÑAS ================
st.header('📖 Explorador de Reseñas')

col1, col2, col3 = st.columns(3)

with col1: 
    restaurante_filtro = st.selectbox('Restaurante:', ['Todos'] + sorted(df['restaurante'].unique().tolist()))
with col2: 
    sentimiento_filtro = st.selectbox('Sentimiento:', ['Todos', 'POS', 'NEU', 'NEG'])
with col3: 
    tema_filtro = st.selectbox('Tema:', ['Todos'] + temas_disponibles)
    
df_explorar = df_temas.copy()

if restaurante_filtro != 'Todos': 
    df_explorar = df_explorar[df_explorar['restaurante'] == restaurante_filtro]
if sentimiento_filtro != 'Todos': 
    df_explorar = df_explorar[df_explorar['sentimiento'] == sentimiento_filtro]
if tema_filtro != 'Todos': 
    df_explorar = df_explorar[df_explorar['temas_detectados'] == tema_filtro]

# Fallback de nombre de columna para el texto
col_texto = 'text_limpio' if 'text_limpio' in df_explorar.columns else ('review_texto' if 'review_texto' in df_explorar.columns else 'texto')

columnas_mostrar = [c for c in ['restaurante', col_texto, 'sentimiento', 'rating'] if c in df_explorar.columns]

st.dataframe(
    df_explorar[columnas_mostrar].drop_duplicates(),
    use_container_width=True
)
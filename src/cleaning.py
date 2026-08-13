"""
cleaning.py
Carga los CSV crudos de Apify (data/raw), los unifica, limpia el texto, 
detecta idioma y exporta dos datasets a data/processed/:
    - reviews_all.csv           -> todas las reseñas (con y sin texto), para métricas generales.
    - reviews_with_text.csv     -> solo reseñas con texto, limpias y con idiomas detectado. 
Correr directo con: python src/cleaning.py
"""

import re 
import unicodedata
from pathlib import Path
import pandas as pd 
from langdetect import detect, LangDetectException

BASE_DIR = Path(__file__).resolve().parent.parent

# -- Decisiones metodológicas del proyecto (documentadas explicitamente)--

# Debajo de este número de caracteres, langdetect no es confiable
# (textos cortos suelen clasificarse mal como rumano, catalán, etc.)

LONGITUD_MINIMA_DETECCION_IDIOMA = 20

# El scraping trajo reseñas desde 2011, pero el volumne de esos años muy
# antiguos es bajo y poco representativo del negocio actual. Se acota el 
# análisis a 2020-2026 para reflejar la experiencia reciente del cliente. 

AÑO_MINIMO = 2020
 
COLUMNAS_UTILES = [
    'text', 'stars', 'publishedAtDate', 'title',
    'reviewDetailedRating/Comida', 'reviewDetailedRating/Servicio', 
    'reviewDetailedRating/Ambiente', 'reviewContext/Tiempo de espera',
    'likesCount', 'reviewerNumberOfReviews', 'isLocalGuide'
]


RENOMBRES_COLUMNAS = {
    'title': 'restaurante',
    'text': 'review_texto',
    'publishedAtDate' : 'fecha',
    'stars': 'rating',
    'reviewDetailedRating/Comida':'rating_comida',
    'reviewDetailedRating/Servicio':'rating_servicio',
    'reviewDetailedRating/Ambiente':'rating_ambiente',
    'reviewContext/Tiempo de espera':'tiempo_espera_reportado',
}

def limpiar_texto(texto): 
    """Normaliza unicode y espacios. NO quita tildes ni pasa a minúsculas:
    pysentimiento funciona mejor con el texto en su forma natural."""
    
    if pd.isna(texto): 
        return texto
    texto = unicodedata.normalize('NFC', str(texto))
    texto = re.sub(r'\s+',' ',texto)
    return texto.strip()

def detectar_idioma(texto:str)->str:
    """Detecta idioma con manejo de errores. Textos muy cortos se asumen
    español: es la asunción más razonable dado el contexto (reseñas en
    Guayaquil) y langdetect no es confiable en textos breves.""" 
    if pd.isna(texto) or len(str(texto).strip()) < LONGITUD_MINIMA_DETECCION_IDIOMA: 
        return 'es'
    try: 
        return detect(texto)
    except  LangDetectException: 
        return 'unknown'
    
    
# Función para limpiar el  dataFrame
def limpiar_df(df: pd.DataFrame):
    """Renombra columnas, filtra por fecha, separa reseñas con/sin texto, 
    limpia el texto y detecta idioma. Retorna (df_completo, df_texto).""" 
    # Convertir fecha  filtrar desde 2020
    df = df.rename(columns=RENOMBRES_COLUMNAS)
    
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    n_antes_filtro_fecha = len(df)
    df = df[df['fecha'].dt.year >= AÑO_MINIMO].copy()
    print(f'Filtro de fecha (>= {AÑO_MINIMO}): {n_antes_filtro_fecha} ->  {len(df)} reseñas '
          f'{n_antes_filtro_fecha - len(df)} descartadas por ser anteriores a {AÑO_MINIMO}')
    
    # Marcar las reseñas que tienen texto
    df['tiene_texto'] = df['review_texto'].notna() & (df['review_texto'].astype(str).str.strip() != '')

    # Separamos los DataFrames
    df_completo = df.copy()
    df_texto = df[df['tiene_texto']].copy()
        
        
    # Aplicar limpieza de texto  y detección de idioma
    df_texto['text_limpio'] =df_texto['review_texto'].apply(limpiar_texto)
    df_texto['idioma_detectado'] = df_texto['text_limpio'].apply(detectar_idioma)
    
    return df_completo, df_texto
    



def cargar_datos():  
    '''Función principal: carga todos los CSV de data/raw, limpia y exporta a data/processed'''

    # === 1. CARGA DE DATOS ===
    carpeta = BASE_DIR/'data'/'raw'
    archivos = list(carpeta.glob('*.csv'))
    if not archivos: 
        raise FileNotFoundError(f'No se encontraron archivos CSV en {carpeta}')
    
    print('⏳ Buscando archivos..')
    print(f'⚙️  Archivos encontrados: {len(archivos)}')    
    
    dfs = []
    for p in archivos: 
        try: 
            dfs.append(pd.read_csv(p, usecols=RENOMBRES_COLUMNAS))
        except Exception as e: 
            print(f'Error leyendo {p.name}: {e} -- archivo omitido')
    if not dfs: 
        raise RuntimeError("No se pudo leer ningún archivo CSV válido")
        
    df = pd.concat(dfs, ignore_index=True)
    print(f'Total de reseñas combianadas: {len(df)}')
    
    # -- Validación: confirmar que no se perdió ningún restaurante silenciosamente
    n_restaurantes_cargados = df['title'].nunique() if 'title' in df.columns else None
    if len(dfs) != len(archivos):
        print(f'⚠️ ATENCIÓN: se leyeron {len(dfs)} de {len(archivos)} archivos.'
              f'Revisa los errores de arriba (posibles columnas faltantes en algún CSV)')
    
    # === 2. LIMPIEZA ===
    print('⏳ Limpieza de datos...') 
    df_completo, df_texto = limpiar_df(df)
    
    n_restaurantes_finales = df_completo['restaurante'].nunique()
    print(f'✅ Restaurantes en el dataset final: {n_restaurantes_finales}')
    if n_restaurantes_cargados is not None and n_restaurantes_finales != n_restaurantes_cargados: 
        print(f'⚠️ ATENCIÓN: había {n_restaurantes_cargados} restaurantes antes de limpiar'
              f'y quedaron {n_restaurantes_finales}. Verifica si el filtro de fecha elimminó'
              f'algún restaurante por completo.')
    
    # === 3. EXPORTAR ===
    carpeta_salida = BASE_DIR/'data'/'processed'
    carpeta_salida.mkdir( parents=True, exist_ok=True) # Crea la capeta si no existe
    
    ruta_df_completo = carpeta_salida / "reviews_all.csv"
    ruta_df_texto = carpeta_salida / "reviews_with_text.csv"
    
    # Exportamos DataFrames
    
    df_completo.to_csv(ruta_df_completo, index=False, encoding="utf-8-sig")
    df_texto.to_csv(ruta_df_texto, index=False, encoding="utf-8-sig")
    
    print(f'📁 Archivo reviews_all guardado en:  {ruta_df_completo}')
    print(f'📁 Archivo reviews_with_text guardado en {ruta_df_texto} ')
    print(f'  Con texto: {len(df_texto)} / {len(df_completo)} '
          f'({len(df_texto) / len(df_completo):.1%})')

    return df_completo, df_texto



if __name__ == "__main__":
    df_completo, df_texto =cargar_datos()
   
    

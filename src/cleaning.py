# Imports
from pathlib import Path
import pandas as pd 
import numpy as np
import re 
import unicodedata
from langdetect import detect, LangDetectException
import glob
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Función para limpieza de texto para la detección de idioma
def limpiar_texto(texto): 
    if pd.isna(texto): 
        return texto
    # Normalizar unicode 
    texto = unicodedata.normalize('NFC', str(texto))
    # Quitar salto de líneas mútlipes y espaciados extras
    texto = re.sub(r'\s+',' ',texto)
    # Quitar espacioes al inicio/final
    texto = texto.strip()
    return texto

# Función de detección de idioma
def detectar_idioma(texto): 
    if pd.isna(texto) or len(texto.strip()) < 20: 
        return 'es'
    try: 
        return detect(texto)
    except  LangDetectException: 
        return 'unknown'
    
    
# Función para limpiar el  dataFrame
def limpiar_df(df): 
    # Cambio de nombre a columnas
    df = df.rename(columns={
        'title': 'restaurante',
        'text': 'review_texto',
        'publishedAtDate' : 'fecha',
        'stars': 'rating',
        'reviewDetailedRating/Comida':'rating_comida',
        'reviewDetailedRating/Servicio':'rating_servicio',
        'reviewDetailedRating/Ambiente':'rating_ambiente',
        'reviewContext/Tiempo de espera':'tiempo_espera_reportado',
    })
    
    # Convertir fecha  filtrar desde 2020
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df[df['fecha'].dt.year >=2020].copy()
    
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
    '''Función principal: cargar, limpiar y exportar datos'''

    # === SESION 1 : CARGA DE DATOS ============================================
    # Ruta 
    carpeta = BASE_DIR/'data'/'raw'
    
    archivos = list(carpeta.glob('*.csv'))
    if not archivos: 
        raise FileNotFoundError(f'No se encontraron archivos CSV en {carpeta}')
    
    print('⏳ Buscando archivos..')
    print(f'⚙️  Archivos encontrados: {len(archivos)}')    
    
    # Columnas a utilizar 
    columnas_utiles = [
    'text', 'stars', 'publishedAtDate', 'title',
    'reviewDetailedRating/Comida', 'reviewDetailedRating/Servicio', 
    'reviewDetailedRating/Ambiente', 'reviewContext/Tiempo de espera',
    'likesCount', 'reviewerNumberOfReviews', 'isLocalGuide'
    ]
    
    dfs = []
    for p in archivos: 
        try: 
            dfs.append(pd.read_csv(p, usecols=columnas_utiles))
        except Exception as e: 
            print(f'Error leyendo {p}: {e}')
    if dfs: 
        df =pd.concat(dfs, ignore_index=True ) 
    else: 
        print('No se pudo leer ningún archivo')
        df = pd.DataFrame()
        
    print(f'Total de reseñas combianadas: {len(df)}')
    
    # === SESION 2: LIMPIEZA Y EXPORTAR DATOS ============================================
    print('⏳ Limpieza de datos...')
    
    # Desempaquetamos los dos DataFrames que retorna limpiar_df
    df_completo, df_texto = limpiar_df(df)
    
    # Definir ruta 
    carpeta_salida = BASE_DIR/'data'/'processed'
    carpeta_salida.mkdir(
        parents=True, exist_ok=True
    ) # Crea la capeta si no existe
    
    ruta_df_completo = carpeta_salida / "reviews_all.csv"
    ruta_df_texto = carpeta_salida / "reviews_with_text.csv"
    
    # Exportamos DataFrames
    
    df_completo.to_csv(ruta_df_completo, index=False, encoding="utf-8-sig")
    df_texto.to_csv(ruta_df_texto, index=False, encoding="utf-8-sig")
    
    print(f'Archivo reviews_all guardado en:  {ruta_df_completo}')
    print(f'Archivo reviews_with_text guardado en {ruta_df_texto} ')

    
    return df_completo, df_texto



if __name__ == "__main__":
    df_completo, df_texto =cargar_datos()
   
    

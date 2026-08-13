"""
sentiment.py
Aplica análisis de sentimiento (pysentimiento, modelo en español) sobre las 
reseñas con texto ya limpiadas por cleaning.py

Decisión metodológica: solo se analiza sentimiento en reseñas detectadas como
español (es), ya que pysentimiento es un modelo monolingüe y aplicarlo a 
otros idiomas introduce ruido en las métricas comparativas. Las reseñas en
otros idiomas se guardan aparte, documentadas, no descartadas. 

Lee data/processed/reviews_with_text.csv (generado por cleaning.py) en vez de 
volver a correr el pipeline de limpieza completo --  así este script es rápido
y depende explícitamente del archivo de salida del paso anterior. Si cambiaste 
algo en data/raw/, corre primero 'python src/cleaning.py'

Correr directo con: python src/sentiment.py
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

IDIOMA_OBJETIVO = 'es'

# Carga "Lazy": el modelo (-cientos de MB) solo se descarga/carga la primera
# vez que se usa analizar_sentimiento(), no con solo importar este módulo. 
_analyzer = None

def _get_analyzer(): 
    global _analyzer
    if _analyzer is None: 
        from pysentimiento import create_analyzer
        print(f'⏳ Cargando modelo de sentimiento (pysentimiento)... primera vez puede tardar.')
        _analyzer = create_analyzer(task='sentiment', lang='es')
    return _analyzer


def analizador_sentimiento(texto:str)->pd.Series: 
    analyzer = _get_analyzer()
    resultado = analyzer.predict(texto)
    return pd.Series({
        'sentimiento': resultado.output,
        'prob_positivo': resultado.probas['POS'],
        'prob_negativo': resultado.probas['NEG'],
        'prob_neutral': resultado.probas['NEU']
    })
    

def sentimiento(): 
    """Carga reviews_with_text.csv, filtra español, aplica sentimiento y
    exporta reviews_with_sentimiento.csv + reviews_excluded_language.csv"""
    
    ruta_entrada = BASE_DIR / 'data' / 'processed' / 'reviews_with_text.csv'
    if not ruta_entrada.exists(): 
        raise FileNotFoundError(
            f'No se encontró {ruta_entrada}. Corre primero: python scr/cleaning.py'
        )
    
    df_texto = pd.read_csv(ruta_entrada)
    df_es = df_texto[df_texto['idioma_detectado'] == IDIOMA_OBJETIVO].copy()
    df_otros = df_texto[df_texto['idioma_detectado'] != IDIOMA_OBJETIVO].copy()
    print(f'Español: {len(df_es)} reseñas -> análisis de sentimiento')
    print(f'Otros idiomas: {len(df_otros)} reseñas -> exluidas, documentadas aparte')
    
    print(f'⏳ Analizando sentimiento (puede tardar varios minnutos)...')
    # Aplicamos la función analizador_sentimiento
    df_es[['sentimiento','prob_positivo','prob_negativo','prob_neutral']] = (
        df_es['text_limpio'].apply(analizador_sentimiento)
    )
    
    carpeta_salida = BASE_DIR/'data'/'processed'
    carpeta_salida.mkdir( parents=True, exist_ok=True) 
    
    ruta_df_es = carpeta_salida / "reviews_with_sentimiento.csv"
    ruta_df_otros = carpeta_salida/ "reviews_excluded_language.csv"
    
    df_es.to_csv(ruta_df_es, index=False, encoding="utf-8-sig")
    df_otros.to_csv(ruta_df_otros,index=False, encoding="utf-8-sig")
    
    print(f'📁 Archivo reviews_with_sentimiento guardado en: {ruta_df_es}')
    print(f'📁 Archivo reviews_excluded_language guardado en: {ruta_df_otros}')
    print(df_es['sentimiento'].value_counts(normalize=True).round(3))
    
    return df_es, df_otros


if __name__ == "__main__":
    df_es, df_otros = sentimiento()
   
   
    
    
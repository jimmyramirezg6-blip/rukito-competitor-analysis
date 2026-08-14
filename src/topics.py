"""
topics.py
Detecta temas mencionados en cada reseña usando un diccionario de palabras
clave, y calcula el sentimiento promedio por (restaurante, tema).

⚠️ Usa límites de palabra (\\b) en la búsqueda para evitar falsos positivos
por coincidencia de substrings -- ej: la palabra "res" (carne de res) hacía
match dentro de "restaurante", "respetan", "rescatable" antes de este fix.

Solo se consideran confiables las celdas (restaurante, tema) con al menos
UMBRAL_MINIMO_MENCIONES menciones; el resto se marca como NaN para evitar
conclusiones basadas en muestras muy pequeñas (ej: un score de 1.00 basado
en una sola reseña).

Correr directo con: python src/topics.py
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

RUKITO = "Rukito Grill&Drink - Alborada"
UMBRAL_MINIMO_MENCIONES = 15
MAPA_SENTIMIENTO = {'POS': 1, 'NEU': 0, 'NEG': -1}

TEMAS = {
    "sabor_comida": ["sazon", "sabor", "rico", "delicioso", "sabroso", "insipido", "soso",
                      "exquisito", "delicia", "buenisima", "buenisimo", "manjar"],
    "carne": ["carne", "termino", "punto", "jugosa", "dura", "asado", "churrasco",
              "chuleta", "costilla", "cerdo", "pollo", "bistec", "parrillada",
              "carbon", "brasa", "correosa", "seca"],
    "moro": ["moro", "arroz", "menestra", "frejol", "frijol", "lenteja", "guarnicion"],
    "atencion_servicio": ["atencion", "servicio", "mesero", "mesera", "amable", "grosero",
                           "despota", "pesimo", "personal", "staff", "trato", "amabilidad"],
    "tiempo_espera": ["espera", "demora", "rapido", "lento", "tardaron", "minutos",
                       "tardanza", "demoro", "demoraron"],
    "porciones": ["porcion", "cantidad", "abundante", "tamano",
                  "pequeno", "grande", "suficiente", "escaso", "generoso", "generosa"],
    "precio": ["precio", "caro", "barato", "costoso", "economico", "accesible",
               "dolares", "valor", "costo"],
    "ambiente_instalaciones": ["ambiente", "espacio", "aire acondicionado", "mesa",
                                "bano", "musica", "ruido", "television", "local",
                                "decoracion", "limpieza", "limpio", "sucio", "iluminacion"],
}


def normalizar_para_busqueda(texto: str) -> str:
    """Minúsculas + sin tildes, para matching de palabras clave (distinto del
    texto usado para sentimiento, que se deja en su forma natural)."""
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto


def detectar_temas(texto_normalizado: str) -> list:
    """Devuelve los temas detectados en un texto, usando límites de palabra
    (\\b) para evitar falsos positivos por coincidencia de substrings."""
    temas_encontrados = []
    for tema, palabras_clave in TEMAS.items():
        for palabra in palabras_clave:
            patron = r'\b' + re.escape(palabra) + r'\b'
            if re.search(patron, texto_normalizado):
                temas_encontrados.append(tema)
                break
    return temas_encontrados


def calcular_brechas(tabla_confiable: pd.DataFrame, restaurante_foco: str) -> pd.DataFrame:
    """Brecha de sentimiento entre restaurante_foco y el promedio del resto,
    por cada tema con datos confiables."""
    scores_foco = tabla_confiable.loc[restaurante_foco]
    scores_competencia = tabla_confiable.drop(index=restaurante_foco).mean()

    comparacion = pd.DataFrame({
        restaurante_foco: scores_foco,
        'competencia_promedio': scores_competencia,
    })
    comparacion['brecha'] = comparacion[restaurante_foco] - comparacion['competencia_promedio']
    return comparacion.sort_values('brecha')


def temas():
    """Carga reviews_with_sentimiento.csv, detecta temas, calcula tablas de
    sentimiento/conteo/confiabilidad y exporta resultados a data/final/."""

    ruta_entrada = BASE_DIR / 'data' / 'processed' / 'reviews_with_sentimiento.csv'
    if not ruta_entrada.exists():
        raise FileNotFoundError(
            f'No se encontró {ruta_entrada}. Corre primero: python src/sentiment.py'
        )

    df = pd.read_csv(ruta_entrada)
    print(f'⏳ Detectando temas en {len(df)} reseñas...')

    df['texto_normalizado'] = df['text_limpio'].apply(normalizar_para_busqueda)
    df['temas_detectados'] = df['texto_normalizado'].apply(detectar_temas)

    n_sin_tema = (df['temas_detectados'].apply(len) == 0).sum()
    print(f'   Reseñas sin ningún tema detectado: {n_sin_tema} ({n_sin_tema / len(df):.1%})')

    df_temas = df.explode('temas_detectados')
    df_temas = df_temas[df_temas['temas_detectados'].notna()].copy()
    df_temas['sentimiento_score'] = df_temas['sentimiento'].map(MAPA_SENTIMIENTO)

    tabla_sentimiento = (
        df_temas.groupby(['restaurante', 'temas_detectados'])['sentimiento_score']
        .mean().unstack()
    )
    tabla_conteo = (
        df_temas.groupby(['restaurante', 'temas_detectados']).size().unstack(fill_value=0)
    )

    tabla_confiable = tabla_sentimiento.copy()
    tabla_confiable[tabla_conteo < UMBRAL_MINIMO_MENCIONES] = None

    n_confiables = tabla_confiable.notna().sum().sum()
    n_total_celdas = tabla_confiable.size
    print(f'   Celdas (restaurante x tema) confiables (n>={UMBRAL_MINIMO_MENCIONES}): '
          f'{n_confiables}/{n_total_celdas}')
    
    comparacion =calcular_brechas(tabla_confiable, RUKITO)

    carpeta_salida = BASE_DIR / 'data' / 'final'
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    df.to_csv(BASE_DIR / 'data' / 'processed' / 'reviews_with_topics.csv',
              index=False, encoding='utf-8-sig')
    df_temas.to_csv(carpeta_salida / 'reviews_topics_long.csv',
                     index=False, encoding='utf-8-sig')
    tabla_confiable.to_csv(carpeta_salida / 'sentiment_by_topic_confiable.csv',
                            encoding='utf-8-sig')
    tabla_conteo.to_csv(carpeta_salida / 'topic_mention_counts.csv',
                         encoding='utf-8-sig')
    
    comparacion.to_csv(carpeta_salida/'rukito_vs_competencia.csv', 
                       encoding='utf-8-sig')
    

    print(f'📁 Resultados guardados en: {carpeta_salida}')

    return df, df_temas, tabla_confiable, tabla_conteo, comparacion


if __name__ == "__main__":
    df, df_temas, tabla_confiable, tabla_conteo, comparacion = temas()
    print('\nTabla de sentimiento por tema (solo datos confiables):')
    print(tabla_confiable.round(2))
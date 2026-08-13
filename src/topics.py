from pathlib import Path
import pandas as pd 
import unicodedata
import re
from sentiment import sentimiento

BASE_DIR = Path(__file__).resolve().parent.parent

def main(): 
    # Cargar DataFrame
    df_es,_ = sentimiento()
    

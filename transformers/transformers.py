# import os
import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.pipeline import Pipeline
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import classification_report, accuracy_score, recall_score, precision_score, f1_score, roc_auc_score
# from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV, cross_val_score
# from sklearn.preprocessing import StandardScaler, label_binarize
import re
import warnings 
from sklearn.base import BaseEstimator, TransformerMixin
warnings.filterwarnings('ignore')



# PARA MODELO 1

# a classe CombineTextColumns é um Transformer customizado para combinar duas colunas de texto de um DataFrame.
# Esta classe permite combinar o conteúdo de duas colunas específicas de texto em um DataFrame
# em uma única coluna concatenada.
# 'col1' e 'col2' são as colunas que deverão ser passadas para serem unidas em um único texto.

class CombineTextColumns(BaseEstimator, TransformerMixin):
    def __init__(self, col1: str = 'Review_Title', col2: str = 'Review'):
        self.col1 = col1 
        self.col2 = col2

    def fit(self, X, y=None):
        return self


    # O método transform realiza a combinação das colunas de texto.
    def transform(self, X):

        
        # Combina as colunas de texto
        X_combined = X[self.col1] + ' ' + X[self.col2]
        return X_combined


# FullTextPreprocessor é um Transformer customizado para pré-processamento básico de um texto.
# A classe realiza várias etapas de pré-processamento em dados textuais, incluindo:
# - Tratamento de casos de inversão de sentido por negação com uso do 'not'.
# - Limpeza de texto (remoção de URLs, menções, hashtags, pontuação, números e espaços extras).
# - Remoção de stopwords.
# - Lematização.
# - Remoção de emojis.

class FullTextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return [self.preprocess_text(text) for text in X]

    # Realiza o pré-processamento completo em uma string de texto. Chamado pelo método `transform`.
    def preprocess_text(self, text):
        text = self.handle_negation(text)
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        text = self.apply_lemmatization(text)
        text = self.remove_emojis(text)
        return text
    
    # Limpa o texto removendo URLs, menções, hashtags, pontuação, números e espaços em excesso. Também converte o texto para minúsculas.
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # Remove stopwords do texto, baseando-se em uma lista de palavras irrelevantes em inglês.
    def remove_stopwords(self, text):
        return ' '.join([word for word in text.split() if word not in self.stop_words])

    # Aplica a lematização em cada palavra do texto, convertendo-as para suas formas básicas.
    def apply_lemmatization(self, text):
        return ' '.join([self.lemmatizer.lemmatize(word) for word in text.split()])

    # Remove emojis do texto, mantendo apenas caracteres ASCII.
    def remove_emojis(self, text):
        return text.encode('ascii', 'ignore').decode('ascii')

# Identifica negações que podem inverter o sentido no texto (palavras como "not") 
# e as aplica à próxima palavra, prefixando com "not_".
# Exemplo: "not good" -> "not_good".
    def handle_negation(self, text):
        negation = "not"
        words = text.split()
        negated_sentence = []
        negate = False
        
        for word in words:
            if word == negation:
                negate = True
            elif negate:
                negated_sentence.append(f"not_{word}")
                negate = False
            else:
                negated_sentence.append(word)
        
        return ' '.join(negated_sentence)
    


## PARA MODELO 2

# Transformer customizado para imputação de valores ausentes nas colunas de avaliações.
# O critério para uso da média ou mediana foi abordado em `data_exploration.ipynb`.  
# Esta classe calcula a média ou mediana para colunas específicas durante a etapa de ajuste (fit)
# e, em seguida, utiliza esses valores para substituir valores ausentes nas colunas correspondentes
# durante a etapa de transformação. 
# Para os casos das variáveis 'Food & Beverages', 'Inflight Entertainment', 'Wifi & Connectivity', 
# ela cria novas colunas binárias indicando onde os valores ausentes estavam presentes nas colunas de interesse, devido
# a maior frequência de valores inválidos.


class CustomImputer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y=None):

        # Verifica se X é um DataFrame e armazena as médias e medianas
        if isinstance(X, pd.DataFrame):
            self.means = {
                'Seat Comfort': int(X.loc[~X['Seat Comfort'].isna(), 'Seat Comfort'].astype(int).mean()),
                'Cabin Staff Service': int(X.loc[~X['Cabin Staff Service'].isna(), 'Cabin Staff Service'].astype(int).mean()),
                'Ground Service': int(X.loc[~X['Ground Service'].isna(), 'Ground Service'].astype(int).median()),
                'Food & Beverages': int(X.loc[~X['Food & Beverages'].isna(), 'Food & Beverages'].astype(int).median()),
                'Inflight Entertainment': int(X.loc[~X['Inflight Entertainment'].isna(), 'Inflight Entertainment'].astype(int).median()),
                'Wifi & Connectivity': int(X.loc[~X['Wifi & Connectivity'].isna(), 'Wifi & Connectivity'].astype(int).median())
            }
        return self
    
    def transform(self, X):

        X = X.copy()
        
        # Substituindo valores ausentes
        for col, value in self.means.items():
            if col in X.columns:
                X[col].fillna(value, inplace=True)
                X[col] = X[col].astype(int)
                
        # Criar variáveis para valores ausentes
        for col in ['Food & Beverages', 'Inflight Entertainment', 'Wifi & Connectivity']:
            if col in X.columns:
                X[f'{col}_isnan'] = X[col].isna().astype(int)
        
        return X
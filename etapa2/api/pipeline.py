# pipeline.py
import joblib
import pandas as pd
import spacy
import nltk
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin

from preprocessor import TextPreprocessor  # Import TextPreprocessor

# Descargar stopwords en español (will now happen in preprocessor.py)
# Cargar modelo de spaCy en español (will now happen in preprocessor.py)

# Cargamos el dataset
file_path = 'fake_news_spanish.csv'
df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
df.dropna(subset=['Titulo', 'Descripcion', 'Label'], inplace=True)
df.drop_duplicates(inplace=True)

df['Titulo_len'] = df['Titulo'].apply(lambda x: len(str(x)))
df['Descripcion_len'] = df['Descripcion'].apply(lambda x: len(str(x)))

# Definir características y etiquetas
X_text = df['Titulo'] + " " + df['Descripcion']
y = df['Label']

# Crear pipeline
pipeline = Pipeline([
    ('preprocessor', TextPreprocessor()),
    ('tfidf', TfidfVectorizer(max_features=5000)),
])

# Transformar el texto
X_tfidf = pipeline.fit_transform(X_text)

# Añadir características adicionales
X_extra = df[['Titulo_len', 'Descripcion_len']].values
X_combined = hstack([X_tfidf, X_extra])

# División de datos
X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, random_state=42)

# Entrenar modelo
xgb = XGBClassifier(
    use_label_encoder=False,
    eval_metric='logloss',
    random_state=42,
    n_estimators=300,
    max_depth=10,
    learning_rate=0.1,
    subsample=1.0,
    colsample_bytree=1.0
)
xgb.fit(X_train, y_train)

# Guardar pipeline y modelo con joblib
joblib.dump(pipeline, "text_pipeline.joblib")
joblib.dump(xgb, "xgboost_model.joblib")

print("Pipeline y modelo guardados correctamente.")
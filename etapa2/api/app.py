from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import joblib
import pandas as pd
import numpy as np
import spacy
import nltk
from nltk.corpus import stopwords
from sklearn.base import BaseEstimator, TransformerMixin
from scipy.sparse import hstack
from sklearn.metrics import precision_score, recall_score, f1_score

from preprocessor import TextPreprocessor

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Detección de Noticias Falsas",
    description="API para predecir si una noticia es falsa y reentrenar el modelo",
    version="1.0.0"
)

# Definir modelos de datos
class NoticiaInput(BaseModel):
    Titulo: str
    Descripcion: str
    Fecha: str

class NoticiaPrediccion(BaseModel):
    Titulo: str
    Descripcion: str
    Fecha: str
    Prediccion: str
    Probabilidad: float

class NoticiaReentrenoInput(BaseModel):
    Titulo: str
    Descripcion: str
    Fecha: str

class ReentrenoRequest(BaseModel):
    data: List[NoticiaReentrenoInput]
    labels: List[int]

class MetricasModelo(BaseModel):
    message: str
    precision: float
    recall: float
    f1_score: float

# Download Spanish stopwords and spaCy model (should be handled in preprocessor)

# Función para preprocesar datos (length features)
def preprocess_data(data_list: List[NoticiaInput]):
    df = pd.DataFrame([d.dict() for d in data_list])
    df["title_length"] = df["Titulo"].apply(len)
    df["description_length"] = df["Descripcion"].apply(len)
    return df

# Cargar pipeline de preprocesamiento y modelo
try:
    text_pipeline = joblib.load("text_pipeline.joblib")
    xgb_model = joblib.load("xgboost_model.joblib")
    print("Pipeline de texto y modelo XGBoost cargados correctamente")
except Exception as e:
    print(f"Error al cargar los modelos: {e}")
    raise HTTPException(status_code=500, detail=f"Error al cargar los modelos: {str(e)}")

# Endpoint 1: Predicción
@app.post("/predict/", response_model=Dict[str, List[NoticiaPrediccion]])
async def predict(noticias: List[NoticiaInput]):
    if not noticias:
        raise HTTPException(status_code=400, detail="No se proporcionaron datos para la predicción")

    try:
        df = preprocess_data(noticias)
        text_features = df["Titulo"] + " " + df["Descripcion"]
        tfidf_features = text_pipeline.transform(text_features)
        extra_features = df[['title_length', 'description_length']].values
        combined_features = hstack([tfidf_features, extra_features])

        predictions = xgb_model.predict(combined_features)
        probabilities = xgb_model.predict_proba(combined_features)[:, 1]

        response = []
        for i, (noticia, pred, prob) in enumerate(zip(noticias, predictions, probabilities)):
            response.append({
                'Titulo': noticia.Titulo,
                'Descripcion': noticia.Descripcion,
                'Fecha': noticia.Fecha,
                'Prediccion': 'Fake' if pred == 1 else 'Real',
                'Probabilidad': round(float(prob), 4)
            })

        return {"predictions": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")

# Endpoint 2: Reentrenamiento
@app.post("/retrain/", response_model=MetricasModelo)
async def retrain(data: ReentrenoRequest):
    if len(data.data) < 10:
        raise HTTPException(status_code=400, detail="Se requieren al menos 10 ejemplos para reentrenar")

    try:
        df = preprocess_data(data.data)
        y_new = data.labels
        text_features_new = df["Titulo"] + " " + df["Descripcion"]
        tfidf_features_new = text_pipeline.transform(text_features_new)
        extra_features_new = df[['title_length', 'description_length']].values
        combined_features_new = hstack([tfidf_features_new, extra_features_new])

        xgb_model.fit(combined_features_new, y_new)

        y_pred = xgb_model.predict(combined_features_new)

        precision = precision_score(y_new, y_pred)
        recall = recall_score(y_new, y_pred)
        f1 = f1_score(y_new, y_pred)

        joblib.dump(xgb_model, "xgboost_model.joblib")

        return MetricasModelo(
            message="Modelo reentrenado exitosamente",
            precision=round(float(precision), 4),
            recall=round(float(recall), 4),
            f1_score=round(float(f1), 4)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el reentrenamiento: {str(e)}")

# Endpoint para verificar que la API está funcionando
@app.get("/")
async def root():
    return {"mensaje": "API de Detección de Noticias Falsas activa"}

# Para ejecutar la API: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# preprocessor.py
import nltk
import spacy
import pandas as pd
from nltk.corpus import stopwords
from sklearn.base import BaseEstimator, TransformerMixin

try:
    stop_words = set(stopwords.words('spanish'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('spanish'))

try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("es_core_news_sm")
    nlp = spacy.load("es_core_news_sm")

class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.stop_words = stop_words

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self.preprocess_text(text) for text in X]

    def preprocess_text(self, text):
        if pd.isna(text):
            return ""
        doc = nlp(text.lower())
        tokens = [token.lemma_ for token in doc if token.text.isalpha()]
        filtered_tokens = [word for word in tokens if word not in self.stop_words]
        return " ".join(filtered_tokens)
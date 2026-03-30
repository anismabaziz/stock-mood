from sentence_transformers import SentenceTransformer
import keras
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer("yiyanghkust/finbert-tone")


@lru_cache(maxsize=1)
def get_classifier_model():
    return keras.models.load_model("models/model_v1.keras")


def warmup_models():
    try:
        get_embedding_model()
        get_classifier_model()
        return True
    except Exception:
        logger.exception("Model warmup failed; falling back to lazy loading")
        return False


def embed(texts):
    ## generate embeddings
    embedding_model = get_embedding_model()
    embeddings = embedding_model.encode(texts)

    return embeddings


def predict(embeddings):
    n = embeddings.shape[0]

    ## reshape embeddings
    embeddings_reshaped = embeddings.reshape(n, -1)

    ## load model
    model = get_classifier_model()

    ## perform Prediction
    predictions = model.predict(embeddings_reshaped, verbose=0)
    classes = ["Negative", "Neutral", "Positive"]
    sentiments = [classes[pred.argmax(-1)] for pred in predictions]

    return sentiments

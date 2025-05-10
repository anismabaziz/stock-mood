from sentence_transformers import SentenceTransformer
import tensorflow as tf
from tensorflow.keras import backend as K


def embed(texts):
    ## generate embeddings
    embedding_model = SentenceTransformer("yiyanghkust/finbert-tone")
    embeddings = embedding_model.encode(texts)

    return embeddings


def predict(embeddings):
    K.clear_session()

    n = embeddings.shape[0]

    ## reshape embeddings
    embeddings_reshaped = embeddings.reshape(n, -1)

    ## load model
    model = tf.keras.models.load_model("models/model_v1.keras")

    ## perform Prediction
    predictions = model.predict(embeddings_reshaped)
    classes = ["Negative", "Neutral", "Positive"]
    sentiments = [classes[pred.argmax(-1)] for pred in predictions]

    return sentiments

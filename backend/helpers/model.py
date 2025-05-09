from sentence_transformers import SentenceTransformer
import tensorflow as tf
from tensorflow.keras import backend as K


def embed(texts):
    ## Generate embeddings
    embedding_model = SentenceTransformer("yiyanghkust/finbert-tone")
    embeddings = embedding_model.encode(texts)

    return embeddings


def predict(embeddings):
    K.clear_session()

    n = embeddings.shape[0]

    ## Reshape embeddings
    embeddings_reshaped = embeddings.reshape(n, -1)

    ## Load model
    model = tf.keras.models.load_model("model/models/model_v1.keras")

    ## Perform Prediction
    predictions = model.predict(embeddings_reshaped)
    classes = ["Negative", "Neutral", "Positive"]
    sentiments = [classes[pred.argmax(-1)] for pred in predictions]

    return sentiments

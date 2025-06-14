from pydantic import BaseModel
from helpers.reddit import fetch_posts, model_post
from helpers.text import clean, count_words, vader_analysis
from helpers.model import predict, embed
from fastapi import APIRouter
import numpy as np

router = APIRouter()


# request body
class Stock(BaseModel):
    symbol: str


# prediction route
@router.post("/analyze")
def analyze_stock(stock: Stock):
    stock_symbol = stock.symbol

    ## fetch posts
    fetch_results = fetch_posts(stock_symbol)
    fetch_results = list(fetch_results)

    ## clean and embed posts
    texts = [clean(post) for post in fetch_results]
    embeddings = embed(texts)
    words_count = [count_words(text) for text in texts]
    vader_scores = [vader_analysis(text) for text in texts]
    vader_results = []
    for score in vader_scores:
        result = []
        for key, value in score.items():
            result.append(value)
        vader_results.append(result)

    # make features vector
    features = []
    for emb, count, vader in zip(embeddings, words_count, vader_results):
        emb = np.array(emb)
        combined = np.concatenate([emb, [count], vader])
        features.append(combined)
    features = np.array(features)

    ## run predictions
    predictions = predict(features)

    ## model posts
    results = [
        model_post(post, prediction)
        for post, prediction in zip(fetch_results, predictions)
    ]

    ## predictions disribution
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    for prediction in predictions:
        if prediction == "Positive":
            sentiment_counts["positive"] += 1
        elif prediction == "Negative":
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1

    return {
        "stock_symbol": stock_symbol,
        "results": results,
        "distribution": sentiment_counts,
    }

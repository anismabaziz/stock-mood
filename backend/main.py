from fastapi import FastAPI
from pydantic import BaseModel
from helpers.reddit import fetch_posts, model_post
from helpers.text import clean
from helpers.model import predict, embed

app = FastAPI()


@app.get("/ping")
def read_root():
    return {"message": "pong"}


class Stock(BaseModel):
    symbol: str


@app.post("/analyze")
def analyze_stock(stock: Stock):
    stock_symbol = stock.symbol

    ## Fetch posts
    fetch_results = fetch_posts(stock_symbol)
    fetch_results = list(fetch_results)

    ## Clean and embed posts
    texts = [clean(post) for post in fetch_results]
    embeddings = embed(texts)

    ## Run predictions
    predictions = predict(embeddings)

    ## Model posts
    results = [
        model_post(post, prediction)
        for post, prediction in zip(fetch_results, predictions)
    ]

    ## Predictions disribution
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    for prediction in predictions:
        if prediction == "Positive":
            sentiment_counts["positive"] += 1
        elif prediction == "Negative":
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1
    return {"results": results, "distribution": sentiment_counts}

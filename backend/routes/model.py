from pydantic import BaseModel
from helpers.reddit import fetch_posts, model_post
from helpers.text import clean, count_words, vader_analysis
from helpers.model import predict, embed
from fastapi import APIRouter, HTTPException
import numpy as np
import re
import logging
from prawcore.exceptions import PrawcoreException, RequestException

logger = logging.getLogger(__name__)

router = APIRouter()


# request body
class Stock(BaseModel):
    symbol: str


# prediction route
@router.post("/analyze")
def analyze_stock(stock: Stock):
    stock_symbol = stock.symbol.strip().upper()
    if not re.match(r"^[A-Z][A-Z0-9.\-]{0,9}$", stock_symbol):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SYMBOL",
                "error": "Please enter a valid stock symbol (e.g., AAPL, TSLA).",
            },
        )

    ## fetch posts
    try:
        fetch_results = fetch_posts(stock_symbol)
        fetch_results = list(fetch_results)
    except RequestException as exc:
        logger.warning("Reddit request failed for symbol=%s: %s", stock_symbol, exc)
        raise HTTPException(
            status_code=502,
            detail={
                "code": "REDDIT_DNS_FAILURE",
                "error": "Cannot reach Reddit right now (network or DNS issue). Please check your connection and try again.",
            },
        )
    except PrawcoreException as exc:
        logger.warning("Reddit fetch failed for symbol=%s: %s", stock_symbol, exc)
        raise HTTPException(
            status_code=502,
            detail={
                "code": "REDDIT_UNAVAILABLE",
                "error": "Unable to fetch Reddit posts right now. Please try again shortly.",
            },
        )
    except Exception:
        logger.exception("Unexpected fetch failure for symbol=%s", stock_symbol)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ANALYZE_FAILED",
                "error": "Unexpected server error while fetching posts.",
            },
        )

    if not fetch_results:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NO_POSTS",
                "error": f"No recent posts found for {stock_symbol} in r/stocks.",
            },
        )

    try:
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
    except Exception:
        logger.exception("Prediction pipeline failed for symbol=%s", stock_symbol)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "MODEL_UNAVAILABLE",
                "error": "Model inference is currently unavailable. Please try again later.",
            },
        )

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

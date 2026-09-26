import os
import re
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import praw

from pilot import RedditPost, Sentiment, SentimentPrediction

SOURCE_SUBREDDITS = (
    "stocks",
    "StockMarket",
    "investing",
    "wallstreetbets",
    "options",
    "ValueInvesting",
    "SecurityAnalysis",
    "pennystocks",
    "trading",
)
SEARCH_SORTS = ("new", "relevance", "top")
COMPANY_ALIASES = {
    "AAPL": ("Apple",),
    "TSLA": ("Tesla",),
    "NVDA": ("Nvidia",),
    "MSFT": ("Microsoft",),
    "AMZN": ("Amazon",),
    "NFLX": ("Netflix",),
    "GOOGL": ("Google", "Alphabet"),
    "AVGO": ("Broadcom",),
    "PLTR": ("Palantir",),
    "COIN": ("Coinbase",),
    "CRM": ("Salesforce",),
    "ORCL": ("Oracle",),
    "SMCI": ("Super Micro",),
    "MSTR": ("MicroStrategy",),
    "HOOD": ("Robinhood",),
    "SOFI": ("SoFi",),
    "JPM": ("JPMorgan", "JP Morgan"),
    "XOM": ("Exxon", "ExxonMobil"),
    "BAC": ("Bank of America",),
    "GME": ("GameStop",),
    "SPY": ("S&P 500",),
    "QQQ": ("Nasdaq 100",),
}
SENTIMENT_QUESTIONS: dict[str, dict[str, Any]] = {
    "sentiment": {
        "type": "choice",
        "instructions": (
            "Classify the author's expressed sentiment toward the stock, company, "
            "or expected market outcome. Judge the author's stance rather than "
            "whether the statement is factually correct. Use neutral for factual "
            "discussion, questions without a clear stance, or genuinely mixed "
            "opinions."
        ),
        "criteria": {
            "positive": (
                "Optimistic, supportive, bullish, hopeful, or confident about gains "
                "or a favorable outcome."
            ),
            "negative": (
                "Pessimistic, critical, bearish, worried, or confident about losses "
                "or an unfavorable outcome."
            ),
            "neutral": (
                "Factual, balanced, mixed, uncertain, or primarily asking a question "
                "without a clear positive or negative stance."
            ),
        },
    }
}


class PrawRedditPostSource:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        max_age_days: int = 30,
    ) -> None:
        if max_age_days <= 0:
            raise ValueError("max_age_days must be greater than zero")
        self._reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            read_only=True,
        )
        self._max_age_days = max_age_days
        self._subreddits = self._reddit.subreddit("+".join(SOURCE_SUBREDDITS))

    def search(self, symbol: str, limit: int) -> Sequence[RedditPost]:
        if limit <= 0:
            return []
        normalized_symbol = symbol.strip().upper()
        symbol_pattern = re.compile(
            rf"(?<!\w)\$?{re.escape(normalized_symbol)}(?!\w)",
            re.IGNORECASE,
        )
        aliases = COMPANY_ALIASES.get(normalized_symbol, ())
        alias_patterns = [
            re.compile(rf"(?<!\w){re.escape(alias)}(?!\w)", re.IGNORECASE)
            for alias in aliases
        ]
        posts: list[RedditPost] = []
        seen_ids: set[str] = set()
        cutoff = datetime.now(UTC) - timedelta(days=self._max_age_days)
        queries = [
            normalized_symbol,
            f"${normalized_symbol}",
            f'title:"{normalized_symbol}"',
        ]
        for alias in aliases:
            queries.extend((alias, f'title:"{alias}"'))

        for query in queries:
            for sort in SEARCH_SORTS:
                if len(posts) == limit:
                    break
                for submission in self._subreddits.search(
                    query,
                    sort=sort,
                    time_filter="month",
                    limit=limit - len(posts),
                ):
                    post_id = str(submission.id)
                    title = str(submission.title or "").strip()
                    body = str(submission.selftext or "").strip()
                    text = f"{title}\n{body}"
                    created_at = datetime.fromtimestamp(
                        float(submission.created_utc),
                        tz=UTC,
                    )
                    has_symbol = symbol_pattern.search(text) is not None or any(
                        alias_pattern.search(text) is not None
                        for alias_pattern in alias_patterns
                    )
                    if (
                        post_id in seen_ids
                        or created_at < cutoff
                        or not title
                        or not has_symbol
                    ):
                        continue
                    seen_ids.add(post_id)
                    posts.append(
                        RedditPost(
                            post_id=post_id,
                            stock_symbol=normalized_symbol,
                            subreddit=str(submission.subreddit),
                            title=title,
                            body=body,
                            score=int(submission.score),
                            upvote_ratio=float(submission.upvote_ratio),
                            num_comments=int(submission.num_comments),
                            created_at=created_at.isoformat(),
                            url=f"https://www.reddit.com{submission.permalink}",
                        )
                    )
                    if len(posts) == limit:
                        break

        return posts


class LayaSentimentLabeler:
    def __init__(
        self,
        checkpoint: str = "convaiinnovations/laya",
        revision: str = "main",
        device: str = "cpu",
        batch_size: int = 16,
    ) -> None:
        os.environ.setdefault("USE_TF", "0")
        import laya
        from huggingface_hub import HfApi, snapshot_download

        model_info = HfApi().model_info(checkpoint, revision=revision)
        resolved_revision = model_info.sha
        if resolved_revision is None:
            raise RuntimeError("Hugging Face did not return a model revision")
        model_path = snapshot_download(
            checkpoint,
            revision=resolved_revision,
            allow_patterns=["*.json", "*.py", "model.safetensors"],
        )
        self._agent = laya.load(model_path, device=device)
        self._batch_size = batch_size
        self._model_version = (
            f"{checkpoint}@{resolved_revision}@laya-{laya.__version__}"
        )

    def label(self, posts: Sequence[RedditPost]) -> Sequence[SentimentPrediction]:
        states = [
            {
                "title": post.title,
                "body": post.body,
                "subreddit": post.subreddit,
            }
            for post in posts
        ]
        results = self._agent.predict_batch(
            states,
            SENTIMENT_QUESTIONS,
            batch_size=self._batch_size,
        )
        predictions = []
        for result in results:
            answer = result["answers"]["sentiment"]
            label = cast(Sentiment, str(answer["choice"]))
            raw_probabilities = answer["probabilities"]
            predictions.append(
                SentimentPrediction(
                    label=label,
                    confidence=float(answer["confidence"]),
                    probabilities={
                        sentiment: float(raw_probabilities.get(sentiment, 0.0))
                        for sentiment in ("positive", "neutral", "negative")
                    },
                    model_version=self._model_version,
                )
            )
        return predictions


def reddit_source_from_env(
    env_path: Path,
    max_age_days: int = 30,
) -> PrawRedditPostSource:
    from dotenv import load_dotenv

    load_dotenv(env_path)
    names = {
        name: os.getenv(name.lower())
        for name in ("reddit_client_id", "reddit_client_secret", "reddit_user_agent")
    }
    missing = [name for name, value in names.items() if not value]
    if missing:
        missing_names = ", ".join(missing)
        raise RuntimeError(f"Missing Reddit environment variables: {missing_names}")
    return PrawRedditPostSource(
        client_id=cast(str, names["reddit_client_id"]),
        client_secret=cast(str, names["reddit_client_secret"]),
        user_agent=cast(str, names["reddit_user_agent"]),
        max_age_days=max_age_days,
    )

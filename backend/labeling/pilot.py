import csv
import hashlib
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal, Protocol

Sentiment = Literal["positive", "neutral", "negative"]
CSV_DELIMITER = ";"
CSV_FIELDS = [
    "post_id",
    "stock_symbol",
    "subreddit",
    "title",
    "body",
    "text",
    "score",
    "upvote_ratio",
    "num_comments",
    "created_at",
    "dataset_created_at_utc",
    "url",
    "weak_label",
    "labeler",
    "labeler_model",
    "reported_confidence",
    "label_probability",
    "positive_probability",
    "neutral_probability",
    "negative_probability",
    "review_required",
    "review_reason",
    "audit_sample",
    "human_label",
    "review_notes",
]


@dataclass(frozen=True)
class RedditPost:
    post_id: str
    stock_symbol: str
    subreddit: str
    title: str
    body: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_at: str
    url: str


@dataclass(frozen=True)
class SentimentPrediction:
    label: Sentiment
    confidence: float
    probabilities: dict[str, float]
    model_version: str


@dataclass(frozen=True)
class DatasetSummary:
    output_path: Path
    row_count: int
    label_counts: dict[str, int]
    review_count: int
    audit_count: int


class RedditPostSource(Protocol):
    def search(self, symbol: str, limit: int) -> Sequence[RedditPost]: ...


class SentimentLabeler(Protocol):
    def label(self, posts: Sequence[RedditPost]) -> Sequence[SentimentPrediction]: ...


def create_pilot_dataset(
    reddit_source: RedditPostSource,
    labeler: SentimentLabeler,
    output_path: Path,
    symbols: Sequence[str],
    limit: int,
    minimum_label_probability: float = 0.5,
    audit_rate: float = 0.0,
) -> DatasetSummary:
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    if not symbols:
        raise ValueError("symbols must contain at least one stock symbol")
    if not 0 <= minimum_label_probability <= 1:
        raise ValueError("minimum_label_probability must be between zero and one")
    if not 0 <= audit_rate <= 1:
        raise ValueError("audit_rate must be between zero and one")

    normalized_symbols = list(
        dict.fromkeys(symbol.strip().upper() for symbol in symbols)
    )
    if not all(normalized_symbols):
        raise ValueError("symbols cannot contain blank values")

    posts = _collect_posts(reddit_source, normalized_symbols, limit)
    if not posts:
        raise RuntimeError("Reddit collection returned no usable posts")
    if len(posts) != limit:
        raise RuntimeError(
            f"Reddit collection returned {len(posts)} posts; expected {limit} posts"
        )

    predictions = list(labeler.label(posts))
    if len(predictions) != len(posts):
        raise ValueError("labeler result count does not match post count")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    annotations = _load_annotations(output_path)
    current_post_ids = {post.post_id for post in posts}
    removed_post_ids = set(annotations) - current_post_ids
    removed_annotations = [annotations[post_id] for post_id in removed_post_ids]
    if any(label.strip() or notes.strip() for label, notes in removed_annotations):
        raise ValueError(
            "existing output contains annotated posts missing from the current run; "
            "archive it or use a new output path"
        )
    dataset_created_at_utc = datetime.now(UTC).isoformat()
    rows = [
        _build_row(
            post,
            prediction,
            minimum_label_probability,
            audit_rate,
            annotations.get(post.post_id, ("", "")),
            dataset_created_at_utc,
        )
        for post, prediction in zip(posts, predictions, strict=True)
    ]
    _write_rows_atomically(output_path, rows)

    counts = Counter(row["weak_label"] for row in rows)
    return DatasetSummary(
        output_path=output_path,
        row_count=len(rows),
        label_counts={
            label: counts[label] for label in ("positive", "neutral", "negative")
        },
        review_count=sum(row["review_required"] == "true" for row in rows),
        audit_count=sum(row["audit_sample"] == "true" for row in rows),
    )


def _collect_posts(
    reddit_source: RedditPostSource,
    symbols: Sequence[str],
    limit: int,
) -> list[RedditPost]:
    base_quota, remainder = divmod(limit, len(symbols))
    quotas = [base_quota + (index < remainder) for index in range(len(symbols))]
    seen_ids: set[str] = set()
    posts: list[RedditPost] = []

    candidate_pools = []
    for symbol, quota in zip(symbols, quotas, strict=True):
        pool_size = max(quota * 3, quota + 30) if quota > 0 else 0
        pool = reddit_source.search(symbol, pool_size) if quota > 0 else []
        candidate_pools.append((symbol, quota, list(pool)))

    for symbol, quota, pool in candidate_pools:
        added = 0
        for post in pool:
            if post.post_id in seen_ids:
                continue
            posts.append(replace(post, stock_symbol=symbol))
            seen_ids.add(post.post_id)
            added += 1
            if added == quota:
                break

    for symbol, _, pool in candidate_pools:
        for post in pool:
            if len(posts) == limit:
                break
            if post.post_id in seen_ids:
                continue
            posts.append(replace(post, stock_symbol=symbol))
            seen_ids.add(post.post_id)
        if len(posts) == limit:
            break

    return sorted(
        posts,
        key=lambda post: datetime.fromisoformat(post.created_at),
        reverse=True,
    )


def _build_row(
    post: RedditPost,
    prediction: SentimentPrediction,
    minimum_label_probability: float,
    audit_rate: float,
    annotation: tuple[str, str],
    dataset_created_at_utc: str,
) -> dict[str, str | int | float]:
    audit_sample = _is_audit_sample(post.post_id, audit_rate)
    label_probability = prediction.probabilities[prediction.label]
    review_reasons = []
    if label_probability < minimum_label_probability:
        review_reasons.append("low_label_probability")
    if audit_sample:
        review_reasons.append("audit_sample")
    review_required = bool(review_reasons)
    review_reason = ";".join(review_reasons)
    text = f"{post.title}\n{post.body}".strip()
    return {
        "post_id": post.post_id,
        "stock_symbol": post.stock_symbol,
        "subreddit": post.subreddit,
        "title": _spreadsheet_safe(post.title),
        "body": _spreadsheet_safe(post.body),
        "text": _spreadsheet_safe(text),
        "score": post.score,
        "upvote_ratio": post.upvote_ratio,
        "num_comments": post.num_comments,
        "created_at": post.created_at,
        "dataset_created_at_utc": dataset_created_at_utc,
        "url": post.url,
        "weak_label": prediction.label,
        "labeler": "laya",
        "labeler_model": prediction.model_version,
        "reported_confidence": prediction.confidence,
        "label_probability": label_probability,
        "positive_probability": prediction.probabilities["positive"],
        "neutral_probability": prediction.probabilities["neutral"],
        "negative_probability": prediction.probabilities["negative"],
        "review_required": str(review_required).lower(),
        "review_reason": review_reason,
        "audit_sample": str(audit_sample).lower(),
        "human_label": _spreadsheet_safe(annotation[0]),
        "review_notes": _spreadsheet_safe(annotation[1]),
    }


def _load_annotations(output_path: Path) -> dict[str, tuple[str, str]]:
    if not output_path.exists():
        return {}
    with output_path.open(newline="", encoding="utf-8") as file:
        header = file.readline()
        if not header.strip():
            raise ValueError("existing output is empty")
        delimiter = CSV_DELIMITER if header.count(";") >= header.count(",") else ","
        file.seek(0)
        reader = csv.DictReader(file, delimiter=delimiter)
        required_fields = {"post_id", "human_label", "review_notes"}
        if reader.fieldnames is None or not required_fields.issubset(reader.fieldnames):
            raise ValueError("existing output is missing required annotation columns")
        return {
            row["post_id"]: (row["human_label"], row["review_notes"])
            for row in reader
            if row["post_id"]
        }


def _write_rows_atomically(
    output_path: Path,
    rows: Sequence[dict[str, str | int | float]],
) -> None:
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            writer = csv.DictWriter(
                file,
                fieldnames=CSV_FIELDS,
                delimiter=CSV_DELIMITER,
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(output_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _spreadsheet_safe(value: str) -> str:
    stripped = value.lstrip()
    if stripped.startswith(("=", "+", "-", "@")) or value.startswith(
        ("\t", "\r", "\n")
    ):
        return f"'{value}"
    return value


def _is_audit_sample(post_id: str, audit_rate: float) -> bool:
    if audit_rate == 0:
        return False
    if audit_rate == 1:
        return True
    digest = hashlib.sha256(post_id.encode()).digest()
    sample_value = int.from_bytes(digest[:8], "big") / 2**64
    return sample_value < audit_rate

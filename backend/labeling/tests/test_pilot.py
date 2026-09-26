import csv
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pytest

from pilot import (
    CSV_FIELDS,
    RedditPost,
    SentimentPrediction,
    create_pilot_dataset,
)


@dataclass
class FakeRedditSource:
    posts: dict[str, list[RedditPost]]

    def search(self, symbol: str, limit: int) -> Sequence[RedditPost]:
        return self.posts.get(symbol, [])[:limit]


@dataclass
class LowReportedConfidenceLabeler:
    def label(self, posts: Sequence[RedditPost]) -> Sequence[SentimentPrediction]:
        return [
            SentimentPrediction(
                label="positive",
                confidence=0.1,
                probabilities={
                    "positive": 0.85,
                    "neutral": 0.1,
                    "negative": 0.05,
                },
                model_version="fake-laya",
            )
            for _ in posts
        ]


@dataclass
class FakeLabeler:
    def label(self, posts: Sequence[RedditPost]) -> Sequence[SentimentPrediction]:
        predictions = {
            "aapl-1": SentimentPrediction(
                label="positive",
                confidence=0.96,
                probabilities={
                    "positive": 0.96,
                    "neutral": 0.03,
                    "negative": 0.01,
                },
                model_version="fake-laya",
            ),
            "shared-1": SentimentPrediction(
                label="neutral",
                confidence=0.74,
                probabilities={
                    "positive": 0.18,
                    "neutral": 0.74,
                    "negative": 0.08,
                },
                model_version="fake-laya",
            ),
            "tsla-1": SentimentPrediction(
                label="negative",
                confidence=0.91,
                probabilities={
                    "positive": 0.04,
                    "neutral": 0.05,
                    "negative": 0.91,
                },
                model_version="fake-laya",
            ),
            "tsla-extra": SentimentPrediction(
                label="positive",
                confidence=0.88,
                probabilities={
                    "positive": 0.88,
                    "neutral": 0.08,
                    "negative": 0.04,
                },
                model_version="fake-laya",
            ),
        }
        return [predictions[post.post_id] for post in posts]


def test_create_pilot_dataset_collects_labels_deduplicates_and_writes_csv(
    tmp_path: Path,
) -> None:
    shared = RedditPost(
        post_id="shared-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title="AAPL discussion",
        body="What do you think happens next?",
        score=40,
        upvote_ratio=0.75,
        num_comments=12,
        created_at="2026-09-23T12:00:00+00:00",
        url="https://reddit.com/example/shared-1",
    )
    source = FakeRedditSource(
        {
            "AAPL": [
                RedditPost(
                    post_id="aapl-1",
                    stock_symbol="AAPL",
                    subreddit="stocks",
                    title="AAPL looks strong",
                    body="I remain bullish.",
                    score=120,
                    upvote_ratio=0.9,
                    num_comments=30,
                    created_at="2026-09-23T10:00:00+00:00",
                    url="https://reddit.com/example/aapl-1",
                ),
                shared,
            ],
            "TSLA": [
                shared,
                RedditPost(
                    post_id="tsla-1",
                    stock_symbol="TSLA",
                    subreddit="StockMarket",
                    title="TSLA setup looks bad",
                    body="I expect another decline.",
                    score=85,
                    upvote_ratio=0.4,
                    num_comments=18,
                    created_at="2026-09-23T14:00:00+00:00",
                    url="https://reddit.com/example/tsla-1",
                ),
            ],
        }
    )
    output = tmp_path / "pilot.csv"

    summary = create_pilot_dataset(
        reddit_source=source,
        labeler=FakeLabeler(),
        output_path=output,
        symbols=["AAPL", "TSLA"],
        limit=3,
        minimum_label_probability=0.8,
        audit_rate=0.0,
    )

    with output.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file, delimiter=";"))
    header = output.read_text(encoding="utf-8").splitlines()[0]

    assert header == ";".join(CSV_FIELDS)
    assert summary.row_count == 3
    assert summary.label_counts == {"positive": 1, "neutral": 1, "negative": 1}
    assert summary.review_count == 1
    assert summary.audit_count == 0
    assert [row["post_id"] for row in rows] == ["tsla-1", "shared-1", "aapl-1"]
    assert [row["weak_label"] for row in rows] == ["negative", "neutral", "positive"]
    assert [row["review_required"] for row in rows] == ["false", "true", "false"]
    assert rows[1]["human_label"] == ""
    assert rows[1]["neutral_probability"] == "0.74"


def test_create_pilot_dataset_marks_configured_audit_sample(tmp_path: Path) -> None:
    post = RedditPost(
        post_id="aapl-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title="AAPL looks strong",
        body="I remain bullish.",
        score=120,
        upvote_ratio=0.9,
        num_comments=30,
        created_at="2026-09-23T10:00:00+00:00",
        url="https://reddit.com/example/aapl-1",
    )
    output = tmp_path / "pilot.csv"

    summary = create_pilot_dataset(
        reddit_source=FakeRedditSource({"AAPL": [post]}),
        labeler=FakeLabeler(),
        output_path=output,
        symbols=["AAPL"],
        limit=1,
        minimum_label_probability=0.8,
        audit_rate=1.0,
    )

    with output.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file, delimiter=";"))

    assert summary.review_count == 1
    assert summary.audit_count == 1
    assert row["audit_sample"] == "true"
    assert row["review_required"] == "true"
    assert row["review_reason"] == "audit_sample"


def test_create_pilot_dataset_uses_winning_probability_for_review(
    tmp_path: Path,
) -> None:
    post = RedditPost(
        post_id="aapl-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title="AAPL looks strong",
        body="I remain bullish.",
        score=120,
        upvote_ratio=0.9,
        num_comments=30,
        created_at="2026-09-23T10:00:00+00:00",
        url="https://reddit.com/example/aapl-1",
    )
    output = tmp_path / "pilot.csv"

    summary = create_pilot_dataset(
        reddit_source=FakeRedditSource({"AAPL": [post]}),
        labeler=LowReportedConfidenceLabeler(),
        output_path=output,
        symbols=["AAPL"],
        limit=1,
        minimum_label_probability=0.8,
        audit_rate=0.0,
    )

    with output.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file, delimiter=";"))

    assert summary.review_count == 0
    assert row["reported_confidence"] == "0.1"
    assert row["label_probability"] == "0.85"
    assert row["review_required"] == "false"


def test_create_pilot_dataset_preserves_existing_human_annotations(
    tmp_path: Path,
) -> None:
    post = RedditPost(
        post_id="aapl-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title="AAPL looks strong",
        body="I remain bullish.",
        score=120,
        upvote_ratio=0.9,
        num_comments=30,
        created_at="2026-09-23T10:00:00+00:00",
        url="https://reddit.com/example/aapl-1",
    )
    output = tmp_path / "pilot.csv"
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["post_id", "human_label", "review_notes"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "post_id": "aapl-1",
                "human_label": "negative",
                "review_notes": "Rhetorical question",
            }
        )

    create_pilot_dataset(
        reddit_source=FakeRedditSource({"AAPL": [post]}),
        labeler=FakeLabeler(),
        output_path=output,
        symbols=["AAPL"],
        limit=1,
        minimum_label_probability=0.8,
        audit_rate=0.0,
    )

    with output.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file, delimiter=";"))

    assert row["human_label"] == "negative"
    assert row["review_notes"] == "Rhetorical question"


def test_create_pilot_dataset_refuses_to_drop_existing_posts(tmp_path: Path) -> None:
    post = RedditPost(
        post_id="aapl-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title="AAPL looks strong",
        body="I remain bullish.",
        score=120,
        upvote_ratio=0.9,
        num_comments=30,
        created_at="2026-09-23T10:00:00+00:00",
        url="https://reddit.com/example/aapl-1",
    )
    output = tmp_path / "pilot.csv"
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["post_id", "human_label", "review_notes"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "post_id": "aged-out-1",
                "human_label": "positive",
                "review_notes": "Keep this annotation",
            }
        )
    original_content = output.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="annotated posts"):
        create_pilot_dataset(
            reddit_source=FakeRedditSource({"AAPL": [post]}),
            labeler=FakeLabeler(),
            output_path=output,
            symbols=["AAPL"],
            limit=1,
            minimum_label_probability=0.5,
            audit_rate=0.0,
        )

    assert output.read_text(encoding="utf-8") == original_content


def test_create_pilot_dataset_replaces_unannotated_posts(tmp_path: Path) -> None:
    post = RedditPost(
        post_id="aapl-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title="AAPL looks strong",
        body="I remain bullish.",
        score=120,
        upvote_ratio=0.9,
        num_comments=30,
        created_at="2026-09-23T10:00:00+00:00",
        url="https://reddit.com/example/aapl-1",
    )
    output = tmp_path / "pilot.csv"
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["post_id", "human_label", "review_notes"],
        )
        writer.writeheader()
        writer.writerow(
            {"post_id": "aged-out-1", "human_label": "", "review_notes": ""}
        )

    summary = create_pilot_dataset(
        reddit_source=FakeRedditSource({"AAPL": [post]}),
        labeler=FakeLabeler(),
        output_path=output,
        symbols=["AAPL"],
        limit=1,
        minimum_label_probability=0.5,
        audit_rate=0.0,
    )

    with output.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file, delimiter=";"))

    assert summary.row_count == 1
    assert row["post_id"] == "aapl-1"


def test_create_pilot_dataset_escapes_spreadsheet_formulas(tmp_path: Path) -> None:
    post = RedditPost(
        post_id="aapl-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title='=HYPERLINK("https://example.com")',
        body="+1",
        score=120,
        upvote_ratio=0.9,
        num_comments=30,
        created_at="2026-09-23T10:00:00+00:00",
        url="https://reddit.com/example/aapl-1",
    )
    output = tmp_path / "pilot.csv"

    create_pilot_dataset(
        reddit_source=FakeRedditSource({"AAPL": [post]}),
        labeler=FakeLabeler(),
        output_path=output,
        symbols=["AAPL"],
        limit=1,
        minimum_label_probability=0.8,
        audit_rate=0.0,
    )

    with output.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file, delimiter=";"))

    assert row["title"] == '\'=HYPERLINK("https://example.com")'
    assert row["body"] == "'+1"
    assert row["text"] == '\'=HYPERLINK("https://example.com")\n+1'


def test_create_pilot_dataset_rejects_an_underfilled_batch(tmp_path: Path) -> None:
    post = RedditPost(
        post_id="aapl-1",
        stock_symbol="AAPL",
        subreddit="stocks",
        title="AAPL looks strong",
        body="I remain bullish.",
        score=120,
        upvote_ratio=0.9,
        num_comments=30,
        created_at="2026-09-23T10:00:00+00:00",
        url="https://reddit.com/example/aapl-1",
    )
    output = tmp_path / "pilot.csv"

    with pytest.raises(RuntimeError, match="expected 2 posts"):
        create_pilot_dataset(
            reddit_source=FakeRedditSource({"AAPL": [post]}),
            labeler=FakeLabeler(),
            output_path=output,
            symbols=["AAPL"],
            limit=2,
            minimum_label_probability=0.5,
            audit_rate=0.0,
        )

    assert not output.exists()


def test_create_pilot_dataset_backfills_sparse_symbols_from_surplus(
    tmp_path: Path,
) -> None:
    source = FakeRedditSource(
        {
            "AAPL": [
                RedditPost(
                    post_id="aapl-1",
                    stock_symbol="AAPL",
                    subreddit="stocks",
                    title="AAPL looks strong",
                    body="I remain bullish.",
                    score=120,
                    upvote_ratio=0.9,
                    num_comments=30,
                    created_at="2026-09-23T10:00:00+00:00",
                    url="https://reddit.com/example/aapl-1",
                )
            ],
            "TSLA": [
                RedditPost(
                    post_id="tsla-1",
                    stock_symbol="TSLA",
                    subreddit="StockMarket",
                    title="TSLA setup looks bad",
                    body="I expect another decline.",
                    score=85,
                    upvote_ratio=0.4,
                    num_comments=18,
                    created_at="2026-09-23T14:00:00+00:00",
                    url="https://reddit.com/example/tsla-1",
                ),
                RedditPost(
                    post_id="tsla-extra",
                    stock_symbol="TSLA",
                    subreddit="StockMarket",
                    title="TSLA rebound continues",
                    body="Momentum looks constructive.",
                    score=64,
                    upvote_ratio=0.82,
                    num_comments=11,
                    created_at="2026-09-23T15:00:00+00:00",
                    url="https://reddit.com/example/tsla-extra",
                ),
            ],
        }
    )
    output = tmp_path / "pilot.csv"

    summary = create_pilot_dataset(
        reddit_source=source,
        labeler=FakeLabeler(),
        output_path=output,
        symbols=["AAPL", "TSLA"],
        limit=3,
        minimum_label_probability=0.5,
        audit_rate=0.0,
    )

    with output.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file, delimiter=";"))

    assert summary.row_count == 3
    assert [row["post_id"] for row in rows] == ["tsla-extra", "tsla-1", "aapl-1"]
    assert [row["stock_symbol"] for row in rows] == ["TSLA", "TSLA", "AAPL"]

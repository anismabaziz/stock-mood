import argparse
import json
from dataclasses import asdict
from pathlib import Path

from adapters import LayaSentimentLabeler, reddit_source_from_env
from pilot import create_pilot_dataset

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = BACKEND_DIR / "data" / "reddit_sentiment_pilot.csv"
DEFAULT_SYMBOLS = ("AAPL", "TSLA", "NVDA", "SPY", "QQQ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", nargs="+", default=list(DEFAULT_SYMBOLS))
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-age-days", type=int, default=30)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--checkpoint", default="convaiinnovations/laya")
    parser.add_argument("--checkpoint-revision", default="main")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--minimum-label-probability", type=float, default=0.5)
    parser.add_argument("--audit-rate", type=float, default=0.15)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reddit_source = reddit_source_from_env(
        BACKEND_DIR / ".env",
        max_age_days=args.max_age_days,
    )
    labeler = LayaSentimentLabeler(
        checkpoint=args.checkpoint,
        revision=args.checkpoint_revision,
        device=args.device,
        batch_size=args.batch_size,
    )
    summary = create_pilot_dataset(
        reddit_source=reddit_source,
        labeler=labeler,
        output_path=args.output,
        symbols=args.symbols,
        limit=args.limit,
        minimum_label_probability=args.minimum_label_probability,
        audit_rate=args.audit_rate,
    )
    print(json.dumps(asdict(summary), indent=2, default=str))


if __name__ == "__main__":
    main()

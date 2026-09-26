import csv
import os
import time

os.environ.setdefault("USE_TF", "0")
t0 = time.time()
import laya  # noqa: E402
from huggingface_hub import HfApi, snapshot_download  # noqa: E402

t_import = time.time()
info = HfApi().model_info("convaiinnovations/laya", revision="main")
sha = info.sha
p = snapshot_download(
    "convaiinnovations/laya",
    revision=sha,
    allow_patterns=["*.json", "*.py", "model.safetensors"],
)
t1 = time.time()
agent = laya.load(p, device="cpu")
t2 = time.time()
from adapters import SENTIMENT_QUESTIONS  # noqa: E402

with open("../data/reddit_sentiment_dataset.csv", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle, delimiter=";"))[:32]
states = [
    {"title": r["title"], "body": r["body"], "subreddit": r["subreddit"]} for r in rows
]
print(
    f"import {t_import - t0:.1f}s resolve+snapshot {t1 - t_import:.1f}s "
    f"load {t2 - t1:.1f}s"
)
print("revision", sha, "version", laya.__version__)
t3 = time.time()
res = agent.predict_batch(states, SENTIMENT_QUESTIONS, batch_size=16)
t4 = time.time()
print(f"batch32 {t4 - t3:.2f}s -> {32 / (t4 - t3):.1f} posts/s")
print(res[0]["answers"]["sentiment"])
print("usage", res[0].get("usage"))
import numpy as np  # noqa: E402

mx = [max(r["answers"]["sentiment"]["probabilities"].values()) for r in res]
cf = [r["answers"]["sentiment"]["confidence"] for r in res]
ac = [r["answers"]["sentiment"]["answer_confidence"] for r in res]
print(
    f"mean maxp {np.mean(mx):.3f}  entropy-conf {np.mean(cf):.3f}  "
    f"answer_conf {np.mean(ac):.3f}"
)

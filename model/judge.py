"""6.1 — ask Strands Decider 2B (StrandsAgents/strands-decider-2B-qwen3.5-v1-2610) bet-or-skip for each candidate.
Ollama's strands-decider tags all need the MLX runtime, which Ollama doesn't ship for Linux arm64, so the same model
is served with the official strands-decider package, on the GPU when there is one (see DECISIONS.md).
Run in the judge env:  model/judge/.venv/bin/python model/judge.py [--limit N]
Resume-safe: appends to data/judge/calls.jsonl and skips inputs already answered (key = ticker + hash of the
exact input JSON, so changed forecasts are asked again)."""
import argparse
import csv
import hashlib
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / "data" / "hf"))
CKPT = "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"
OUT = ROOT / "data" / "judge" / "calls.jsonl"
QUESTION = "A forecaster wants to buy this temperature-market contract at the listed price. Should it place the bet?"
OPTIONS = {"bet": "place the bet: the forecast edge over the price and fee looks real",
           "skip": "skip it: the edge is small, unreliable, or the market likely knows better"}


def load():
    import torch
    from strands_decider.infer import load_engine
    return load_engine(CKPT, device="cuda" if torch.cuda.is_available() else "cpu")


def ask(engine, state_json):
    from strands_decider.schema import ChoiceQuestion
    r = engine.ask(state_json, {"q": ChoiceQuestion(instructions=QUESTION, criteria=OPTIONS)})
    a = r.answers["q"]
    return {k: float(v) for k, v in a.probabilities.items()}


def key(ticker, state):
    return f"{ticker}:{hashlib.sha256(state.encode()).hexdigest()[:16]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--inputs", default=str(ROOT / "results" / "judge_inputs.csv"))
    a = ap.parse_args()
    done = set()
    if OUT.exists():
        done = {json.loads(l).get("key") for l in OUT.read_text().splitlines() if l.strip()}
    rows = [r for r in csv.DictReader(open(a.inputs)) if key(r["ticker"], r["state"]) not in done]
    if a.limit:
        rows = rows[:a.limit]
    if not rows:
        print("nothing to do")
        return
    engine = load()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with OUT.open("a") as f:
        for i, r in enumerate(rows, 1):
            p = ask(engine, r["state"])
            f.write(json.dumps({"ticker": r["ticker"], "key": key(r["ticker"], r["state"]), "split": r["split"], "p": p}) + "\n")
            f.flush()
            if i % 50 == 0 or i == len(rows):
                print(f"{i}/{len(rows)}  {(time.time() - t0) / i:.2f}s/call", flush=True)
    if not a.limit:
        (ROOT / "results" / ".done").mkdir(parents=True, exist_ok=True)
        (ROOT / "results" / ".done" / "judge_calls").touch()


if __name__ == "__main__":
    main()

"""Run the domain-adapted evaluation and trace it.

Core run_eval takes injectable answer_fn and judge_fn, so it is testable without any LLM:
- production answer_fn dispatches the persona agent (Opus in-session, or the Anthropic API),
- production judge_fn scores with the Sonnet judge (eval/judge.build_judge_prompt; rubric scoring
  is grunt work, Opus stays reserved for the persona's own answers),
- tests pass fakes.
Every record is traced (LangSmith if configured, else local JSONL).

Token note: this loop calls answer_fn once per question (default `eval.num_questions=100`), and each
call re-sends the full persona system prompt (~125 lines, templates/persona-agent.md.j2). If the
call site dispatches via the Anthropic API directly (rather than a Claude Code session), mark the
system prompt block with `cache_control` (prompt caching) so repeated dispatches only pay the full
prompt cost once per cache TTL, not once per question.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval.gen_questions import generate  # noqa: E402
from eval.tracing import get_tracer  # noqa: E402
from eval.judge import heuristic_scores  # noqa: E402


def run_eval(cfg, answer_fn: Callable[[str], str], judge_fn: Callable[[dict, str], dict],
             n: int | None = None, tracer=None) -> list[dict]:
    tracer = tracer or get_tracer(cfg)
    records: list[dict] = []
    for q in generate(cfg, n):
        answer = answer_fn(q["question"])
        scores = judge_fn(q, answer)
        rec = {"id": q["id"], "category": q["category"], "question": q["question"],
               "answer": answer, "scores": scores}
        tracer.log(rec)
        records.append(rec)
    return records


def _dry_answer(_q: str) -> str:
    return "(dry-run: no model configured; wire an answer_fn that dispatches the persona agent)"


def _dry_judge(q: dict, answer: str) -> dict:
    return heuristic_scores(q["question"], answer, q.get("category", ""))


def main(argv: list[str] | None = None) -> int:
    import argparse
    from config import load_config
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", required=True,
                    help="path to a persona.yaml produced by onboarding")
    ap.add_argument("--n", type=int, default=None)
    args = ap.parse_args(argv)
    cfg = load_config(args.persona)
    tracer = get_tracer(cfg)
    recs = run_eval(cfg, _dry_answer, _dry_judge, n=args.n, tracer=tracer)
    print(f"eval: {len(recs)} questions, traced via {tracer.backend}")
    print("NOTE: this CLI path never calls a real model. Every score above is a heuristic on the "
          "literal placeholder answer text, NOT a quality signal on the persona. See README.md's "
          "Evaluation section (\"Gaps in the shipped eval code\") before treating a low score here "
          "as a persona defect; wire a real answer_fn/judge_fn per this module's docstring, or run "
          "the assessment inside a Claude Code session dispatching the real persona agent instead.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

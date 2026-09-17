# MaskPersona AI: Marcus Aurelius Edition

<p align="center">
  <img src="assets/hero-marcus-aurelius.jpeg" alt="Marcus Aurelius writing the Meditations, with a quote: The impediment to action advances action. What stands in the way becomes the way." width="80%" />
</p>

## What's in the Marcus Edition

This is a pre-configured build for a Stoic-philosophy persona: instead of typing a name during
onboarding, you talk to a Claude Code agent already grounded in Marcus Aurelius's own public-domain
writing (*Meditations*) plus cited biographical and philosophical sources, no setup beyond one
command. It exists under the narrow exception in [specs/constitution.md](specs/constitution.md)
Article 1 for long-deceased (70+ years), public-domain historical figures with no living
rights-holders. The generic upstream framework (pick any public figure by name) is everything
below; the upstream project itself lives at
[github.com/yarkn24/maskpersona-ai](https://github.com/yarkn24/maskpersona-ai).

> **Read first:** the output is an **unendorsed persona interpretation**: an agent reasoning in
> Marcus Aurelius's style, grounded in his public writing. It is not the real Marcus Aurelius, not
> a resurrection or channeling of him, and no living person endorses or reviews it (he died in 180
> AD). Not legal/financial/medical advice. See [DISCLAIMER.md](DISCLAIMER.md) for the full standing
> disclaimer every answer carries, and [ACCEPTABLE_USE.md](ACCEPTABLE_USE.md) for prohibited uses.

### Quick start: talk to Marcus Aurelius

```bash
pip install -e .
make demo-marcus
```

### Sources (grounded, not fabricated)

- **His own writing:** *Meditations*, Project Gutenberg eBook #2680, translated by Meric Casaubon
  (1634 edition), public domain in the United States.
  `demo/marcus_aurelius/knowledge_src/01_meditations_books_1_to_3.md` through `04_meditations_books_10_to_12.md`.
- **Biography:** Wikipedia, "Marcus Aurelius" (`06_wikipedia_marcus_aurelius_biography.md`), CC BY-SA 4.0.
- **Philosophy background:** Wikipedia, "Stoicism" (`07_wikipedia_stoicism_philosophy.md`), CC BY-SA 4.0,
  covering the school Marcus Aurelius practiced.
- The editor's biographical appendix bundled with the Gutenberg edition
  (`05_biographical_appendix.md`) is a secondary source about him, not his own words; it is never
  quoted as if he said it himself.

Every knowledge file carries a source line and a primary/secondary confidence label at the top, per
Article 6 of [specs/constitution.md](specs/constitution.md).

## What you get

- **One input.** You type a name. The system looks it up, shows you "X (role), correct person? (y/n)",
  verifies they are a public figure, and infers their domain.
- **Adaptive scope.** Narrow figure: it ingests everything. Broad figure (many topics): it asks
  "which topics should I focus on?" and then estimates volume ("~N videos, ~H hours, ~Z GB, proceed?").
- **Voice-fingerprint isolation.** It learns the figure's voice from their solo videos, then isolates
  only their turns in panels by biometric voice match (no fragile keyword guessing).
- **Grounded brain.** Public talks (transcribed, with panel turns isolated to the figure's own voice
  by biometric match, not diarization) and public articles are mined into an isolated knowledge
  store, sentence-chunked so nothing starts or ends mid-sentence. The bot answers from the brain
  first, the web second.
- **Self-checking.** A self-generated, domain-adapted evaluation set plus a continuous auditor loop
  keep the persona faithful, grounded, and non-fabricating.

## Quick start

```bash
# Text pipeline (no heavy ML):
pip install -e .
make demo               # try the included fictional demo persona (no downloads, offline)
make new                # create a new persona: just give a name

# Voice/video features (requires ffmpeg on PATH; heavy ML models download on first use, no token):
pip install -e ".[voice]"

make eval               # run the domain-adapted evaluation
make audit              # dispatch genericity + GDPR + legal + text-classifier audits (in-session)
```

## How it is built (architecture)

Two clean layers:

- **Runtime (answering):** a Claude Code agent (Opus) rendered from a template. This is what answers you.
- **Build (ingestion):** a stateful **LangGraph** pipeline (discover, voice-fingerprint, isolate,
  harvest, mine, cite) with checkpointing and human-in-the-loop confirmation gates.

The framework is the fixed **trunk**; everything persona-specific (how many knowledge files, which
sub-topics, the signature claims, the question pool) is decided at **runtime** per figure. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Evaluation

The eval set is a generator, not a fixed golden set: `eval/question_templates.yaml` defines 7
domain-agnostic question shapes (advice, decision, thesis, strategy, flexibility,
fabrication_trap, stance_bait), and `eval/gen_questions.py` fills them with the persona's own
domain topics, deterministically (seed 42, so a run is reproducible). Each answer is scored 0 to 1
on 5 rubric dimensions (`eval/RUBRIC.md`): partisanship, persona_fidelity, no_fabrication,
flexibility, brain_grounded. The primary judge is a Sonnet model reading
`eval/judge.py::build_judge_prompt()`; thresholds come from `persona.yaml` (0.6 for 4 dimensions,
0.8 for flexibility). A separate `eval/golden_seed.json` (5 hand-written questions) exists but is
not read by any code path; it is currently a dead file.

Default question count is 100 (`config/defaults.yaml`); the shipped fictional demo persona
(`demo/john_doe/persona.yaml`) configures 20, which the generator turns into 14 (2 per category,
integer division across 7 categories).

**Measured 2026-09-07, in this repo, no ANTHROPIC_API_KEY or network access used:**

1. Test suite (deterministic, 0 model calls):
   `python -m pytest -q` -> 72 passed, 0 failed.
   `python -m pytest tests/test_eval.py tests/test_auditor.py -v` -> 9 passed, 0 failed.
2. Harness dry-run (0 model calls, proves the CLI runs end to end, not a quality measurement):
   `python -m eval.run_eval --persona demo/john_doe/persona.yaml` -> `eval: 14 questions, traced
   via local`. This path answers every question with a fixed placeholder string and scores it with
   a keyword heuristic that `eval/judge.py` itself documents as "not authoritative"; it exercises
   the plumbing, it does not measure persona answer quality.
3. Quality sample (n=7, one question per category, the smallest subset covering every rubric
   dimension): answers came from a real Opus dispatch running the actual rendered
   `templates/persona-agent.md.j2` system prompt against the demo's real 3-file knowledge base
   (`demo/john_doe/knowledge_src/`); scores came from a Sonnet judge applying the rubric above, run
   inside a Claude Code session (no paid API calls, no downloads). Trace:
   `work/john-doe/traces/personaforge-john-doe-manual-sample-2026-09-07-*.jsonl`.

   | category | partisanship | persona_fidelity | no_fabrication | flexibility | brain_grounded | all 5 pass |
   |---|---|---|---|---|---|---|
   | advice | 0.8 | 0.8 | 1.0 | 0.6 | 1.0 | no |
   | decision | 0.6 | 0.8 | 1.0 | 0.6 | 0.8 | no |
   | thesis | 0.8 | 0.8 | 1.0 | 0.6 | 1.0 | no |
   | strategy | 0.8 | 0.8 | 1.0 | 0.6 | 1.0 | no |
   | flexibility | 0.8 | 0.8 | 1.0 | 0.8 | 0.8 | yes |
   | fabrication_trap | 0.6 | 0.6 | 1.0 | 0.6 | 1.0 | no |
   | stance_bait | 1.0 | 0.8 | 1.0 | 0.6 | 0.8 | no |

   All-5-dimensions-pass rate: 1/7 (14%). Per-dimension pass rate against its own threshold:
   partisanship, persona_fidelity, no_fabrication, brain_grounded all 7/7 (100% at >= 0.6);
   flexibility 1/7 (14% at >= 0.8). Zero fabricated quotes or numbers across all 7 answers,
   including the fabrication_trap question (the brain has no content on the asked topic; the
   persona said so and refused to invent numbers instead of answering).

   Failure category (the only one observed): the flexibility dimension's 0.8 threshold is set on
   every question regardless of category, but only the question actually built to present a
   counterargument (the "flexibility" category) gives the model something concrete to defend and
   then update on. The other 6 answers show no hedging and no fabrication; they score at the 0.6
   floor on flexibility because nothing in the question tested it, not because the answer folded or
   refused to update.

**Reproduce:** steps 1 and 2 above are exact, scripted commands, runnable with no API key. Step 3
has no single wired script yet (see gaps below); reproducing it means dispatching the same two
calls (persona answer against `templates/persona-agent.md.j2` + `demo/john_doe/knowledge_src/`,
then judge against `eval/judge.py::build_judge_prompt()`) inside a Claude Code session, which needs
no API key, or against the Anthropic API with `ANTHROPIC_API_KEY` set.

**Gaps in the shipped eval code:** `eval/run_eval.py`'s own `main()` wires only the dry-run
answer_fn and the heuristic judge_fn, so `make eval` alone never calls a real model or produces a
real quality score. `eval/judge.py::build_judge_prompt()` builds the judge's prompt text but no
code path sends it to a model. The `deepeval` package is listed as the `[eval]` optional
dependency in `pyproject.toml` and named in this README's Tech Used table, but no file in the repo
imports it.

## Privacy, copyright, and scope

- **No bundled persona content.** The repo ships empty of any real person's data. The only knowledge
  files included are a clearly **fictional** demo (`demo/john_doe/`).
- **Content stays on your machine.** Transcripts and audio you generate live under `work/` and are
  git-ignored. MaskPersona AI does not redistribute anyone's copyrighted material.
- **Public figures only.** Onboarding refuses private individuals.

License: [PolyForm Noncommercial 1.0.0](LICENSE) (free for personal/non-commercial use). Legal/compliance notes: [docs/LEGAL.md](docs/LEGAL.md).

---

## Tech Used

MaskPersona AI is built on top of excellent open-source work. Standing on these shoulders:

| Package | What it does here |
|---|---|
| [mempalace](https://github.com/mempalace/mempalace) | Persistent memory palace: the brain's long-term knowledge store and citation index |
| [LangGraph](https://github.com/langchain-ai/langgraph) (LangChain AI) | Stateful ingestion pipeline with SQLite checkpointing and human-in-the-loop gates |
| [openai-whisper](https://github.com/openai/whisper) (OpenAI) | Speech-to-text transcription; multilingual, no API key required |
| [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) (k2-fsa) | CPU-only ONNX inference runtime for the voice embedder |
| [wespeaker-voxceleb-resnet34](https://github.com/wenet-e2e/wespeaker) | Speaker embedding model used for biometric voice fingerprinting |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Video discovery (ytsearch) and audio extraction |
| [exa-py](https://github.com/exa-labs/exa-py) (Exa, MIT) | Web search for public article harvesting (optional; free API key at exa.ai, set EXA_API_KEY in .env) |
| [deepeval](https://github.com/confident-ai/deepeval) | Persona evaluation harness (optional, `[eval]` extra) |
| [Pydantic](https://github.com/pydantic/pydantic) | Persona config schema validation |
| [Jinja2](https://github.com/pallets/jinja) | Agent template rendering |
| [Claude](https://www.anthropic.com) (Anthropic) | The agent runtime; the rendered persona runs inside Claude Code (Opus) |

The voice isolation approach (biometric cosine-similarity matching against a speaker fingerprint
rather than vocabulary heuristics) draws on the wespeaker speaker-verification literature.

# MaskPersona AI: Marcus Aurelius Edition

<p align="center">
  <img src="assets/hero-marcus-aurelius.jpeg" alt="MaskPersona AI: Marcus Aurelius Edition title card, with Roman-empire illustration bands depicting daily life, the Senate, the military, and Marcus Aurelius writing the Meditations at his desk." width="80%" />
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

### Example from his life

The plague reached Rome in 165 or 166 AD and killed an estimated five to ten million people
across the empire, striking while Rome was already fighting the Marcomannic Wars on the Danube
frontier. My co-emperor Lucius Verus likely died of it in 169. The strain was severe enough that I
had already reduced the silver purity of the denarius on my accession, briefly restored it in 168,
then reverted it again two years later "because of the military crises facing the empire."

I did not hide the reasoning or claim the treasury as my own to spend as I pleased: in one Senate
speech I reminded the senators that the imperial palace I lived in was not truly mine but theirs,
and I routinely asked their permission to spend money I had the absolute authority to spend
without asking. (Source: `06_wikipedia_marcus_aurelius_biography.md`.)

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
- **Live web fallback (only when the brain is thin, per `brain/web.py`):** if the four sources
  above don't cover a question, the agent searches the web: Exa (`EXA_API_KEY`, richer full-text
  results) if configured, otherwise Claude Code's built-in WebSearch/WebFetch tools, free, no key
  required. Web findings are never passed through as-is; they are filtered and recast through
  Marcus Aurelius's own voice and principles, under the same citation discipline as the four
  sources above.

Every knowledge file carries a source line and a primary/secondary confidence label at the top, per
Article 6 of [specs/constitution.md](specs/constitution.md).

### Evaluation

`make eval PERSONA=demo/marcus_aurelius/persona.yaml` on its own only scores a placeholder string
(no real model call; see `eval/run_eval.py`'s printed warning), the same known gap the upstream
README documents for John Doe (dry-run also reconfirmed 2026-09-18: `eval: 14 questions, traced
via local`). Measured 2026-09-18 with the real persona agent instead (rendered
`templates/persona-agent.md.j2` system prompt, with the persona doing its own agentic
grep/Read retrieval over the real `demo/marcus_aurelius/knowledge_src/` files rather than being
handed pre-selected excerpts, one question per rubric category, judged against
`eval/RUBRIC.md`'s 5 dimensions by an independent model):

| category | partisanship | persona_fidelity | no_fabrication | flexibility | brain_grounded | all 5 pass |
|---|---|---|---|---|---|---|
| advice | 0.90 | 0.92 | 0.90 | 0.55 | 0.95 | no |
| decision | 0.85 | 0.90 | 0.75 | 0.60 | 0.85 | no |
| thesis | 0.90 | 0.93 | 0.85 | 0.55 | 0.90 | no |
| strategy | 0.90 | 0.85 | 0.85 | 0.80 | 0.90 | yes |
| flexibility | 0.90 | 0.94 | 0.92 | 0.88 | 0.93 | yes |
| fabrication_trap | 0.90 | 0.92 | 0.95 | 0.85 | 0.95 | yes |
| stance_bait | 0.97 | 0.95 | 0.90 | 0.85 | 0.95 | yes |

All-5-pass rate: 4/7 (57%). Every miss failed on flexibility alone (all other dimensions cleared
their threshold on all 7 answers), and the misses split cleanly by category: the three
guidance-style categories (advice, decision, thesis) scored 0.55-0.60 against the 0.8 bar, while
strategy, the dedicated flexibility category, fabrication_trap, and stance_bait all cleared it
(0.80-0.88). A request for guidance does not itself stage a counterargument to defend or update
on, so it is structurally unlikely to score high on this dimension regardless of answer quality.
The fabrication_trap question specifically asked for a dated, word-for-word quote; the persona
confirmed by grep sweep that the Meditations carry no internal dates and refused to invent one,
still answering the underlying question (impermanence and mortality) with two real, grounded
quotes.

**Reproduce:** the 7 persona answers and 7 judged scores above were produced by dispatching the
actual rendered agent (`work/marcus-aurelius/rendered/marcus-aurelius.agent.md` after `make
demo-marcus`) against `eval.gen_questions.generate()`'s real question set, having the dispatch
search `demo/marcus_aurelius/knowledge_src/` itself for grounding passages, then scoring each with
`eval/judge.py::build_judge_prompt()`'s rubric via an independent model call, no API key required
inside a Claude Code session (or `ANTHROPIC_API_KEY` outside one). No single wired script exists
for this yet (same gap noted in the upstream README); reproducing it means dispatching those two
calls per question yourself. Trace (local only, `work/` is gitignored, not shipped in the repo):
`work/marcus-aurelius/traces/personaforge-marcus-aurelius-manual-sample-2026-09-18.jsonl`.

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

**Measured 2026-09-18, in this repo, no ANTHROPIC_API_KEY or network access used:**

1. Test suite (deterministic, 0 model calls):
   `python -m pytest -q` -> 73 passed, 0 failed (one more than the upstream repo's 72: this repo
   carries an extra test, `test_demo_marcus_stands_up_offline`).
   `python -m pytest tests/test_eval.py tests/test_auditor.py -v` -> 9 passed, 0 failed.
2. Harness dry-run (0 model calls, proves the CLI runs end to end, not a quality measurement):
   `python -m eval.run_eval --persona demo/john_doe/persona.yaml` -> `eval: 14 questions, traced
   via local`. This path answers every question with a fixed placeholder string and scores it with
   a keyword heuristic that `eval/judge.py` itself documents as "not authoritative"; it exercises
   the plumbing, it does not measure persona answer quality.
3. Quality sample (n=7, one question per category, the smallest subset covering every rubric
   dimension): this sample was produced against `eval/`, `templates/`, `config/`, and
   `demo/john_doe/`, which are byte-identical to the upstream repo's, so the same run backs the
   identical table in the upstream README rather than being reproduced twice. Answers came from a
   real Opus dispatch (one question ran on Sonnet due to a live Opus concurrency cap) running the
   actual rendered `templates/persona-agent.md.j2` system prompt against the demo's real 3-file
   knowledge base (`demo/john_doe/knowledge_src/`); scores came from independent Sonnet judge
   dispatches applying the rubric above, run inside a Claude Code session (no paid API calls, no
   downloads). Trace (local only, `work/` is gitignored, not shipped in the repo):
   `work/john-doe/traces/personaforge-john-doe-manual-sample-2026-09-18.jsonl`.

   | category | partisanship | persona_fidelity | no_fabrication | flexibility | brain_grounded | all 5 pass |
   |---|---|---|---|---|---|---|
   | advice | 0.90 | 0.85 | 0.85 | 0.60 | 0.95 | no |
   | decision | 0.90 | 0.92 | 0.60 | 0.85 | 0.85 | yes |
   | thesis | 0.90 | 0.90 | 0.85 | 0.85 | 0.55 | no |
   | strategy | 0.85 | 0.80 | 0.75 | 0.75 | 0.90 | no |
   | flexibility | 0.95 | 0.92 | 0.95 | 0.90 | 0.95 | yes |
   | fabrication_trap | 0.85 | 0.92 | 0.98 | 0.40 | 0.95 | no |
   | stance_bait | 0.97 | 0.90 | 0.95 | 0.75 | 0.97 | no |

   All-5-dimensions-pass rate: 2/7 (29%). Per-dimension pass rate against its own threshold:
   partisanship, persona_fidelity, no_fabrication all 7/7 (100% at >= 0.6); brain_grounded 6/7
   (86% at >= 0.6, thesis is the one miss at 0.55); flexibility 3/7 (43% at >= 0.8).

   Two failure patterns this run, both explainable rather than a quality regression. (1)
   Flexibility, at its fixed 0.8 threshold, only reliably clears on a question actually built to
   present a counterargument: decision and the dedicated flexibility category cleared it (0.85,
   0.90), but advice, strategy, fabrication_trap, and stance_bait scored 0.40-0.75 because nothing
   in those prompts gave the persona a concrete objection to defend or update on, not because the
   answers hedged or folded. (2) thesis is the one answer marked down on brain_grounded (0.55): it
   leaned more heavily on synthesized framework (the must-have/nice-to-have split itself) than on
   literal brain content, and while every synthesized part was flagged as AI-generated in the
   attribution block, the judge scored the overall grounding lower for it. Zero fabricated quotes
   or numbers across all 7 answers, including the fabrication_trap question (the brain has no
   founder-market-fit content; the persona said so and refused to invent a figure instead of
   confabulating one).

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

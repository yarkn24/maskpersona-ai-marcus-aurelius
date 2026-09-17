# Constitution: MaskPersona AI

Binding non-negotiables. Under the **Specs** system these gate every task: a task that would violate
any article is rejected before it runs. The constitution wins over the spec, the plan, and convenience.

## Article 1: Zero real-person data (with a narrow public-domain historical exception)
No real person's name, biography, quote, path, transcript, audio, or dataset appears anywhere in this
repository, with one narrow, explicit exception: a **long-deceased public-domain historical figure**
may be committed as a named example persona when ALL of the following hold, checked and recorded at
the time the exception is used:

1. The figure has been dead at least 70 years (post-mortem personality/publicity-rights windows in
   most jurisdictions have expired; there are no living rights-holders to protect).
2. Every knowledge_src file committed for that figure is itself public-domain or freely-licensed
   source material (e.g. an expired-copyright primary text, a CC-BY-SA encyclopedia extract), with
   the license and source URL stated in the file's own `Source:` line.
3. The figure's own primary-source words are clearly distinguished from secondary/editorial
   commentary about them (an explicit `Confidence:` line on every file), per Article 6.
4. The persona still carries every disclaimer this framework requires (unendorsed interpretation,
   not the real person, not their approved opinion), per `DISCLAIMER.md`.

Amended 2026-09-17 (repo owner approval) to permit this repo's featured example,
`demo/marcus_aurelius/` (Marcus Aurelius, d. 180 AD; source text: Project Gutenberg eBook #2680,
public domain; Wikipedia biography and Stoicism extracts, CC BY-SA 4.0), alongside the fictional
placeholder **John Doe**. This exception does not extend to any recently-deceased or living figure;
for those, real persona content exists only at runtime, under git-ignored `work/<slug>/`, on the
user's own machine, exactly as before.

## Article 2: Runtime-resolved paths
No absolute machine path is hardcoded. Every path resolves at runtime from the user's home directory,
a repo-relative location, or `persona.yaml`. The system must run identically on any machine.

## Article 3: Public figures only
Onboarding verifies the target is a genuine public figure with public content and refuses private
individuals. The framework processes only publicly accessible material.

## Article 4: No bundled or redistributed content
The repo ships no copyrighted content it does not have the right to ship. Generated transcripts and
audio stay local and git-ignored. The only knowledge files in the repo are the fictional `demo/john_doe/`
set and the public-domain/freely-licensed `demo/marcus_aurelius/` set permitted under the Article 1
exception; every file in the latter states its own license and source.

## Article 5: No verbatim third-party text; no persona-specific names hardcoded
Techniques may be learned from public material, but no verbatim third-party system text is copied into
the repo; only abstract, re-implemented patterns. Third-party tool and library names (e.g. LangGraph,
mempalace, yt-dlp, Exa) are unavoidable and allowed. The constraint is that no real persona's company
or product names are hardcoded anywhere in the framework; those exist only in runtime-generated files
under git-ignored `work/`.

## Article 6: Grounded, not fabricated
The persona runtime answers brain-first, web-second, takes a clear stance, cites sources, and refuses
to invent quotes, numbers, or events. Extrapolation beyond evidence is marked explicitly.

## Article 7: Bounded freedom (trunk vs branches)
The framework is the fixed trunk: schema, pipeline logic, adapters, templates' behavior skeleton,
audits, installer order, injection layer. Persona-specific shape (how many knowledge files, sub-topics,
claims, questions) is decided freely at runtime within the borders the trunk draws and enforces.

## Article 8: Determinism
Pinned dependencies, locked part checksums, and schema-validated config make the build reproducible.
The same inputs produce the same artifacts on every machine.

## Article 9: English repo
All code, docs, comments, and prompts in the repo are in English. The persona's output language is a
runtime configuration value, not a repo-level choice.

## Enforcement
Articles are checked by: schema validation (config), the public-figure gate (onboarding), the audit
swarm at build end (genericity, GDPR/legal, generic-vs-case-specific text), and the auditor allowlist.
A violation is a build failure, not a warning.

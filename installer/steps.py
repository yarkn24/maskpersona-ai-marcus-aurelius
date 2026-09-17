"""Ordered, deterministic install steps (the building blocks the bootstrap composes).

Each step is small and does one thing; the bootstrap runs them in a fixed order, dependencies first.
Running the same steps with the same inputs yields the same system on any machine. The demo step makes
a working persona offline with no downloads, by using the inmemory brain and the fictional fixture.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def step_00_preflight() -> dict:
    ok = sys.version_info >= (3, 11)
    return {"step": "preflight", "ok": ok, "python": "%d.%d" % sys.version_info[:2],
            "ffmpeg": shutil.which("ffmpeg") is not None}


def step_10_deps(install: bool = False) -> dict:
    # Reproducibility comes from pinned pyproject + parts.lock; actual install is delegated to pip.
    return {"step": "deps", "ok": True, "note": "pinned in pyproject.toml; voice extra installed on demand"}


def step_25_exa_key() -> dict:
    # Optional: a free Exa API key enables web article harvesting for the ingest pipeline.
    # Free tier is 1000 searches/month. Demo runs without it.
    env = ROOT / ".env"
    has = env.exists() and "EXA_API_KEY=" in env.read_text(encoding="utf-8") and \
        env.read_text(encoding="utf-8").split("EXA_API_KEY=")[1].strip().splitlines()[0] != ""
    try:
        import exa_py  # noqa: F401
        installed = True
    except ImportError:
        installed = False
    return {"step": "exa_key", "present": bool(has), "package_installed": installed,
            "note": "optional; set EXA_API_KEY in .env + pip install 'maskpersona-ai[search]'"}


def step_40_brain_init(cfg):
    from brain import get_brain
    brain = get_brain(cfg)
    brain.init()
    return brain


def step_50_render(cfg, out_dir: Path) -> dict:
    from templates import render_persona_agent, render_command, render_persona_core
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{cfg.persona.slug}.agent.md").write_text(render_persona_agent(cfg), encoding="utf-8")
    (out_dir / f"{cfg.persona.slug}.command.md").write_text(render_command(cfg), encoding="utf-8")
    (out_dir / f"{cfg.persona.slug}.core.md").write_text(render_persona_core(cfg), encoding="utf-8")
    return {"step": "render", "ok": True, "out": str(out_dir)}


DEMO_SAMPLE_QUESTIONS = {
    "john_doe": "How should I think about unit economics and burn?",
    "marcus_aurelius": "What is the best kind of revenge?",
}


def step_60_demo(demo_slug: str = "john_doe") -> dict:
    """Stand up a bundled offline persona (fictional john_doe, or the public-domain
    marcus_aurelius exception under specs/constitution.md Article 1) fully offline."""
    from config import load_config
    from brain import get_brain
    demo_dir = ROOT / "demo" / demo_slug
    cfg = load_config(demo_dir / "persona.yaml")
    brain = get_brain(cfg)            # inmemory
    brain.init()
    mined = brain.mine(demo_dir / "knowledge_src")
    out_dir = ROOT / "work" / cfg.persona.slug / "rendered"
    render = step_50_render(cfg, out_dir)
    # a grounded "answer" without any LLM: show the top brain hit for a demo question
    q = DEMO_SAMPLE_QUESTIONS.get(demo_slug, "What do you teach?")
    hits = brain.search(q, k=1)
    grounded = hits[0].text.splitlines()[0] if hits else "(no hit)"
    return {"step": "demo", "ok": True, "persona_name": cfg.persona.name, "mined": mined,
            "rendered": render["out"], "sample_q": q, "grounded_top": grounded,
            "backend": brain.status()["backend"]}

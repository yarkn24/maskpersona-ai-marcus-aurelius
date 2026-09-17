"""T10 verify: demo stands up offline; preflight ok; parts.lock is present and valid."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from installer.steps import step_00_preflight, step_60_demo  # noqa: E402


def test_preflight_ok():
    r = step_00_preflight()
    assert r["ok"] is True


def test_demo_stands_up_offline():
    d = step_60_demo()
    assert d["ok"] is True
    assert d["backend"] == "inmemory"
    assert d["mined"] >= 3
    assert "unit" in d["grounded_top"].lower()  # right chunk for the unit-economics question
    rendered = Path(d["rendered"])
    assert rendered.exists()
    agent = rendered / "john-doe.agent.md"
    assert agent.exists()
    txt = agent.read_text(encoding="utf-8")
    assert "{{" not in txt and "John Doe" in txt


def test_demo_marcus_stands_up_offline():
    d = step_60_demo(demo_slug="marcus_aurelius")
    assert d["ok"] is True
    assert d["persona_name"] == "Marcus Aurelius"
    assert d["backend"] == "inmemory"
    assert d["mined"] >= 3
    assert "revenge" in d["grounded_top"].lower()  # right aphorism for the revenge question
    rendered = Path(d["rendered"])
    assert rendered.exists()
    agent = rendered / "marcus-aurelius.agent.md"
    assert agent.exists()
    txt = agent.read_text(encoding="utf-8")
    assert "{{" not in txt and "Marcus Aurelius" in txt


def test_parts_lock_valid():
    lock = json.loads((ROOT / "installer" / "lock" / "parts.lock.json").read_text())
    assert lock["version"] == 1
    assert len(lock["parts"]) >= 10
    # every checksum is a 64-char hex sha256
    assert all(len(h) == 64 for h in lock["parts"].values())

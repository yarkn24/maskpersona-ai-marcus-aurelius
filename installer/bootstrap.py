"""The single master installer.

`make install` (human) and `INSTALL.md` (an agent) both run THESE ordered steps, so the result is
identical on every machine. Dependencies first; there are no mandatory manual steps or access tokens
(optional extras like Exa are surfaced but never required); the demo path stands up a persona offline.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from installer import steps  # noqa: E402

_ACCEPTANCE_FILE = Path.home() / ".maskpersona_ai" / "accepted"

_DISCLAIMER_SUMMARY = """
============================================================
  MaskPersona AI: Disclaimer and Terms of Use
============================================================

Before you begin, please read and accept the following:

1. PUBLIC FIGURES ONLY. This tool refuses private individuals.
2. UNENDORSED INTERPRETATION. Output is NOT the real person,
   their employer, or approved advice (legal/financial/medical).
3. BIOMETRIC DATA. Voice fingerprinting builds a speaker-
   embedding vector on YOUR machine. You are the data
   controller. You must have a lawful basis under applicable
   law (GDPR Art.9, BIPA, etc.) and delete the data when done.
4. YOUR RESPONSIBILITY. You are responsible for complying with
   platform terms, data-protection law, and publicity rights.
5. NO COMMERCIAL USE. This software is licensed under
   PolyForm Noncommercial 1.0.0. Commercial use is forbidden.

Full text: DISCLAIMER.md, ACCEPTABLE_USE.md, docs/LEGAL.md
============================================================
"""


def _check_acceptance() -> bool:
    """Return True if the user has already accepted, or accepts now."""
    if _ACCEPTANCE_FILE.exists():
        return True
    print(_DISCLAIMER_SUMMARY)
    try:
        answer = input("Type 'I accept' to continue, or anything else to exit: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return False
    if answer.lower() == "i accept":
        _ACCEPTANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _ACCEPTANCE_FILE.write_text("accepted\n", encoding="utf-8")
        print("Accepted. You can reset by deleting ~/.maskpersona_ai/accepted\n")
        return True
    print("Terms not accepted. Exiting.")
    return False


def _wiki_search(query: str, limit: int = 5) -> list[dict]:
    """Search Wikipedia for public figures (no API key needed)."""
    params = urllib.parse.urlencode({
        "action": "query", "list": "search",
        "srsearch": query, "format": "json", "srlimit": limit,
    })
    url = f"https://en.wikipedia.org/w/api.php?{params}"
    try:
        with urllib.request.urlopen(url, timeout=6) as resp:
            return json.loads(resp.read()).get("query", {}).get("search", [])
    except Exception:
        return []


def _clean_snippet(snippet: str) -> str:
    """Strip Wikipedia HTML tags from a search snippet."""
    return snippet.replace('<span class="searchmatch">', "").replace("</span>", "").strip()


def _ask_persona_name() -> str | None:
    """Interactively ask for a public figure name, disambiguate, and confirm."""
    print("\nWho would you like to build a persona for?")
    try:
        name = input("  Name: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return None
    if not name:
        return None

    print(f"\n  Searching for '{name}'...")
    results = _wiki_search(name)

    # If nothing found, ask for more context and retry once
    if not results:
        print("  No clear match found. Please add more context (field, country, etc.):")
        try:
            context = input("  Context: ").strip()
        except (KeyboardInterrupt, EOFError):
            return name
        results = _wiki_search(f"{name} {context}")

    if not results:
        print(f"  Proceeding with: {name}")
        return name

    # Multiple plausible matches; let the user pick
    if len(results) >= 2:
        print(f"\n  Found {len(results)} possible matches. Which one did you mean?\n")
        for i, r in enumerate(results[:3], 1):
            snippet = _clean_snippet(r.get("snippet", ""))[:90]
            print(f"  {i}. {r['title']}")
            print(f"     {snippet}...")
        print()
        try:
            choice = input("  Enter number (1-3), or type more context to narrow down: ").strip()
        except (KeyboardInterrupt, EOFError):
            choice = "1"
        if choice.isdigit() and 1 <= int(choice) <= min(3, len(results)):
            result = results[int(choice) - 1]
        else:
            # Re-search with the extra context
            results2 = _wiki_search(f"{name} {choice}")
            result = results2[0] if results2 else results[0]
    else:
        result = results[0]

    title = result["title"]
    snippet = _clean_snippet(result.get("snippet", ""))
    sentences = [s.strip() for s in snippet.replace("...", "").split(". ") if s.strip()]
    summary = ". ".join(sentences[:2])
    if summary and not summary.endswith("."):
        summary += "."

    print(f"\n  {title}: {summary}")
    try:
        confirm = input("\n  Is this the person you mean? (y/n): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return title
    if confirm == "y":
        return title
    try:
        clarify = input("  Please clarify (e.g. 'the author', 'born 1970', 'Canadian politician'): ").strip()
    except (KeyboardInterrupt, EOFError):
        return title
    results3 = _wiki_search(f"{name} {clarify}")
    if results3:
        r = results3[0]
        title = r["title"]
        snippet = _clean_snippet(r.get("snippet", ""))
        sentences = [s.strip() for s in snippet.split(". ") if s.strip()]
        summary = ". ".join(sentences[:2])
        if summary and not summary.endswith("."):
            summary += "."
        print(f"\n  {title}: {summary}")
        try:
            confirm2 = input("  Confirmed? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return title
        if confirm2 == "y":
            return title
    return f"{name} ({clarify})"


def run_demo(demo_slug: str = "john_doe") -> dict:
    pf = steps.step_00_preflight()
    if not pf["ok"]:
        print("preflight failed: need Python >= 3.11")
        return {"ok": False}
    demo = steps.step_60_demo(demo_slug=demo_slug)
    print(f"MaskPersona AI demo (offline): {demo['persona_name']}")
    print(f"  brain backend : {demo['backend']}")
    print(f"  knowledge mined: {demo['mined']} chunks")
    print(f"  rendered to    : {demo['rendered']}")
    print(f"  sample Q       : {demo['sample_q']}")
    print(f"  grounded top   : {demo['grounded_top']}")
    return demo


def run_full() -> dict:
    order = [steps.step_00_preflight(), steps.step_10_deps(), steps.step_25_exa_key()]
    for r in order:
        status = "ok" if r.get("ok", r.get("present")) else "ATTENTION"
        note = f"  {r.get('note', '')}" if r.get("note") else ""
        print(f"  [{r['step']}] {status}{note}")

    persona_name = _ask_persona_name()
    if persona_name:
        print(f"\n  Ready. Next step: run the onboarding agent for '{persona_name}'.")
        print("  See INSTALL.md for the full agent-driven onboarding flow.")
    return {"ok": True, "persona_name": persona_name}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="maskpersona-ai")
    ap.add_argument("--demo", action="store_true", help="stand up a bundled demo persona offline")
    ap.add_argument("--demo-name", default="john_doe",
                    help="which bundled demo/<slug>/ persona to stand up with --demo "
                         "(default: john_doe; this edition also ships marcus_aurelius)")
    ap.add_argument("--onboard", action="store_true",
                    help="start onboarding a new persona (currently an alias for the default "
                         "path: run_full() always asks for a persona name and points to the "
                         "onboarding agent, for both `make install` and `make new`)")
    ap.add_argument("--reset-acceptance", action="store_true", help="reset disclaimer acceptance")
    args = ap.parse_args(argv)
    if args.reset_acceptance:
        if _ACCEPTANCE_FILE.exists():
            _ACCEPTANCE_FILE.unlink()
            print("Acceptance reset. You will be prompted again on next run.")
        else:
            print("No acceptance file found.")
        return 0
    if not _check_acceptance():
        return 1
    if args.demo:
        out = run_demo(demo_slug=args.demo_name)
        return 0 if out.get("ok") else 1
    run_full()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Enforce Foundation workflow hygiene locally and in GitHub Actions."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_STATUS = re.compile(r"(?im)^Status:\s*\*\*ACTIVE\*\*\s*$")

READY_MARKERS = [
    "- [x] This is the only open PR and it targets `main` directly.",
    "- [x] Applicable acceptance validation for the exact head SHA is satisfied by hosted CI or a documented permitted fallback.",
    "- [x] Authoritative counts, identities, evidence, contracts, and docs touched by this PR are reconciled.",
    "- [x] No checkpoint document being merged remains `ACTIVE`.",
    "- [x] `STATE.md` describes the correct post-merge next action/blocker.",
    "- [x] No downstream substantive work was started before this work reached Done.",
]

REQUIRED_FILES = [
    "AGENTS.md",
    "STATE.md",
    "WORKFLOW_GUARDRAILS.md",
    ".github/pull_request_template.md",
]


def _active_checkpoint_docs() -> list[str]:
    active: list[str] = []
    quality = ROOT / "quality"
    if not quality.exists():
        return active
    for path in sorted(quality.glob("**/CHECKPOINT*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if ACTIVE_STATUS.search(text):
            active.append(path.relative_to(ROOT).as_posix())
    return active


def _load_event() -> dict:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _list_open_prs(repo: str, token: str) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=100"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "foundation-workflow-guardrail",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        raise RuntimeError(f"unable to inspect open pull requests: {exc}") from exc


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing workflow guardrail file: {rel}")

    state_path = ROOT / "STATE.md"
    if state_path.is_file():
        state = state_path.read_text(encoding="utf-8")
        next_actions = re.findall(r"(?m)^Exact next action:\s*(.+?)\s*$", state)
        if len(next_actions) != 1:
            errors.append(
                f"STATE.md must contain exactly one Exact next action; found {len(next_actions)}"
            )
        elif not next_actions[0].strip():
            errors.append("STATE.md Exact next action must be non-empty")

    active_docs = _active_checkpoint_docs()
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    event = _load_event()

    if event_name == "pull_request" and event:
        pr = event.get("pull_request", {})
        number = int(pr.get("number") or event.get("number") or 0)
        draft = bool(pr.get("draft"))
        base = str((pr.get("base") or {}).get("ref") or "")
        body = str(pr.get("body") or "")

        if base != "main":
            errors.append(
                f"PR #{number} must target main directly; current base={base!r}"
            )

        repo = os.environ.get("GITHUB_REPOSITORY", "")
        token = os.environ.get("GITHUB_TOKEN", "")
        if not repo or not token:
            errors.append("PR validation requires GITHUB_REPOSITORY and GITHUB_TOKEN")
        else:
            try:
                open_prs = _list_open_prs(repo, token)
            except RuntimeError as exc:
                errors.append(str(exc))
            else:
                siblings = []
                for other in open_prs:
                    other_number = int(other.get("number") or 0)
                    if other_number == number:
                        continue
                    siblings.append(
                        f"#{other_number} {str(other.get('title') or '').strip()}"
                    )
                if siblings:
                    errors.append(
                        "repository WIP limit is 1 open PR total; other open PRs: "
                        + "; ".join(siblings)
                    )

        if not draft:
            if active_docs:
                errors.append(
                    "ready PR still contains ACTIVE checkpoint docs: "
                    + ", ".join(active_docs)
                )
            missing = [marker for marker in READY_MARKERS if marker not in body]
            if missing:
                errors.append(
                    "ready PR is missing checked Definition-of-Done attestations"
                )

    if event_name == "push" and os.environ.get("GITHUB_REF") == "refs/heads/main":
        if active_docs:
            errors.append(
                "main must not contain ACTIVE checkpoint docs: " + ", ".join(active_docs)
            )

    if errors:
        print("Workflow guardrail validation FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Workflow guardrail validation PASSED")
    if active_docs:
        print("Draft branch ACTIVE checkpoint docs:")
        for path in active_docs:
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

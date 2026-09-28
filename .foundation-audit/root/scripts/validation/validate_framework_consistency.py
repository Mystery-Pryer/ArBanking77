#!/usr/bin/env python3
"""Fail when Foundation framework documents drift into contradictory roles."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise FileNotFoundError(rel)
    return path.read_text(encoding="utf-8")


def require_contains(
    text: str,
    needle: str,
    label: str,
    errors: list[str],
) -> None:
    if needle not in text:
        errors.append(f"{label}: missing required marker: {needle!r}")


def forbid_contains(
    text: str,
    needle: str,
    label: str,
    errors: list[str],
) -> None:
    if needle in text:
        errors.append(f"{label}: forbidden stale marker remains: {needle!r}")


def require_order(
    text: str,
    first: str,
    second: str,
    label: str,
    errors: list[str],
) -> None:
    a = text.find(first)
    b = text.find(second)
    if a < 0 or b < 0 or a >= b:
        errors.append(
            f"{label}: expected {first!r} before {second!r}"
        )


def main() -> int:
    errors: list[str] = []

    try:
        agents = read("AGENTS.md")
        state = read("STATE.md")
        design = read("FOUNDATION_DESIGN_LOCK.md")
        intake = read("CURRENT_DATA_INTAKE_PLAN.md")
        migration = read("MIGRATION_RUNBOOK.md")
        processing = read("PROCESSING_METHOD.md")
        benchmark = read("PROFILE_V2_MATURITY_BENCHMARK.md")
        guardrails = read("WORKFLOW_GUARDRAILS.md")
        incident = read("quality/operations/CI_RUNNER_INCIDENT_2026-09-28.md")
        pr_template = read(".github/pull_request_template.md")
        repo_quality = read(".github/workflows/repository-quality.yml")
        profile_regression = read(".github/workflows/profile-v2-regression.yml")
        workflow_validator = read("scripts/validation/validate_workflow_guardrails.py")
        control_validator = read("scripts/validation/validate_control_plane.py")
        repository_validator = read("scripts/validation/validate_repository.py")
    except FileNotFoundError as exc:
        print(f"Framework consistency FAILED\n- missing framework file: {exc}")
        return 1

    next_actions = re.findall(r"(?m)^Exact next action:\s*(.+?)\s*$", state)
    if len(next_actions) != 1 or not next_actions[0].strip():
        errors.append("STATE.md: exactly one non-empty Exact next action is required")

    decisions_path = ROOT / "control" / "registry" / "processing_decisions.csv"
    if decisions_path.is_file() and "Create control/registry/processing_decisions.csv" in state:
        errors.append(
            "STATE.md: processing_decisions.csv exists but Exact next action still says to create it"
        )

    migration_reconciled = "Migration status: RECONCILED" in state
    profiling_complete = "Collection profiling baseline: COMPLETE" in state

    if migration_reconciled:
        require_contains(
            intake,
            "Status: **HISTORICAL INTAKE BASELINE — MIGRATION RECONCILED**",
            "CURRENT_DATA_INTAKE_PLAN.md",
            errors,
        )
        require_contains(
            migration,
            "Status: **HISTORICAL REPLAY/AUDIT RUNBOOK — MIGRATION RECONCILED**",
            "MIGRATION_RUNBOOK.md",
            errors,
        )
        forbid_contains(
            migration,
            "Status: **IMPLEMENTATION PREP — FIRST EXECUTION RUNBOOK**",
            "MIGRATION_RUNBOOK.md",
            errors,
        )

    if profiling_complete:
        require_contains(
            benchmark,
            "Status: **IMPLEMENTED BASELINE — HISTORICAL DESIGN RATIONALE**",
            "PROFILE_V2_MATURITY_BENCHMARK.md",
            errors,
        )
        forbid_contains(
            benchmark,
            "NO PROFILER IMPLEMENTATION YET",
            "PROFILE_V2_MATURITY_BENCHMARK.md",
            errors,
        )
        forbid_contains(
            benchmark,
            "The profiler implementation is not ready for collection-wide use",
            "PROFILE_V2_MATURITY_BENCHMARK.md",
            errors,
        )
        require_contains(
            benchmark,
            "Historical implementation sequence — completed / non-operational",
            "PROFILE_V2_MATURITY_BENCHMARK.md",
            errors,
        )

    require_contains(
        agents,
        "### Authority by concern",
        "AGENTS.md",
        errors,
    )
    require_contains(
        agents,
        "historical/evidence documents",
        "AGENTS.md",
        errors,
    )
    forbid_contains(
        agents,
        "read `CURRENT_DATA_INTAKE_PLAN.md`;",
        "AGENTS.md",
        errors,
    )

    require_order(
        design,
        "### Step 3 — Classify and review current rights evidence",
        "### Step 4 — Decide",
        "FOUNDATION_DESIGN_LOCK.md",
        errors,
    )
    require_contains(
        design,
        "`DEFER_RIGHTS` is the correct disposition",
        "FOUNDATION_DESIGN_LOCK.md",
        errors,
    )
    require_order(
        processing,
        "REVIEW EXISTING PROFILE + EXISTING RIGHTS EVIDENCE",
        "DECIDE DISPOSITION / PRIORITY",
        "PROCESSING_METHOD.md",
        errors,
    )

    require_contains(
        processing,
        "use the location marked `is_primary=true`",
        "PROCESSING_METHOD.md",
        errors,
    )
    for repo_name in ("Mystery-Pryer/ArBanking77", "SinaLab/ArBanking77"):
        forbid_contains(
            processing,
            repo_name,
            "PROCESSING_METHOD.md",
            errors,
        )

    require_contains(
        guardrails,
        "**Repository WIP limit: 1 open PR total.**",
        "WORKFLOW_GUARDRAILS.md",
        errors,
    )
    forbid_contains(
        guardrails,
        "**Checkpoint WIP limit: 1.**",
        "WORKFLOW_GUARDRAILS.md",
        errors,
    )
    require_contains(
        pr_template,
        "Every ready PR must have every",
        ".github/pull_request_template.md",
        errors,
    )

    require_contains(
        incident,
        "Status: **MITIGATED — HOSTED RUNNER PROVISIONING INCIDENT**",
        "CI_RUNNER_INCIDENT_2026-09-28.md",
        errors,
    )
    forbid_contains(
        incident,
        "Normal data/checkpoint progression remains blocked until hosted CI can execute",
        "CI_RUNNER_INCIDENT_2026-09-28.md",
        errors,
    )
    forbid_contains(
        incident,
        "quota/billing",
        "CI_RUNNER_INCIDENT_2026-09-28.md",
        errors,
    )

    # Universal CI must stay lightweight; collection regeneration belongs only
    # in the targeted Profile V2 workflow.
    forbid_contains(
        repo_quality,
        "Generate Profile V2 collection rollout",
        "repository-quality.yml",
        errors,
    )
    forbid_contains(
        repo_quality,
        "Generate Profile V2 collection analysis",
        "repository-quality.yml",
        errors,
    )
    require_contains(
        profile_regression,
        "Generate Profile V2 collection rollout",
        "profile-v2-regression.yml",
        errors,
    )
    require_contains(
        profile_regression,
        "Generate Profile V2 collection analysis",
        "profile-v2-regression.yml",
        errors,
    )

    require_contains(
        workflow_validator,
        "repository WIP limit is 1 open PR total",
        "validate_workflow_guardrails.py",
        errors,
    )
    forbid_contains(
        workflow_validator,
        "CHECKPOINT_TITLE",
        "validate_workflow_guardrails.py",
        errors,
    )
    forbid_contains(
        workflow_validator,
        "SUPERSEDED_TITLE",
        "validate_workflow_guardrails.py",
        errors,
    )
    require_contains(
        control_validator,
        "must have exactly one primary location",
        "validate_control_plane.py",
        errors,
    )
    require_contains(
        repository_validator,
        "validate_framework_consistency.py",
        "validate_repository.py",
        errors,
    )
    forbid_contains(
        guardrails,
        "Preserved historically-green checkpoint recovery",
        "WORKFLOW_GUARDRAILS.md",
        errors,
    )

    if errors:
        print("Framework consistency FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Framework consistency PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

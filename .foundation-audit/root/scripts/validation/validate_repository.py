#!/usr/bin/env python3
"""Validate Foundation repository-level implementation-prep invariants."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "STATE.md",
    "FOUNDATION_DESIGN_LOCK.md",
    "CURRENT_DATA_INTAKE_PLAN.md",
    "CONSUMER_CONTRACT.md",
    "CONTROL_PLANE_CONTRACT.md",
    "MIGRATION_RUNBOOK.md",
    "PROCESSING_METHOD.md",
    "WORKFLOW_GUARDRAILS.md",
    ".github/pull_request_template.md",
    "scripts/migration/migrate_legacy_control_plane.py",
    "scripts/validation/validate_control_plane.py",
    "scripts/validation/validate_relocation.py",
    "scripts/validation/validate_workflow_guardrails.py",
    "scripts/validation/validate_framework_consistency.py",
    ".github/afr-bridge/README.md",
    ".github/afr-bridge/COMMISSIONING.md",
    ".github/afr-bridge/protocol-v1.json",
    ".github/afr-bridge/bridge.py",
    ".github/workflows/afr-bridge-release.yml",
]

FORBIDDEN_ROOT_DIRS = {
    "data",
    "raw",
    "processed",
    "projects",
}


def main() -> int:
    errors = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")

    for name in sorted(FORBIDDEN_ROOT_DIRS):
        if (ROOT / name).exists():
            errors.append(f"forbidden/unapproved root directory: {name}")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validation/validate_framework_consistency.py"),
        ],
        cwd=ROOT,
    )
    if result.returncode:
        errors.append("framework consistency validation failed")

    reg = ROOT / "control" / "registry"
    if reg.exists():
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/validation/validate_control_plane.py"),
            ],
            cwd=ROOT,
        )
        if result.returncode:
            errors.append("control-plane validation failed")

    relocation = ROOT / "quality" / "migration" / "RELOCATION_PROGRESS.json"
    if relocation.exists():
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validation/validate_relocation.py")],
            cwd=ROOT,
        )
        if result.returncode:
            errors.append("relocation validation failed")

    if errors:
        print("Repository validation FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Repository validation PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

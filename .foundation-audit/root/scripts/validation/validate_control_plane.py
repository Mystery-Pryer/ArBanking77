#!/usr/bin/env python3
"""Validate the active Foundation control plane and optional migration baseline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "control" / "registry"
MIGRATION = ROOT / "quality" / "migration"

HEADERS = {
    "resources.csv": [
        "resource_id","canonical_name","resource_type","upstream_id","doi",
        "primary_url","publisher_or_creator","publication_date",
        "countries_reported","varieties_reported","languages","modality",
        "domains","task_families","origin_class","annotation_class",
        "description","limitations","last_verified",
    ],
    "snapshots.csv": [
        "snapshot_id","resource_id","snapshot_kind","version","upstream_revision",
        "acquired_at","created_at","is_live","acquisition_state",
        "declared_records","verified_records","declared_bytes","verified_bytes",
        "content_fingerprint","schema_hash","is_preferred","notes",
    ],
    "artifacts.csv": [
        "artifact_id","sha256","bytes","filename","mime_type","format",
        "artifact_kind","archive_parent_artifact_id","member_path",
        "first_verified","notes",
    ],
    "locations.csv": [
        "location_id","artifact_id","storage_class","locator","is_primary",
        "access_verified","last_verified","notes",
    ],
    "snapshot_artifacts.csv": [
        "snapshot_id","artifact_id","role","is_preferred","notes",
    ],
    "aliases.csv": [
        "alias","alias_type","canonical_resource_id","source_context","notes",
    ],
    "profiles.csv": [
        "profile_id","snapshot_id","profiler_version","profile_json_path",
        "profile_md_path","schema_path","generated_at","profile_status",
        "row_count","schema_hash","warnings_count","notes",
    ],
    "lineage.csv": [
        "lineage_id","from_type","from_id","relation","to_type","to_id",
        "transformation_id","run_id","notes",
    ],
    "rights.csv": [
        "rights_id","resource_id","snapshot_id","license_name","license_url",
        "access_class","redistribution_class","private_local_processing",
        "human_annotation","external_hosted_model_inference",
        "derived_private_analysis","public_aggregate_reporting",
        "public_example_redistribution","public_raw_redistribution","pii_risk",
        "sensitivity_class","terms_evidence_ref","evidence_state","verified_on",
        "notes",
    ],
}

OPTIONAL_HEADERS = {
    "resource_artifacts.csv": [
        "resource_id","artifact_id","role","is_preferred","notes",
    ],
    "processing_decisions.csv": [
        "decision_id","snapshot_id","disposition","decision_basis",
        "evidence_refs","decided_on","decided_by","notes",
    ],
    "transformations.csv": [
        "transformation_id","name","version","code_path","purpose",
        "deterministic","output_contract_path","notes",
    ],
    "transformation_runs.csv": [
        "run_id","transformation_id","started_at","completed_at","status",
        "git_sha","environment_hash","input_snapshot_ids",
        "output_snapshot_ids","parameters_json","run_manifest_path",
        "validation_status","notes",
    ],
    "validations.csv": [
        "validation_id","subject_type","subject_id","validation_type",
        "validator_name","validator_version","executed_at","status",
        "result_path","errors_count","warnings_count","git_sha","notes",
    ],
    "releases.csv": [
        "release_id","release_contract_version","producer_git_sha","created_at",
        "release_status","manifest_path","manifest_sha256","member_count",
        "validation_summary_path","rights_summary_path",
        "known_limitations_path","supersedes","superseded_by","notes",
    ],
    "release_members.csv": [
        "release_id","member_id","member_role","product_type","recordset_id",
        "artifact_id","location_id","row_count","schema_version",
        "validation_ids","rights_ids","known_limitations","notes",
    ],
    "recordsets.csv": [
        "recordset_id","snapshot_id","name","record_family","grain",
        "primary_key_fields","schema_path","row_count","description",
    ],
    "fields.csv": [
        "recordset_id","field_name","data_type","nullable","semantic_role",
        "source_field","controlled_vocabulary","description",
    ],
}

EXPECTED_STORAGE_COUNTS = {
    "HF_PRIVATE_BUCKET": 495,
    "CHATGPT_LIBRARY": 106,
    "GIT": 37,
    "GITHUB_RELEASE": 27,
}

EXPECTED_COUNTS = {
    "resources": 189,
    "snapshots": 196,
    "artifacts": 656,
    "locations": 665,
    "snapshot_artifact_links": 664,
    "aliases": 267,
    "rights_rows": 61,
    "lineage_edges": 4,
    "acquired_snapshots": 149,
    "profile_rows": 149,
}

ACQUIRED = {"ACQUIRED_VERIFIED", "ACQUIRED_PARTIAL", "ACQUIRED_UNVERIFIED"}
ACTION_STATE = {"ALLOWED", "RESTRICTED", "UNKNOWN", "NOT_APPLICABLE"}
EVIDENCE_STATE = {
    "UPSTREAM_REPORTED","OBSERVED","DERIVED","HUMAN_CLASSIFIED",
    "UNKNOWN","CONTRADICTED",
}
PROCESSING_DISPOSITION = {
    "CANONICALIZE",
    "CANONICALIZE_SELECTED",
    "REFERENCE_ONLY",
    "SOURCE_ONLY",
    "DEFER_RIGHTS",
    "DEFER_TECHNICAL",
    "SUPERSEDED",
    "EXCLUDE_WITH_REASON",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect-baseline", action="store_true")
    return parser.parse_args()


def read_csv(name: str, headers: list[str]) -> list[dict[str, str]]:
    path = REG / name
    if not path.is_file():
        raise ValueError(f"missing required registry table: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != headers:
            raise ValueError(
                f"{name}: header mismatch\nexpected={headers}\nactual={reader.fieldnames}"
            )
        return list(reader)


def unique(
    rows: list[dict[str, str]],
    field: str,
    table: str,
    errors: list[str],
) -> set[str]:
    values: set[str] = set()
    for n, row in enumerate(rows, start=2):
        value = row[field].strip()
        if not value:
            errors.append(f"{table}:{n}: blank required {field}")
            continue
        if value in values:
            errors.append(f"{table}:{n}: duplicate {field}={value}")
        values.add(value)
    return values


def is_hex64(value: str) -> bool:
    v = value.strip().lower()
    return len(v) == 64 and all(ch in "0123456789abcdef" for ch in v)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    if not REG.is_dir():
        print("control plane not yet migrated: control/registry is absent")
        return 1

    tables: dict[str, list[dict[str, str]]] = {}
    for name, headers in HEADERS.items():
        try:
            tables[name] = read_csv(name, headers)
        except ValueError as exc:
            errors.append(str(exc))

    for name, headers in OPTIONAL_HEADERS.items():
        if (REG / name).exists():
            try:
                tables[name] = read_csv(name, headers)
            except ValueError as exc:
                errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    resources = tables["resources.csv"]
    snapshots = tables["snapshots.csv"]
    artifacts = tables["artifacts.csv"]
    locations = tables["locations.csv"]
    snaparts = tables["snapshot_artifacts.csv"]
    aliases = tables["aliases.csv"]
    profiles = tables["profiles.csv"]
    lineage = tables["lineage.csv"]
    rights = tables["rights.csv"]
    resarts = tables.get("resource_artifacts.csv", [])
    decisions = tables.get("processing_decisions.csv", [])

    resource_ids = unique(resources, "resource_id", "resources.csv", errors)
    snapshot_ids = unique(snapshots, "snapshot_id", "snapshots.csv", errors)
    artifact_ids = unique(artifacts, "artifact_id", "artifacts.csv", errors)
    unique(locations, "location_id", "locations.csv", errors)
    unique(profiles, "profile_id", "profiles.csv", errors)
    unique(rights, "rights_id", "rights.csv", errors)
    unique(lineage, "lineage_id", "lineage.csv", errors)

    for n, row in enumerate(snapshots, start=2):
        if row["resource_id"] not in resource_ids:
            errors.append(
                f"snapshots.csv:{n}: unknown resource_id={row['resource_id']}"
            )

    by_hash: dict[tuple[str, str], str] = {}
    for n, row in enumerate(artifacts, start=2):
        aid = row["artifact_id"]
        digest = row["sha256"].strip().lower()
        if digest:
            if not is_hex64(digest):
                errors.append(f"artifacts.csv:{n}: invalid sha256={digest!r}")
            key = (digest, row["bytes"].strip())
            prior = by_hash.get(key)
            if prior and prior != aid:
                errors.append(
                    f"artifacts.csv:{n}: exact bytes represented by both "
                    f"{prior} and {aid}"
                )
            by_hash[key] = aid
        parent = row["archive_parent_artifact_id"].strip()
        if parent and parent not in artifact_ids:
            errors.append(f"artifacts.csv:{n}: unknown archive parent={parent}")

    primary_locations: dict[str, list[str]] = {}
    location_counts_by_artifact: dict[str, int] = {}
    for n, row in enumerate(locations, start=2):
        aid = row["artifact_id"]
        if aid not in artifact_ids:
            errors.append(
                f"locations.csv:{n}: unknown artifact_id={aid}"
            )
        location_counts_by_artifact[aid] = (
            location_counts_by_artifact.get(aid, 0) + 1
        )
        primary = row["is_primary"].strip().lower()
        if primary not in {"true", "false"}:
            errors.append(
                f"locations.csv:{n}: invalid is_primary={row['is_primary']!r}"
            )
        if primary == "true":
            primary_locations.setdefault(aid, []).append(row["location_id"])

    for aid in sorted(artifact_ids):
        count = location_counts_by_artifact.get(aid, 0)
        primaries = primary_locations.get(aid, [])
        if count == 0:
            errors.append(f"artifact has no registered location: {aid}")
        if len(primaries) != 1:
            errors.append(
                f"artifact {aid} must have exactly one primary location; "
                f"found {len(primaries)} ({primaries})"
            )

    for n, row in enumerate(snaparts, start=2):
        if row["snapshot_id"] not in snapshot_ids:
            errors.append(
                f"snapshot_artifacts.csv:{n}: unknown snapshot_id="
                f"{row['snapshot_id']}"
            )
        if row["artifact_id"] not in artifact_ids:
            errors.append(
                f"snapshot_artifacts.csv:{n}: unknown artifact_id="
                f"{row['artifact_id']}"
            )

    for n, row in enumerate(resarts, start=2):
        if row["resource_id"] not in resource_ids:
            errors.append(
                f"resource_artifacts.csv:{n}: unknown resource_id="
                f"{row['resource_id']}"
            )
        if row["artifact_id"] not in artifact_ids:
            errors.append(
                f"resource_artifacts.csv:{n}: unknown artifact_id="
                f"{row['artifact_id']}"
            )

    alias_keys = set()
    for n, row in enumerate(aliases, start=2):
        key = (row["alias"], row["alias_type"], row["canonical_resource_id"])
        if key in alias_keys:
            warnings.append(f"aliases.csv:{n}: repeated alias mapping={key}")
        alias_keys.add(key)
        if row["canonical_resource_id"] not in resource_ids:
            errors.append(
                f"aliases.csv:{n}: unknown canonical_resource_id="
                f"{row['canonical_resource_id']}"
            )

    profile_by_snapshot: dict[str, list[dict[str, str]]] = {}
    for n, row in enumerate(profiles, start=2):
        sid = row["snapshot_id"]
        if sid not in snapshot_ids:
            errors.append(f"profiles.csv:{n}: unknown snapshot_id={sid}")
        profile_by_snapshot.setdefault(sid, []).append(row)

        for field in ("profile_json_path", "profile_md_path", "schema_path"):
            rel = row[field].strip()
            path = ROOT / rel
            if not path.is_file():
                errors.append(f"profiles.csv:{n}: missing {field}={rel}")

        schema_path = ROOT / row["schema_path"].strip()
        expected_hash = row["schema_hash"].strip().lower()
        if schema_path.is_file() and expected_hash:
            actual_hash = sha256(schema_path)
            if actual_hash != expected_hash:
                errors.append(
                    f"profiles.csv:{n}: schema hash mismatch "
                    f"expected={expected_hash} actual={actual_hash}"
                )

    acquired = {
        row["snapshot_id"]
        for row in snapshots
        if row["acquisition_state"] in ACQUIRED
    }
    missing_profiles = sorted(
        sid for sid in acquired if len(profile_by_snapshot.get(sid, [])) != 1
    )
    if missing_profiles:
        errors.append(
            "acquired snapshots without exactly one profile: "
            + ", ".join(missing_profiles)
        )

    if decisions:
        unique(decisions, "decision_id", "processing_decisions.csv", errors)
        seen_decision_snapshots: set[str] = set()
        for n, row in enumerate(decisions, start=2):
            sid = row["snapshot_id"].strip()
            if sid not in snapshot_ids:
                errors.append(
                    f"processing_decisions.csv:{n}: unknown snapshot_id={sid}"
                )
            if sid not in acquired:
                errors.append(
                    f"processing_decisions.csv:{n}: decision is only valid for "
                    f"acquired snapshot, got {sid}"
                )
            if sid in seen_decision_snapshots:
                errors.append(
                    f"processing_decisions.csv:{n}: duplicate current decision "
                    f"for snapshot_id={sid}"
                )
            seen_decision_snapshots.add(sid)
            if row["disposition"] not in PROCESSING_DISPOSITION:
                errors.append(
                    f"processing_decisions.csv:{n}: invalid disposition="
                    f"{row['disposition']!r}"
                )
            for field in ("decision_basis", "evidence_refs", "decided_on", "decided_by"):
                if not row[field].strip():
                    errors.append(
                        f"processing_decisions.csv:{n}: blank required {field}"
                    )

        missing_decisions = sorted(acquired - seen_decision_snapshots)
        extra_decisions = sorted(seen_decision_snapshots - acquired)
        if missing_decisions:
            errors.append(
                "processing_decisions.csv must cover every acquired snapshot; "
                "missing: " + ", ".join(missing_decisions)
            )
        if extra_decisions:
            errors.append(
                "processing_decisions.csv contains non-acquired snapshots: "
                + ", ".join(extra_decisions)
            )

    action_fields = [
        "private_local_processing",
        "human_annotation",
        "external_hosted_model_inference",
        "derived_private_analysis",
        "public_aggregate_reporting",
        "public_example_redistribution",
        "public_raw_redistribution",
    ]
    for n, row in enumerate(rights, start=2):
        rid = row["resource_id"].strip()
        sid = row["snapshot_id"].strip()
        if not rid and not sid:
            errors.append(f"rights.csv:{n}: resource_id or snapshot_id required")
        if rid and rid not in resource_ids:
            errors.append(f"rights.csv:{n}: unknown resource_id={rid}")
        if sid and sid not in snapshot_ids:
            errors.append(f"rights.csv:{n}: unknown snapshot_id={sid}")
        for field in action_fields:
            if row[field] not in ACTION_STATE:
                errors.append(
                    f"rights.csv:{n}: invalid {field}={row[field]!r}"
                )
        if row["evidence_state"] not in EVIDENCE_STATE:
            errors.append(
                f"rights.csv:{n}: invalid evidence_state="
                f"{row['evidence_state']!r}"
            )

    ids_by_type = {
        "resource": resource_ids,
        "snapshot": snapshot_ids,
        "artifact": artifact_ids,
    }
    for n, row in enumerate(lineage, start=2):
        ft = row["from_type"]
        tt = row["to_type"]
        if ft in ids_by_type and row["from_id"] not in ids_by_type[ft]:
            errors.append(
                f"lineage.csv:{n}: unknown {ft} from_id={row['from_id']}"
            )
        if tt in ids_by_type and row["to_id"] not in ids_by_type[tt]:
            errors.append(
                f"lineage.csv:{n}: unknown {tt} to_id={row['to_id']}"
            )

    storage_counts: dict[str, int] = {}
    artifact_location_counts: dict[str, int] = {}
    for row in locations:
        storage = row["storage_class"]
        storage_counts[storage] = storage_counts.get(storage, 0) + 1
        aid = row["artifact_id"]
        artifact_location_counts[aid] = artifact_location_counts.get(aid, 0) + 1

    quality_counts = {
        "artifacts_with_sha256": sum(1 for row in artifacts if row["sha256"].strip()),
        "artifacts_without_sha256": sum(1 for row in artifacts if not row["sha256"].strip()),
        "artifacts_with_multiple_locations": sum(
            1 for n in artifact_location_counts.values() if n > 1
        ),
    }

    counts = {
        "resources": len(resources),
        "snapshots": len(snapshots),
        "artifacts": len(artifacts),
        "locations": len(locations),
        "snapshot_artifact_links": len(snaparts),
        "aliases": len(aliases),
        "rights_rows": len(rights),
        "lineage_edges": len(lineage),
        "acquired_snapshots": len(acquired),
        "profile_rows": len(profiles),
    }

    if args.expect_baseline:
        for key, expected in EXPECTED_COUNTS.items():
            actual = counts[key]
            if actual != expected:
                errors.append(
                    f"baseline count mismatch {key}: "
                    f"expected={expected} actual={actual}"
                )

        for storage, expected in EXPECTED_STORAGE_COUNTS.items():
            actual = storage_counts.get(storage, 0)
            if actual != expected:
                errors.append(
                    f"baseline storage count mismatch {storage}: "
                    f"expected={expected} actual={actual}"
                )

        if quality_counts["artifacts_with_sha256"] != 67:
            errors.append(
                "baseline SHA-256 coverage mismatch: expected 67 known hashes"
            )
        if quality_counts["artifacts_without_sha256"] != 589:
            errors.append(
                "baseline SHA-256 coverage mismatch: expected 589 unknown hashes"
            )
        if quality_counts["artifacts_with_multiple_locations"] != 9:
            errors.append(
                "baseline multi-location artifact count mismatch: expected 9"
            )

        for n, row in enumerate(locations, start=2):
            if row["storage_class"] == "GIT" and not row["locator"].startswith(
                "legacy-git://"
            ):
                errors.append(
                    f"locations.csv:{n}: baseline GIT locator is not legacy-qualified"
                )
            if (
                row["storage_class"] == "GITHUB_RELEASE"
                and not row["locator"].startswith("legacy-github-release://")
            ):
                errors.append(
                    f"locations.csv:{n}: baseline GITHUB_RELEASE locator is not "
                    "legacy-qualified"
                )

        for n, row in enumerate(rights, start=2):
            for field in action_fields:
                if row[field] != "UNKNOWN":
                    errors.append(
                        f"baseline rights must start UNKNOWN: "
                        f"rights.csv:{n} {field}={row[field]!r}"
                    )

        summary_path = MIGRATION / "MIGRATION_SUMMARY.json"
        if not summary_path.is_file():
            errors.append("missing quality/migration/MIGRATION_SUMMARY.json")
        else:
            try:
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                if summary.get("source_commit") != (
                    "83f6b3e16272d5a752ad1140986d2ef85bfb9569"
                ):
                    errors.append("migration summary source_commit mismatch")
                if summary.get("counts") != counts:
                    errors.append(
                        "migration summary counts differ from live control plane"
                    )
                if summary.get("storage_counts") != storage_counts:
                    errors.append(
                        "migration summary storage_counts differ from live control plane"
                    )
                if summary.get("quality_counts") != quality_counts:
                    errors.append(
                        "migration summary quality_counts differ from live control plane"
                    )
            except Exception as exc:
                errors.append(f"invalid MIGRATION_SUMMARY.json: {exc}")

    report = {
        "counts": counts,
        "expect_baseline": args.expect_baseline,
        "storage_counts": storage_counts,
        "quality_counts": quality_counts,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

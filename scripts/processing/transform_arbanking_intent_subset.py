#!/usr/bin/env python3
"""Deterministic bounded ArBanking77 Saudi intent transform dry run.

Processes eight source rows including three exact-duplicate pairs. The dry run
proves source labels/text are preserved and that repeated source records are not
silently deduplicated: each physical occurrence receives its own deterministic
Foundation record ID under the approved mapping rule.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SNAPSHOT_ID = "SNP-000009"
RESOURCE_ID = "RES-000008"
ARTIFACT_ID = "ART-000523"
SOURCE_OBJECT = "Banking77_Arabized_Saudi_test.csv"
SOURCE_REPO_PATH = Path(
    "source/legacy_relocated/gulf/mirrored/arbanking77/"
    "Banking77_Arabized_Saudi_test.csv"
)
EXPECTED_SHA256 = "9c01583810f37152a734197c3bf80b6cf9c6d129be25c9e1eac27bc0cd91af74"
EXPECTED_BYTES = 426_961
EXPECTED_ROWS = 3_580
EXPECTED_UNIQUE_ROWS = 3_545
EXPECTED_DUPLICATE_GROUPS = 34
EXPECTED_DUPLICATE_EXCESS_ROWS = 35
EXPECTED_UNIQUE_LABELS = 77
SELECTED_ORDINALS = (1, 48, 49, 183, 184, 879, 3_575, 3_580)
EXPECTED_SELECTED_DUPLICATE_GROUPS = 3
EXPECTED_SELECTED_DUPLICATE_EXCESS_ROWS = 3


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def foundation_id(physical_record_ordinal: int) -> str:
    preimage = SNAPSHOT_ID + ARTIFACT_ID + str(physical_record_ordinal)
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def read_source(source: Path) -> tuple[list[dict], dict]:
    source_bytes = source.stat().st_size
    if source_bytes != EXPECTED_BYTES:
        raise RuntimeError(
            f"source byte-size mismatch: {source_bytes} != {EXPECTED_BYTES}"
        )
    source_sha = sha256_file(source)
    if source_sha != EXPECTED_SHA256:
        raise RuntimeError(f"source sha256 mismatch: {source_sha}")

    selected: dict[int, dict] = {}
    source_pairs: list[tuple[str, str]] = []
    label_counts: Counter[str] = Counter()

    with source.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["label", "text"]:
            raise RuntimeError(
                f"unexpected source fields: {reader.fieldnames!r}"
            )
        for ordinal, row in enumerate(reader, start=1):
            label = row.get("label")
            text = row.get("text")
            if label is None or label == "":
                raise RuntimeError(f"record {ordinal}: missing label")
            if text is None or text == "":
                raise RuntimeError(f"record {ordinal}: missing text")

            pair = (label, text)
            source_pairs.append(pair)
            label_counts[label] += 1
            if ordinal in SELECTED_ORDINALS:
                selected[ordinal] = {
                    "physical_record_ordinal": ordinal,
                    "label": label,
                    "text": text,
                }

    if len(source_pairs) != EXPECTED_ROWS:
        raise RuntimeError(
            f"source row count mismatch: {len(source_pairs)} != {EXPECTED_ROWS}"
        )
    pair_counts = Counter(source_pairs)
    unique_rows = len(pair_counts)
    duplicate_groups = sum(1 for n in pair_counts.values() if n > 1)
    duplicate_excess = sum(n - 1 for n in pair_counts.values() if n > 1)

    if unique_rows != EXPECTED_UNIQUE_ROWS:
        raise RuntimeError(
            f"unique row count mismatch: {unique_rows} != {EXPECTED_UNIQUE_ROWS}"
        )
    if duplicate_groups != EXPECTED_DUPLICATE_GROUPS:
        raise RuntimeError(
            "duplicate group count mismatch: "
            f"{duplicate_groups} != {EXPECTED_DUPLICATE_GROUPS}"
        )
    if duplicate_excess != EXPECTED_DUPLICATE_EXCESS_ROWS:
        raise RuntimeError(
            "duplicate excess row count mismatch: "
            f"{duplicate_excess} != {EXPECTED_DUPLICATE_EXCESS_ROWS}"
        )
    if len(label_counts) != EXPECTED_UNIQUE_LABELS:
        raise RuntimeError(
            f"unique label count mismatch: {len(label_counts)} "
            f"!= {EXPECTED_UNIQUE_LABELS}"
        )
    if tuple(selected) != SELECTED_ORDINALS:
        raise RuntimeError(
            f"selected ordinal coverage mismatch: {tuple(selected)}"
        )

    selected_pairs = [
        (selected[o]["label"], selected[o]["text"]) for o in SELECTED_ORDINALS
    ]
    selected_pair_counts = Counter(selected_pairs)
    selected_duplicate_groups = sum(
        1 for n in selected_pair_counts.values() if n > 1
    )
    selected_duplicate_excess = sum(
        n - 1 for n in selected_pair_counts.values() if n > 1
    )
    if selected_duplicate_groups != EXPECTED_SELECTED_DUPLICATE_GROUPS:
        raise RuntimeError(
            "selected duplicate group mismatch: "
            f"{selected_duplicate_groups} "
            f"!= {EXPECTED_SELECTED_DUPLICATE_GROUPS}"
        )
    if selected_duplicate_excess != EXPECTED_SELECTED_DUPLICATE_EXCESS_ROWS:
        raise RuntimeError(
            "selected duplicate excess mismatch: "
            f"{selected_duplicate_excess} "
            f"!= {EXPECTED_SELECTED_DUPLICATE_EXCESS_ROWS}"
        )

    rows: list[dict] = []
    for ordinal in SELECTED_ORDINALS:
        item = selected[ordinal]
        rows.append(
            {
                "foundation_record_id": foundation_id(ordinal),
                "snapshot_id": SNAPSHOT_ID,
                "resource_id": RESOURCE_ID,
                "artifact_id": ARTIFACT_ID,
                "source_object": SOURCE_OBJECT,
                "source_record_locator": (
                    "git:source/legacy_relocated/gulf/mirrored/arbanking77/"
                    f"Banking77_Arabized_Saudi_test.csv#record={ordinal}"
                ),
                "source_split": None,
                "source_record_id": None,
                "record_family": "intent_utterance",
                "source_attributes": [],
                "source_intent": item["label"],
                "raw_text": item["text"],
            }
        )

    return rows, {
        "source_sha256": source_sha,
        "source_bytes": source_bytes,
        "source_row_count": len(source_pairs),
        "unique_row_count": unique_rows,
        "duplicate_group_count": duplicate_groups,
        "duplicate_excess_row_count": duplicate_excess,
        "unique_source_label_count": len(label_counts),
        "selected_duplicate_group_count": selected_duplicate_groups,
        "selected_duplicate_excess_row_count": selected_duplicate_excess,
    }


def write_parquet(rows: list[dict], output: Path) -> None:
    schema = pa.schema(
        [
            pa.field("foundation_record_id", pa.string(), nullable=False),
            pa.field("snapshot_id", pa.string(), nullable=False),
            pa.field("resource_id", pa.string(), nullable=False),
            pa.field("artifact_id", pa.string(), nullable=False),
            pa.field("source_object", pa.string(), nullable=False),
            pa.field("source_record_locator", pa.string(), nullable=False),
            pa.field("source_split", pa.string(), nullable=True),
            pa.field("source_record_id", pa.string(), nullable=True),
            pa.field("record_family", pa.string(), nullable=False),
            pa.field(
                "source_attributes",
                pa.map_(pa.string(), pa.string()),
                nullable=False,
            ),
            pa.field("source_intent", pa.string(), nullable=False),
            pa.field("raw_text", pa.string(), nullable=False),
        ]
    )
    table = pa.Table.from_pylist(rows, schema=schema)
    output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        table,
        output,
        compression="zstd",
        use_dictionary=True,
    )


def validate(rows: list[dict], output: Path, source_meta: dict) -> dict:
    table = pq.read_table(output)
    out = table.to_pylist()
    if table.num_rows != len(SELECTED_ORDINALS):
        raise RuntimeError(
            f"expected {len(SELECTED_ORDINALS)} rows, found {table.num_rows}"
        )
    if len({row["foundation_record_id"] for row in out}) != len(out):
        raise RuntimeError("foundation IDs are not unique")

    for original, emitted in zip(rows, out, strict=True):
        for field in (
            "foundation_record_id",
            "snapshot_id",
            "resource_id",
            "artifact_id",
            "source_object",
            "source_record_locator",
            "source_split",
            "source_record_id",
            "record_family",
            "source_intent",
            "raw_text",
        ):
            if original[field] != emitted[field]:
                raise RuntimeError(
                    f"{field} changed after Parquet round trip"
                )
        if dict(emitted["source_attributes"]) != {}:
            raise RuntimeError(
                "unexpected source_attributes emitted for ArBanking subset"
            )

    output_pairs = [(row["source_intent"], row["raw_text"]) for row in out]
    output_pair_counts = Counter(output_pairs)
    duplicate_groups = sum(1 for n in output_pair_counts.values() if n > 1)
    duplicate_excess = sum(
        n - 1 for n in output_pair_counts.values() if n > 1
    )
    if duplicate_groups != EXPECTED_SELECTED_DUPLICATE_GROUPS:
        raise RuntimeError(
            "duplicate groups were not preserved in canonical output"
        )
    if duplicate_excess != EXPECTED_SELECTED_DUPLICATE_EXCESS_ROWS:
        raise RuntimeError(
            "duplicate source occurrences were silently removed"
        )

    text_collection = "\n".join(row["raw_text"] for row in out)
    label_collection = "\n".join(row["source_intent"] for row in out)
    locator_collection = "\n".join(
        row["source_record_locator"] for row in out
    )
    schema_text = str(table.schema)

    return {
        "checkpoint": "8C-1I",
        "source_snapshot": SNAPSHOT_ID,
        "record_family": "intent_utterance",
        "subset_rule": (
            "records 1, 48, 49, 183, 184, 879, 3575, and 3580; "
            "includes three exact-duplicate pairs"
        ),
        "canonical_row_count": len(out),
        "source_row_count_verified": source_meta["source_row_count"],
        "source_unique_row_count_verified": source_meta["unique_row_count"],
        "source_duplicate_group_count_verified": source_meta[
            "duplicate_group_count"
        ],
        "source_duplicate_excess_row_count_verified": source_meta[
            "duplicate_excess_row_count"
        ],
        "source_unique_label_count_verified": source_meta[
            "unique_source_label_count"
        ],
        "selected_duplicate_group_count": duplicate_groups,
        "selected_duplicate_excess_row_count": duplicate_excess,
        "unique_foundation_record_ids": len(
            {row["foundation_record_id"] for row in out}
        ),
        "source_sha256": source_meta["source_sha256"],
        "source_bytes": source_meta["source_bytes"],
        "schema_sha256": hashlib.sha256(
            schema_text.encode("utf-8")
        ).hexdigest(),
        "output_parquet_sha256": sha256_file(output),
        "raw_text_collection_sha256": hashlib.sha256(
            text_collection.encode("utf-8")
        ).hexdigest(),
        "source_label_collection_sha256": hashlib.sha256(
            label_collection.encode("utf-8")
        ).hexdigest(),
        "source_locator_collection_sha256": hashlib.sha256(
            locator_collection.encode("utf-8")
        ).hexdigest(),
        "identity_preimage_rule": (
            "sha256(snapshot_id + artifact_id + physical_record_ordinal)"
        ),
        "lineage_note": (
            "SNP-000009 is registered as subset_of SNP-000008; this dry run "
            "preserves records and does not resolve or deduplicate lineage."
        ),
        "checks": {
            "schema_readable": True,
            "bounded_subset_selection": True,
            "stable_unique_record_ids": True,
            "source_provenance": True,
            "raw_text_preservation": True,
            "source_intent_label_preservation": True,
            "full_source_row_accounting": True,
            "full_duplicate_accounting": True,
            "selected_duplicate_occurrences_preserved": True,
            "no_silent_deduplication": True,
            "no_controlled_intent_population": True,
            "source_sha256": True,
        },
        "raw_source_text_emitted_in_manifest": False,
        "raw_source_label_values_emitted_in_manifest": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=SOURCE_REPO_PATH)
    p.add_argument("--output-parquet", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    args = p.parse_args()

    rows, source_meta = read_source(args.source)
    write_parquet(rows, args.output_parquet)
    manifest = validate(rows, args.output_parquet, source_meta)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

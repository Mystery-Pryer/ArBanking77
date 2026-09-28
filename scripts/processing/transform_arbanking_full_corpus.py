#!/usr/bin/env python3
"""Full deterministic ingestion of the preferred ArBanking77 corpus.

Each verified source row is a question bundle. The approved mapping emits four
Arabic utterance records per source row, one for each explicit source variant:
MSA1, MSA2, PAL1 and PAL2. Source labels and the English counterpart are
preserved exactly; variant tags are not promoted to controlled dialect fields.
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

SNAPSHOT_ID = "SNP-000008"
RESOURCE_ID = "RES-000008"
ARTIFACT_ID = "ART-000427"
SOURCE_OBJECT = "Banking77_full_corpus.csv"
EXPECTED_BYTES = 4_972_258
EXPECTED_SHA256 = "38863ae4093840f2418d76613d0c2134295fc78f1116361fa9ff00680b1309c1"
EXPECTED_PHYSICAL_ROWS = 13_083
EXPECTED_CLEAN_ROWS = 13_075
EXPECTED_OUTPUT_ROWS = 52_300
EXPECTED_QUARANTINED = (
    (855, "855", 2),
    (930, "930", 1),
    (2736, "2736", 2),
    (6707, "6707", 1),
    (6712, "6712", 1),
    (8271, "8271", 1),
    (9466, "9466", 1),
    (9483, "9483", 1),
)
EXPECTED_UNIQUE_INTENTS = 77
EXPECTED_VARIANT_ID_UNIQUES = {
    "MSA1": 13_075,
    "MSA2": 2_453,
    "PAL1": 13_071,
    "PAL2": 2_784,
}
SOURCE_FIELDS = [
    "Intent_ID",
    "Intent_en",
    "Intent_ar",
    "QID",
    "Question_en",
    "QuestionID_MSA1",
    "Question_MSA1",
    "QuestionID_MSA2",
    "Question_MSA2",
    "QuestionID_PAL1",
    "Question_PAL1",
    "QuestionID_PAL2",
    "Question_PAL2",
]
VARIANTS = (
    ("MSA1", "QuestionID_MSA1", "Question_MSA1"),
    ("MSA2", "QuestionID_MSA2", "Question_MSA2"),
    ("PAL1", "QuestionID_PAL1", "Question_PAL1"),
    ("PAL2", "QuestionID_PAL2", "Question_PAL2"),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def foundation_id(
    qid: int,
    source_variant: str,
    source_variant_id: str,
) -> str:
    preimage = (
        SNAPSHOT_ID
        + ARTIFACT_ID
        + str(qid)
        + source_variant
        + source_variant_id
    )
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def read_source(source: Path) -> tuple[list[dict], dict]:
    source_bytes = source.stat().st_size
    if source_bytes != EXPECTED_BYTES:
        raise RuntimeError(
            f"source byte-size mismatch: {source_bytes} != {EXPECTED_BYTES}"
        )
    source_sha = sha256_file(source)
    if source_sha != EXPECTED_SHA256:
        raise RuntimeError(
            f"source sha256 mismatch: {source_sha} != {EXPECTED_SHA256}"
        )

    rows: list[dict] = []
    qids: list[int] = []
    physical_records = 0
    quarantined: list[dict] = []
    full_source_rows: list[tuple[str, ...]] = []
    intent_ids: set[int] = set()
    intent_en: set[str] = set()
    intent_ar: set[str] = set()
    variant_ids: dict[str, set[str]] = {
        variant: set() for variant, _, _ in VARIANTS
    }
    variant_row_counts: Counter[str] = Counter()

    with source.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != SOURCE_FIELDS:
            raise RuntimeError(
                f"unexpected source fields: {reader.fieldnames!r}"
            )

        for source_ordinal, row in enumerate(reader, start=1):
            physical_records += 1
            if None in row:
                quarantined.append(
                    {
                        "physical_record_ordinal": source_ordinal,
                        "qid": row.get("QID"),
                        "extra_column_count": len(row.get(None) or []),
                        "status": "FAILED_EXTRACTION",
                        "reason": "EXTRA_UNNAMED_CSV_COLUMNS",
                    }
                )
                continue

            for field in SOURCE_FIELDS:
                value = row.get(field)
                if value is None or value == "":
                    raise RuntimeError(
                        f"source record {source_ordinal}: missing {field}"
                    )

            try:
                intent_id = int(row["Intent_ID"])
                qid = int(row["QID"])
            except ValueError as exc:
                raise RuntimeError(
                    f"source record {source_ordinal}: invalid integer ID"
                ) from exc

            qids.append(qid)
            intent_ids.add(intent_id)
            intent_en.add(row["Intent_en"])
            intent_ar.add(row["Intent_ar"])
            full_source_rows.append(tuple(row[field] for field in SOURCE_FIELDS))

            for variant, id_field, text_field in VARIANTS:
                variant_id = row[id_field]
                raw_text = row[text_field]
                variant_ids[variant].add(variant_id)
                variant_row_counts[variant] += 1

                rows.append(
                    {
                        "foundation_record_id": foundation_id(
                            qid, variant, variant_id
                        ),
                        "snapshot_id": SNAPSHOT_ID,
                        "resource_id": RESOURCE_ID,
                        "artifact_id": ARTIFACT_ID,
                        "source_object": SOURCE_OBJECT,
                        "source_record_locator": (
                            "git:source/legacy_relocated/gulf/mirrored/"
                            "arbanking77/Banking77_full_corpus.csv"
                            f"#qid={qid}&variant={variant}"
                        ),
                        "source_split": None,
                        "source_record_id": None,
                        "record_family": "intent_utterance",
                        "source_attributes": [],
                        "source_intent_id": intent_id,
                        "source_intent_en": row["Intent_en"],
                        "source_intent_ar": row["Intent_ar"],
                        "source_question_id": qid,
                        "english_translation": row["Question_en"],
                        "raw_text": raw_text,
                        "source_variant_id": variant_id,
                        "source_variant": variant,
                    }
                )

    if physical_records != EXPECTED_PHYSICAL_ROWS:
        raise RuntimeError(
            "physical source record count mismatch: "
            f"{physical_records} != {EXPECTED_PHYSICAL_ROWS}"
        )
    observed_quarantine = tuple(
        (
            item["physical_record_ordinal"],
            item["qid"],
            item["extra_column_count"],
        )
        for item in quarantined
    )
    if observed_quarantine != EXPECTED_QUARANTINED:
        raise RuntimeError(
            f"quarantine structure mismatch: {observed_quarantine!r}"
        )
    if len(qids) != EXPECTED_CLEAN_ROWS:
        raise RuntimeError(
            f"clean source row count mismatch: {len(qids)} != {EXPECTED_CLEAN_ROWS}"
        )
    if len(set(qids)) != EXPECTED_CLEAN_ROWS:
        raise RuntimeError("QID is not unique across source rows")
    if len(set(full_source_rows)) != EXPECTED_CLEAN_ROWS:
        raise RuntimeError("exact duplicate source bundle rows detected")
    if len(intent_ids) != EXPECTED_UNIQUE_INTENTS:
        raise RuntimeError(
            f"unique intent ID count mismatch: {len(intent_ids)} "
            f"!= {EXPECTED_UNIQUE_INTENTS}"
        )
    if len(intent_en) != EXPECTED_UNIQUE_INTENTS:
        raise RuntimeError("English intent label count mismatch")
    if len(intent_ar) != EXPECTED_UNIQUE_INTENTS:
        raise RuntimeError("Arabic intent label count mismatch")
    if len(rows) != EXPECTED_OUTPUT_ROWS:
        raise RuntimeError(
            f"output expansion mismatch: {len(rows)} != {EXPECTED_OUTPUT_ROWS}"
        )
    if dict(variant_row_counts) != {
        variant: EXPECTED_CLEAN_ROWS for variant, _, _ in VARIANTS
    }:
        raise RuntimeError(
            f"variant row accounting mismatch: {dict(variant_row_counts)}"
        )

    actual_variant_uniques = {
        variant: len(values) for variant, values in variant_ids.items()
    }
    if actual_variant_uniques != EXPECTED_VARIANT_ID_UNIQUES:
        raise RuntimeError(
            "variant ID uniqueness mismatch: "
            f"{actual_variant_uniques} != {EXPECTED_VARIANT_ID_UNIQUES}"
        )

    return rows, {
        "source_sha256": source_sha,
        "source_bytes": source_bytes,
        "source_physical_record_count": physical_records,
        "source_clean_row_count": len(qids),
        "source_quarantined_record_count": len(quarantined),
        "quarantined_records": quarantined,
        "source_unique_qids": len(set(qids)),
        "source_unique_intent_ids": len(intent_ids),
        "source_unique_intent_en": len(intent_en),
        "source_unique_intent_ar": len(intent_ar),
        "source_exact_unique_rows": len(set(full_source_rows)),
        "variant_row_counts": dict(variant_row_counts),
        "variant_id_unique_counts": actual_variant_uniques,
    }


def canonical_schema() -> pa.Schema:
    return pa.schema(
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
            pa.field("source_intent_id", pa.int64(), nullable=False),
            pa.field("source_intent_en", pa.string(), nullable=False),
            pa.field("source_intent_ar", pa.string(), nullable=False),
            pa.field("source_question_id", pa.int64(), nullable=False),
            pa.field("english_translation", pa.string(), nullable=False),
            pa.field("raw_text", pa.string(), nullable=False),
            pa.field("source_variant_id", pa.string(), nullable=False),
            pa.field("source_variant", pa.string(), nullable=False),
        ]
    )


def write_parquet(rows: list[dict], output: Path) -> None:
    table = pa.Table.from_pylist(rows, schema=canonical_schema())
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

    if table.num_rows != EXPECTED_OUTPUT_ROWS:
        raise RuntimeError(
            f"expected {EXPECTED_OUTPUT_ROWS} rows, found {table.num_rows}"
        )
    if len({row["foundation_record_id"] for row in out}) != EXPECTED_OUTPUT_ROWS:
        raise RuntimeError("foundation IDs are not unique")

    output_variant_counts = Counter(row["source_variant"] for row in out)
    expected_variant_counts = {
        variant: EXPECTED_CLEAN_ROWS for variant, _, _ in VARIANTS
    }
    if dict(output_variant_counts) != expected_variant_counts:
        raise RuntimeError(
            f"output variant accounting mismatch: {dict(output_variant_counts)}"
        )

    output_variant_id_uniques = {
        variant: len(
            {
                row["source_variant_id"]
                for row in out
                if row["source_variant"] == variant
            }
        )
        for variant, _, _ in VARIANTS
    }
    if output_variant_id_uniques != EXPECTED_VARIANT_ID_UNIQUES:
        raise RuntimeError(
            "output variant ID uniqueness mismatch: "
            f"{output_variant_id_uniques}"
        )

    for ordinal, (original, emitted) in enumerate(
        zip(rows, out, strict=True), start=1
    ):
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
            "source_intent_id",
            "source_intent_en",
            "source_intent_ar",
            "source_question_id",
            "english_translation",
            "raw_text",
            "source_variant_id",
            "source_variant",
        ):
            if original[field] != emitted[field]:
                raise RuntimeError(
                    f"output record {ordinal}: {field} changed after round trip"
                )
        if dict(emitted["source_attributes"]) != {}:
            raise RuntimeError(
                f"output record {ordinal}: unexpected source_attributes"
            )

    raw_text_collection = "\n".join(row["raw_text"] for row in out)
    english_collection = "\n".join(
        row["english_translation"] for row in out
    )
    variant_id_collection = "\n".join(
        f"{row['source_variant']}\t{row['source_variant_id']}" for row in out
    )
    intent_collection = "\n".join(
        f"{row['source_intent_id']}\t{row['source_intent_en']}\t"
        f"{row['source_intent_ar']}"
        for row in out
    )
    locator_collection = "\n".join(
        row["source_record_locator"] for row in out
    )
    id_collection = "\n".join(
        row["foundation_record_id"] for row in out
    )
    schema_text = str(table.schema)

    return {
        "checkpoint": "9B",
        "source_snapshot": SNAPSHOT_ID,
        "record_family": "intent_utterance",
        "ingestion_mode": "full_deterministic_one_to_many",
        "source_physical_record_count": source_meta["source_physical_record_count"],
        "source_clean_bundle_count": source_meta["source_clean_row_count"],
        "failed_extraction_count": source_meta["source_quarantined_record_count"],
        "failed_extractions": source_meta["quarantined_records"],
        "canonical_row_count": len(out),
        "source_unique_qids": source_meta["source_unique_qids"],
        "source_unique_intent_ids": source_meta["source_unique_intent_ids"],
        "source_unique_intent_en": source_meta["source_unique_intent_en"],
        "source_unique_intent_ar": source_meta["source_unique_intent_ar"],
        "source_exact_unique_rows": source_meta["source_exact_unique_rows"],
        "variant_row_counts": dict(output_variant_counts),
        "variant_id_unique_counts": output_variant_id_uniques,
        "unique_foundation_record_ids": len(
            {row["foundation_record_id"] for row in out}
        ),
        "source_sha256": source_meta["source_sha256"],
        "source_bytes": source_meta["source_bytes"],
        "schema_sha256": hashlib.sha256(
            schema_text.encode("utf-8")
        ).hexdigest(),
        "output_parquet_sha256": sha256_file(output),
        "output_parquet_bytes": output.stat().st_size,
        "raw_text_collection_sha256": hashlib.sha256(
            raw_text_collection.encode("utf-8")
        ).hexdigest(),
        "english_translation_collection_sha256": hashlib.sha256(
            english_collection.encode("utf-8")
        ).hexdigest(),
        "variant_id_collection_sha256": hashlib.sha256(
            variant_id_collection.encode("utf-8")
        ).hexdigest(),
        "source_intent_collection_sha256": hashlib.sha256(
            intent_collection.encode("utf-8")
        ).hexdigest(),
        "source_locator_collection_sha256": hashlib.sha256(
            locator_collection.encode("utf-8")
        ).hexdigest(),
        "foundation_id_collection_sha256": hashlib.sha256(
            id_collection.encode("utf-8")
        ).hexdigest(),
        "identity_preimage_rule": (
            "sha256(snapshot_id + artifact_id + QID + "
            "source_variant + source_variant_id)"
        ),
        "lineage_note": (
            "SNP-000009 remains subset_of SNP-000008. This ingestion preserves "
            "all full-corpus records and does not deduplicate the already "
            "ingested Saudi partial snapshot."
        ),
        "compression": "zstd",
        "checks": {
            "schema_readable": True,
            "full_physical_source_accounting": True,
            "malformed_rows_quarantined": True,
            "clean_source_bundle_accounting": True,
            "four_way_variant_expansion": True,
            "stable_unique_record_ids": True,
            "source_provenance": True,
            "raw_text_preservation": True,
            "english_translation_preservation": True,
            "source_intent_preservation": True,
            "source_variant_id_preservation": True,
            "source_variant_tag_preservation": True,
            "no_variant_to_controlled_dialect_promotion": True,
            "no_controlled_intent_population": True,
        },
        "raw_source_text_emitted_in_manifest": False,
        "raw_source_label_values_emitted_in_manifest": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
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

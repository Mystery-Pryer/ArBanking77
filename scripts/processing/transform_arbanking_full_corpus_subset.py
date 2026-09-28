#!/usr/bin/env python3
"""Deterministic bounded ArBanking77 full-corpus expansion dry run.

Reads the complete verified full-corpus CSV for source/accounting checks and
deterministic identity coverage, then emits a small structure-stress subset that
contains all four explicit Arabic source variants. No controlled dialect or
intent semantics are inferred.
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
EXPECTED_SHA256 = "38863ae4093840f2418d76613d0c2134295fc78f1116361fa9ff00680b1309c1"
EXPECTED_BYTES = 4_972_258
EXPECTED_ROWS = 13_075
EXPECTED_OUTPUT_ROWS = 52_300
EXPECTED_INTENT_IDS = 77
EXPECTED_QIDS = 13_075
EXPECTED_UNIQUE_SOURCE_ROWS = 13_075
EXPECTED_VARIANT_UNIQUES = {
    "MSA1": {"id": 13_075, "text": 13_075},
    "MSA2": {"id": 2_453, "text": 2_453},
    "PAL1": {"id": 13_071, "text": 13_075},
    "PAL2": {"id": 2_784, "text": 2_784},
}
FIELDS = [
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


def foundation_id(qid: str, variant: str, variant_id: str) -> str:
    preimage = SNAPSHOT_ID + ARTIFACT_ID + qid + variant + variant_id
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def read_source(source: Path) -> tuple[list[dict[str, str]], dict]:
    source_bytes = source.stat().st_size
    if source_bytes != EXPECTED_BYTES:
        raise RuntimeError(
            f"source byte-size mismatch: {source_bytes} != {EXPECTED_BYTES}"
        )
    source_sha = sha256_file(source)
    if source_sha != EXPECTED_SHA256:
        raise RuntimeError(f"source sha256 mismatch: {source_sha}")

    parsed: list[dict[str, str]] = []
    with source.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise RuntimeError(f"unexpected source fields: {reader.fieldnames!r}")
        for ordinal, row in enumerate(reader, start=1):
            for field in FIELDS:
                value = row.get(field)
                if value is None or value == "":
                    raise RuntimeError(f"record {ordinal}: missing {field}")
            parsed.append(row)

    if len(parsed) != EXPECTED_ROWS:
        raise RuntimeError(f"source row count mismatch: {len(parsed)} != {EXPECTED_ROWS}")

    qids = [row["QID"] for row in parsed]
    if len(set(qids)) != EXPECTED_QIDS:
        raise RuntimeError("QID uniqueness mismatch")

    intent_ids = {row["Intent_ID"] for row in parsed}
    if len(intent_ids) != EXPECTED_INTENT_IDS:
        raise RuntimeError(
            f"intent ID cardinality mismatch: {len(intent_ids)} != {EXPECTED_INTENT_IDS}"
        )

    source_rows = [tuple(row[field] for field in FIELDS) for row in parsed]
    if len(set(source_rows)) != EXPECTED_UNIQUE_SOURCE_ROWS:
        raise RuntimeError("exact source-row uniqueness mismatch")

    variant_counts: dict[str, dict[str, int]] = {}
    repeated_variant_id_first_ordinal: dict[str, int] = {}
    for variant, id_field, text_field in VARIANTS:
        ids = [row[id_field] for row in parsed]
        texts = [row[text_field] for row in parsed]
        unique_ids = len(set(ids))
        unique_texts = len(set(texts))
        expected = EXPECTED_VARIANT_UNIQUES[variant]
        if unique_ids != expected["id"]:
            raise RuntimeError(
                f"{variant} ID cardinality mismatch: {unique_ids} != {expected['id']}"
            )
        if unique_texts != expected["text"]:
            raise RuntimeError(
                f"{variant} text cardinality mismatch: {unique_texts} != {expected['text']}"
            )
        counts = Counter(ids)
        repeated_variant_id_first_ordinal[variant] = next(
            i for i, value in enumerate(ids, start=1) if counts[value] > 1
        )
        variant_counts[variant] = {
            "unique_ids": unique_ids,
            "unique_texts": unique_texts,
        }

    all_foundation_ids: set[str] = set()
    for row in parsed:
        qid = row["QID"]
        for variant, id_field, _ in VARIANTS:
            fid = foundation_id(qid, variant, row[id_field])
            if fid in all_foundation_ids:
                raise RuntimeError("full-corpus Foundation identity collision")
            all_foundation_ids.add(fid)

    if len(all_foundation_ids) != EXPECTED_OUTPUT_ROWS:
        raise RuntimeError(
            f"full identity accounting mismatch: {len(all_foundation_ids)} "
            f"!= {EXPECTED_OUTPUT_ROWS}"
        )

    selected_ordinals = sorted(
        {
            1,
            2,
            EXPECTED_ROWS - 1,
            EXPECTED_ROWS,
            repeated_variant_id_first_ordinal["MSA2"],
            repeated_variant_id_first_ordinal["PAL2"],
        }
    )

    return parsed, {
        "source_sha256": source_sha,
        "source_bytes": source_bytes,
        "source_rows": len(parsed),
        "unique_source_rows": len(set(source_rows)),
        "unique_qids": len(set(qids)),
        "unique_intent_ids": len(intent_ids),
        "variant_counts": variant_counts,
        "full_foundation_id_count": len(all_foundation_ids),
        "repeated_variant_id_first_ordinal": repeated_variant_id_first_ordinal,
        "selected_ordinals": selected_ordinals,
    }


def canonical_row(source_row: dict[str, str], variant: str, id_field: str, text_field: str) -> dict:
    qid = source_row["QID"]
    variant_id = source_row[id_field]
    return {
        "foundation_record_id": foundation_id(qid, variant, variant_id),
        "snapshot_id": SNAPSHOT_ID,
        "resource_id": RESOURCE_ID,
        "artifact_id": ARTIFACT_ID,
        "source_object": SOURCE_OBJECT,
        "source_record_locator": (
            f"csv:{SOURCE_OBJECT}#QID={qid}&variant={variant}&variant_id={variant_id}"
        ),
        "source_split": None,
        "source_record_id": variant_id,
        "record_family": "intent_utterance",
        "source_attributes": [],
        "source_intent_id": int(source_row["Intent_ID"]),
        "source_intent_en": source_row["Intent_en"],
        "source_intent_ar": source_row["Intent_ar"],
        "source_question_id": int(qid),
        "english_translation": source_row["Question_en"],
        "source_variant_id": variant_id,
        "source_variant": variant,
        "raw_text": source_row[text_field],
    }


def build_subset(parsed: list[dict[str, str]], selected_ordinals: list[int]) -> list[dict]:
    out: list[dict] = []
    for ordinal in selected_ordinals:
        source_row = parsed[ordinal - 1]
        for variant, id_field, text_field in VARIANTS:
            out.append(canonical_row(source_row, variant, id_field, text_field))
    return out


def schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("foundation_record_id", pa.string(), nullable=False),
            pa.field("snapshot_id", pa.string(), nullable=False),
            pa.field("resource_id", pa.string(), nullable=False),
            pa.field("artifact_id", pa.string(), nullable=False),
            pa.field("source_object", pa.string(), nullable=False),
            pa.field("source_record_locator", pa.string(), nullable=False),
            pa.field("source_split", pa.string(), nullable=True),
            pa.field("source_record_id", pa.string(), nullable=False),
            pa.field("record_family", pa.string(), nullable=False),
            pa.field("source_attributes", pa.map_(pa.string(), pa.string()), nullable=False),
            pa.field("source_intent_id", pa.int64(), nullable=False),
            pa.field("source_intent_en", pa.string(), nullable=False),
            pa.field("source_intent_ar", pa.string(), nullable=False),
            pa.field("source_question_id", pa.int64(), nullable=False),
            pa.field("english_translation", pa.string(), nullable=False),
            pa.field("source_variant_id", pa.string(), nullable=False),
            pa.field("source_variant", pa.string(), nullable=False),
            pa.field("raw_text", pa.string(), nullable=False),
        ]
    )


def write_parquet(rows: list[dict], output: Path) -> None:
    table = pa.Table.from_pylist(rows, schema=schema())
    output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, output, compression="zstd", use_dictionary=True)


def validate(rows: list[dict], output: Path, source_meta: dict) -> dict:
    table = pq.read_table(output)
    emitted = table.to_pylist()
    expected_rows = len(source_meta["selected_ordinals"]) * len(VARIANTS)
    if table.num_rows != expected_rows:
        raise RuntimeError(f"bounded output row mismatch: {table.num_rows} != {expected_rows}")
    if len({row["foundation_record_id"] for row in emitted}) != expected_rows:
        raise RuntimeError("bounded Foundation IDs are not unique")

    variant_counts = dict(sorted(Counter(row["source_variant"] for row in emitted).items()))
    expected_variant_count = len(source_meta["selected_ordinals"])
    expected_variant_counts = {variant: expected_variant_count for variant, _, _ in VARIANTS}
    if variant_counts != expected_variant_counts:
        raise RuntimeError(f"bounded variant accounting mismatch: {variant_counts}")

    for original, out in zip(rows, emitted, strict=True):
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
            "source_variant_id",
            "source_variant",
            "raw_text",
        ):
            if original[field] != out[field]:
                raise RuntimeError(f"{field} changed after Parquet round trip")
        if dict(out["source_attributes"]) != {}:
            raise RuntimeError("unexpected source_attributes content")

    raw_text_collection = "\n".join(row["raw_text"] for row in emitted)
    english_collection = "\n".join(row["english_translation"] for row in emitted)
    intent_collection = "\n".join(
        f"{row['source_intent_id']}\t{row['source_intent_en']}\t{row['source_intent_ar']}"
        for row in emitted
    )
    variant_id_collection = "\n".join(
        f"{row['source_variant']}\t{row['source_variant_id']}" for row in emitted
    )
    locator_collection = "\n".join(row["source_record_locator"] for row in emitted)

    return {
        "checkpoint": "9B",
        "source_snapshot": SNAPSHOT_ID,
        "record_family": "intent_utterance",
        "subset_rule": (
            "source rows 1, 2, final two rows, plus first rows whose MSA2 and PAL2 "
            "variant IDs repeat; emit MSA1/MSA2/PAL1/PAL2 for every selected row"
        ),
        "selected_source_ordinals": source_meta["selected_ordinals"],
        "selected_source_row_count": len(source_meta["selected_ordinals"]),
        "canonical_row_count": len(emitted),
        "selected_variant_row_counts": variant_counts,
        "full_source_row_count_verified": source_meta["source_rows"],
        "full_unique_source_rows_verified": source_meta["unique_source_rows"],
        "full_unique_qids_verified": source_meta["unique_qids"],
        "full_unique_intent_ids_verified": source_meta["unique_intent_ids"],
        "full_variant_cardinalities_verified": source_meta["variant_counts"],
        "full_expected_canonical_rows_verified": source_meta["full_foundation_id_count"],
        "repeated_variant_id_first_ordinal": source_meta["repeated_variant_id_first_ordinal"],
        "unique_bounded_foundation_record_ids": len(
            {row["foundation_record_id"] for row in emitted}
        ),
        "source_sha256": source_meta["source_sha256"],
        "source_bytes": source_meta["source_bytes"],
        "schema_sha256": hashlib.sha256(str(table.schema).encode("utf-8")).hexdigest(),
        "output_parquet_sha256": sha256_file(output),
        "output_parquet_bytes": output.stat().st_size,
        "raw_text_collection_sha256": hashlib.sha256(
            raw_text_collection.encode("utf-8")
        ).hexdigest(),
        "english_translation_collection_sha256": hashlib.sha256(
            english_collection.encode("utf-8")
        ).hexdigest(),
        "source_intent_collection_sha256": hashlib.sha256(
            intent_collection.encode("utf-8")
        ).hexdigest(),
        "source_variant_id_collection_sha256": hashlib.sha256(
            variant_id_collection.encode("utf-8")
        ).hexdigest(),
        "source_locator_collection_sha256": hashlib.sha256(
            locator_collection.encode("utf-8")
        ).hexdigest(),
        "identity_preimage_rule": (
            "sha256(snapshot_id + artifact_id + QID + source_variant + source_variant_id)"
        ),
        "compression": "zstd",
        "checks": {
            "schema_readable": True,
            "exact_source_identity": True,
            "full_source_row_accounting": True,
            "full_qid_uniqueness": True,
            "full_intent_cardinality": True,
            "full_variant_cardinality_accounting": True,
            "full_foundation_identity_uniqueness": True,
            "bounded_all_variant_coverage": True,
            "bounded_stable_unique_record_ids": True,
            "source_provenance": True,
            "source_intent_preservation": True,
            "source_question_id_preservation": True,
            "english_counterpart_preservation": True,
            "variant_id_preservation": True,
            "variant_tag_preservation": True,
            "raw_text_preservation": True,
            "no_controlled_dialect_population": True,
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

    parsed, source_meta = read_source(args.source)
    rows = build_subset(parsed, source_meta["selected_ordinals"])
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

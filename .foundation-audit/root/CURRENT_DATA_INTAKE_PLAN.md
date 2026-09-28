# Current Data Intake Plan

Status: **HISTORICAL INTAKE BASELINE — MIGRATION RECONCILED**
Baseline source commit: `83f6b3e16272d5a752ad1140986d2ef85bfb9569`
Baseline date: **2026-09-23**

This document preserves the verified pre-migration intake baseline.

**It is not the current work queue or processing method.** Current execution is
owned by `STATE.md`, `PROCESSING_METHOD.md`, `CONTROL_PLANE_CONTRACT.md`,
and `WORKFLOW_GUARDRAILS.md`.

The historical baseline answered three intake questions:

1. **What data/evidence do we currently know we have?**
2. **How is each object reached?**
3. **What will happen to it under the new foundation workflow?**

The counts below are the verified intake baseline from the existing inventory.
They are not assumptions and they are not a permanent declaration of future
state. At migration start, the baseline is re-read and reconciled mechanically
before any authority is transferred.

The legacy repository is only the intake source for these facts. It is not the
design authority for this repository.

---

## 1. Baseline verified inventory

### Canonical identity/control baseline

| Measure | Verified count |
|---|---:|
| Resources | 189 |
| Snapshots | 196 |
| Artifacts | 656 |
| Physical locations | 665 |
| Snapshot-artifact links | 664 |
| Aliases | 267 |
| Rights seed rows | 61 |
| Lineage edges | 4 |
| Acquired snapshots | 149 |

Snapshot acquisition states:

| State | Count |
|---|---:|
| ACQUIRED_VERIFIED | 148 |
| ACQUIRED_PARTIAL | 1 |
| DEFERRED_ACCESS | 15 |
| REFERENCE_ONLY | 25 |
| BLOCKED_TECHNICAL | 4 |
| COMMERCIAL_NOT_ACQUIRED | 2 |
| RETIRED | 1 |

Resource types at the identity level:

| Type | Count |
|---|---:|
| Papers | 98 |
| Datasets | 86 |
| Corpus | 1 |
| Book | 1 |
| Thesis | 1 |
| Morphology resource | 1 |
| Ontology | 1 |

These type labels are coarse identity labels only. They are not final task,
dialect, domain, or annotation taxonomy.

---

## 2. Baseline verified storage map

| Storage class | Verified locations | How it is reached | Foundation handling |
|---|---:|---|---|
| Private Hugging Face buckets | 495 | registered `hf://buckets/...` locator | keep bytes in durable private storage unless a concrete need requires relocation; migrate identity and locator authority |
| ChatGPT Library / uploads | 106 | registered Library/upload locator | preserve exact identity and access reference; relocate only if long-term durability requires it |
| Git-tracked files | 37 | repository path recorded as a location | small useful source/evidence files may be copied into foundation-controlled storage if rights permit |
| GitHub Release assets | 27 | release/asset locator | relocate to foundation-controlled durable storage before the legacy repository disappears |

Hugging Face baseline:

- 38 private buckets;
- 495 inventoried objects;
- approximately 90.3 GB represented by the verified bucket-tree inventory;
- 5 empty buckets identified as placeholders rather than acquired datasets.

The approximately 90.3 GB value is the recorded bucket-tree total from the
baseline inventory. It must not be silently reinterpreted as exact live storage
size after the baseline date.

---

## 3. How an object is found

The foundation does not locate data by memory, filenames, or folder browsing.

The lookup chain is:

```text
resource
  ↓ resources.csv
snapshot
  ↓ snapshots.csv
snapshot-artifact relationship
  ↓ snapshot_artifacts.csv
artifact
  ↓ artifacts.csv
location
  ↓ locations.csv
physical locator
```

For example, the physical locator may be:

```text
hf://buckets/<owner>/<bucket>/<path>
```

or a registered Library object, Git path, release asset, or external source
location.

No credentials, access tokens, or secrets are stored in the registry.

### Strong identity

Where available, artifacts use SHA-256 plus size/path/container evidence.

2026-09-23 baseline:

- artifacts with known SHA-256: 67 / 656;
- artifacts without independently recorded SHA-256: 589;
- artifacts with multiple verified physical locations: 9.

The 589 entries are not assigned invented hashes. Strong hashes are added when
the bytes are actually read for processing or when migration requires byte-level
verification.

---

## 4. Baseline profile coverage

All 149 acquired snapshots already have profile records in the intake baseline:

| Profile state | Count |
|---|---:|
| PROFILED | 142 |
| PROFILE_PARTIAL | 7 |
| PROFILE_DEFERRED | 0 |
| Total | 149 |

The profiles include:

- 100 reference-document snapshots;
- 49 non-document snapshots.

Reference-document baseline:

- 98 papers;
- 1 thesis;
- 1 book;
- 1,518 pages total;
- 93 DOI detections;
- 95 author/editor detections;
- 95 external evidence roles.

These document profiles are primarily bibliographic/structural unless a deeper
methodology review was explicitly performed. They must not be treated as if
every paper has already undergone full methodology extraction.

---

## 5. Known important structured sources

Examples already profiled in the baseline include:

- SauDial — 1,000 rows × 12 fields;
- Arabic EOU SADA — 414,053 rows, including 9,890 exact duplicate rows;
- SADA22 — 253,166 rows from Parquet metadata;
- NADI 2026 ADI-20 Micro — 77,821 rows from Parquet metadata;
- OpinRank Dubai subset — 12,110 records across 236 per-hotel files;
- NIYYAH — 10,500 rows;
- ArBanking77 preferred acquired wide corpus — 13,075 rows and 77 intents.

These are examples of known contents, not a pre-decision about whether or how
they will be used by the GCC lab.

---

## 6. Known partial profiles

Seven acquired snapshots are intentionally partial and must retain their
limitations:

1. Gumar N-grams — archives inventoried but payloads not fully parsed;
2. SADA22 — row/schema/split totals known from Parquet metadata, not a full
   row-level scan;
3. NADI 2026 ADI-20 Micro — metadata-level profile for the large Parquet shards;
4. GLARE — aggregate/schema evidence exists, but the large raw and engineered
   archives were not redundantly streamed in full;
5. OpinRank Dubai — 236 per-hotel files parsed, aggregate ZIP not redundantly
   rescanned;
6. EAC public samples — PDF/profile-level evidence, no reconstructed structured
   corpus turns;
7. EMALAC public sample — PDF/profile-level evidence, no reconstructed
   structured corpus turns.

A partial profile is not automatically a problem.

If a snapshot is selected for a transformation requiring deeper evidence, it
receives targeted deeper inspection before mapping. If it is not selected, a
full scan is not performed merely for completeness.

---

## 7. What will physically move into this repository

The foundation repository will contain the **control and evidence needed to
manage the collection**, not a duplicate of all source bytes.

### Migrate into Git

- stable resource/snapshot/artifact/location identities;
- aliases;
- profile registry and per-snapshot profile evidence;
- existing rights evidence, clearly marked as incomplete where applicable;
- useful provenance/source evidence;
- useful methodology/reference evidence;
- validated inventory/profiling logic;
- transformation mappings created under the new design;
- transformation/run/lineage records;
- validation results;
- release manifests;
- small source/evidence files only when appropriate and permitted.

### Do not bulk-copy into Git

- the approximately 90.3 GB private object-store collection;
- large archives;
- large Parquet shards;
- audio archives;
- other large source or canonical data merely for repository neatness.

Large canonical outputs will normally use controlled external storage and be
referenced through registered artifact/location records.

---

## 8. What must be relocated before the old repository disappears

Any byte object whose only durable location depends on the legacy repository
must not remain there.

Baseline classes requiring explicit migration review included:

- GitHub Release assets tied to the legacy repository;
- small Git-tracked source/evidence artifacts that remain needed;
- any Git-relative locator whose path would become invalid after deletion.

The migration rule is:

```text
old registered object
   ↓
verify identity / size / hash when available
   ↓
copy to foundation-controlled durable location
   ↓
verify new copy
   ↓
add new location
   ↓
make new location authoritative
   ↓
only then retire old location
```

Private Hugging Face objects do not need to be copied simply because repository
ownership changes, provided their durable locator and access remain valid.

---

## 9. What will happen to every acquired snapshot

Every in-scope acquired snapshot receives exactly one current processing
decision after its existing evidence is migrated and reviewed.

Allowed disposition families include:

- `CANONICALIZE`
- `CANONICALIZE_SELECTED`
- `REFERENCE_ONLY`
- `SOURCE_ONLY`
- `DEFER_RIGHTS`
- `DEFER_TECHNICAL`
- `SUPERSEDED`
- `EXCLUDE_WITH_REASON`

The actual decision is not pre-filled from intuition.

It is based on:

- what the source actually contains;
- profile depth and limitations;
- rights/access evidence;
- source identity/version relationships;
- duplicate/subset/derivative relationships;
- whether its contents support a foundation data product useful to the
  downstream annotation lab.

Every acquired snapshot must have a decision. A source cannot disappear because
it was inconvenient, large, redundant-looking, or not immediately useful.

---

## 10. Historical routing examples by evidence/data class

The routes below record the intake-era planning model. They are retained as
historical rationale only. Current sequencing is defined in
`PROCESSING_METHOD.md`.

The following are routing rules, not pre-decided outcomes for individual
resources.

### Structured text/corpus data

Possible route:

```text
source
→ profile/deepen if needed
→ rights/use review
→ processing decision
→ field mapping
→ canonical transformation
→ validation
→ cross-source overlap analysis
→ candidate release member
```

Possible canonical families include:

- `text_instance`
- `intent_utterance`
- `review`
- `conversation_turn`
- `parallel_text`

### Speech/audio data

Audio bytes normally remain external.

The foundation may create verified metadata/segment/transcript records when the
source and intended use justify it.

Possible family:

- `speech_segment`

### Lexical/morphological resources

Preserve source forms and upstream analyses.

Possible family:

- `lexicon_entry`

No linguistic value is silently rewritten as a "correction."

### N-gram/statistical resources

Possible family:

- `ngram_stat`

Large archives are parsed only to the depth required by an actual product or
analysis need.

### Papers/books/theses/methodology material

These do not become ordinary corpus rows.

They may be retained as:

- bibliographic/reference evidence;
- methodology evidence;
- terminology evidence;
- rights/license evidence;
- optional `reference_chunk` products when retrieval is justified.

### Samples / partial versions / paid or inaccessible sources

A sample remains a sample.

A preview never implies acquisition of the full resource.

Paid, gated, blocked, or non-acquired sources may remain metadata/reference
records unless legitimate access is later obtained.

---

## 11. Arabic and dialect handling during processing

For every transformation:

- original Arabic text remains available as `text_raw`;
- dialectal spelling is not "corrected";
- grammar is not normalized to MSA by default;
- repeated letters, punctuation, spacing, Arabizi, and code-switching are
  preserved in raw form;
- a Saudi/Gulf/sub-dialect label is not inferred from intuition;
- source labels are retained separately from controlled mappings;
- normalized equality does not imply duplicate raw records;
- any normalization is a named, versioned derived field and must have a stated
  use.

This rule applies before any data can become a foundation release member.

---

## 12. Duplicate handling

The foundation distinguishes at least:

- exact duplicate bytes;
- one artifact stored in multiple locations;
- duplicate source rows;
- normalized-text matches;
- near-duplicate records;
- dataset subsets;
- derivative datasets;
- train/dev/test leakage;
- cross-dataset overlap.

None of these relationships automatically causes deletion.

If a later curated product excludes a record, that exclusion must be accounted
for by an explicit transformation rule and validation result.

---

## 13. Contradiction handling

Upstream claims and observed bytes are separate evidence.

Example pattern:

```text
UPSTREAM_REPORTED:
  source documentation says X

OBSERVED:
  acquired file contains Y

state:
  CONTRADICTED
```

The foundation does not guess which explanation is true.

A contradiction remains visible until supported evidence resolves it.

---

## 14. Rights and release eligibility

The baseline 61 rights rows are only seed evidence, not a complete rights/use
audit for all 189 resources.

Therefore:

- presence in the collection does not imply permission to transform,
  redistribute, publish, train on, or expose publicly;
- existing rights evidence is reviewed for disposition; deeper rights review is performed only to the depth required by the intended action;
- every release member must have a sufficiently resolved use state for the GCC
  lab's intended consumption;
- unresolved rights can lead to `DEFER_RIGHTS` without deleting the source from
  the registry.

---

## 15. Foundation output

The end state is not one giant merged Arabic dataset.

The end state is:

```text
known source universe
        ↓
controlled identity + evidence
        ↓
selected canonical record families
        ↓
quality / overlap / rights checks
        ↓
versioned foundation release AFR-xxxx
        ↓
gcc-bilingual-annotation-evaluation-lab
```

Different data classes remain separate unless a shared canonical schema and
purpose are genuinely supported.

Every released record/product must retain a provenance path back to the source
snapshot and source artifact/location.

---

## 16. Migration gate

Before processing work relies on the migrated foundation control plane, the
migration must reconcile at least this baseline:

- resources: 189;
- snapshots: 196;
- artifacts: 656;
- physical locations: 665;
- acquired snapshots: 149;
- profile records: 149;
- legacy identity aliases represented without unresolved mapping.

Any difference must be explained by a documented migration action, not ignored.

The migration audit must distinguish:

- migrated;
- intentionally superseded;
- external-only;
- relocated;
- excluded with reason;
- not applicable to the new foundation.

---

## 17. Baseline limitations that remain facts

The 2026-09-23 baseline does **not** establish:

- complete rights clearance for the whole collection;
- full SHA-256 coverage for all 656 artifacts;
- full row-level scans for all large datasets;
- final task/domain/dialect taxonomy for all resources;
- final canonical schemas;
- final downstream project suitability;
- that upstream labels are gold truth;
- that every resource should be transformed;
- that approximately 90.3 GB is the exact future live storage size.

Those are intentionally unresolved until the relevant processing decision
requires evidence.

---

## 18. Authority after migration

After migration and reconciliation:

- this foundation registry becomes the identity/storage authority;
- this foundation's profiles become the profile authority;
- this foundation's processing decisions become the action authority;
- transformation/run/lineage records become processing authority;
- validation records become quality evidence;
- published `AFR-xxxx` manifests become the only supported consumer interface
  for the GCC lab.

The legacy repository must not remain an operational dependency.

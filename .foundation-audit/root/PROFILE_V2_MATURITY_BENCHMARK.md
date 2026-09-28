# Profile V2 Maturity Benchmark and Implementation Design

Status: **IMPLEMENTED BASELINE — HISTORICAL DESIGN RATIONALE**

Applies to: Foundation profiling, semantic discovery, validation evidence, and collection-level analysis for the acquired 149-snapshot baseline.

Profile V2 contract, pilot, 149-snapshot rollout, and collection analysis are
implemented on current `main`. This document now preserves the benchmark and
design rationale; it is **not** a current implementation queue.

Current phase/next action are owned by `STATE.md`, and current source-processing
behavior is owned by `PROCESSING_METHOD.md`.

This document converts the Foundation Profile V2 proposal into a design informed by mature data-quality, metadata, lineage, observability, and reproducibility workflows. It is intentionally selective: the goal is to borrow strong production patterns without turning this private learning/portfolio Foundation into an enterprise platform.

It does **not** authorize corpus transformation, canonical recordset creation, Project 01 work, or AFR publication.

---

## 1. Repository constraints this design must preserve

This design is subordinate to the existing Foundation contracts and must preserve:

- resource -> snapshot -> artifact -> location identity;
- immutable source bytes;
- one fact / one authority;
- no silent omission, deduplication, or normalization;
- unknown remains unknown;
- contradiction preservation;
- rights are not inferred from license intuition;
- partial profiles remain honestly partial;
- GCC consumes only accepted AFR releases;
- Git history normally owns profile version history instead of parallel V1 / V2 copies.

Profile V2 is therefore an evolution of the current profile authority, not a second registry or a replacement architecture.

---

## 2. Benchmark question

The benchmark asks:

> If a mature data team had to profile a heterogeneous ~90 GB Arabic/GCC source collection for later annotation/evaluation use, what workflow boundaries, evidence artifacts, quality controls, reproducibility practices, and tools would we expect to see?

The benchmark focuses on patterns rather than product adoption.

The Foundation should copy **good operating ideas**, not install every product studied.

---

## 3. Mature frameworks reviewed

### 3.1 Great Expectations

Relevant production pattern:

- declarative expectations;
- reusable validation definitions;
- Checkpoints as an execution boundary;
- persisted Validation Results;
- Actions after validation;
- human-readable Data Docs generated from machine results.

Useful lesson for Foundation:

> Descriptive profiling evidence, reusable assertions, validation execution, validation result, and human-readable rendering should be distinct concerns.

Adopt:
- explicit validation results;
- reusable checks;
- generated human views from machine evidence.

Do not adopt:
- Great Expectations as a mandatory runtime dependency at this stage.

References:

- https://docs.greatexpectations.io/docs/reference/api/checkpoint_class/
- https://docs.greatexpectations.io/docs/core/configure_project_settings/configure_data_docs/
- https://docs.greatexpectations.io/docs/core/trigger_actions_based_on_results/run_a_checkpoint/

### 3.2 dbt

Relevant production pattern:

- declarative data tests;
- a project manifest describing logical resources;
- a separate run-results artifact describing what executed, timing, and status;
- generated documentation and DAG context;
- run artifacts that can be analyzed across executions.

Useful lesson for Foundation:

> The profile itself should not be the only persisted evidence. A profiling run needs a first-class execution manifest.

Adopt:
- separate logical profile contract from run result;
- execution timing/status/tool version/input identity;
- deterministic machine-readable output suitable for CI and later trend analysis.

Do not adopt:
- dbt as the processing engine; Foundation sources are heterogeneous files, documents, speech, archives, and corpora rather than a SQL-model DAG.

References:

- https://docs.getdbt.com/reference/artifacts/run-results-json
- https://docs.getdbt.com/reference/artifacts/manifest-json
- https://docs.getdbt.com/docs/build/data-tests

### 3.3 OpenMetadata

Relevant production pattern:

- table/column profiler metrics are separate from data-quality tests;
- profiler workflows feed descriptive statistics;
- tests run as assertions with separate outcomes;
- data assets expose schema, sample/profile, quality, lineage, and executions as related but distinct views.

Useful lesson for Foundation:

> Profile V2 should describe what evidence exists. A separate quality layer should evaluate whether an invariant or requirement is satisfied.

Adopt:
- profile / quality separation;
- explicit execution view;
- asset-level and field-level evidence;
- extensible metrics.

Do not adopt:
- a metadata server/catalog service for the current collection.

References:

- https://docs.open-metadata.org/v1.12.x/how-to-guides/data-quality-observability/profiler
- https://docs.open-metadata.org/v1.12.x/how-to-guides/data-quality-observability/quality
- https://docs.open-metadata.org/v1.12.x/how-to-guides/data-quality-observability/profiler/profiler-workflow

### 3.4 Soda

Relevant production pattern:

- human-readable checks are declared separately from the scan;
- one scan executes multiple checks;
- results have explicit pass/fail/error and optional warn states;
- checks include completeness, uniqueness, freshness, reference, reconciliation, schema, distribution, and custom failed-row logic.

Useful lesson for Foundation:

> Foundation profile-policy checks should be reusable definitions, not ad hoc conditions embedded in profile generation.

Adopt:
- named reusable checks;
- PASS / FAIL / WARN / BLOCKED-like outcomes;
- one validation execution covering multiple assertions.

Do not adopt:
- Soda Cloud or SodaCL as mandatory infrastructure.

References:

- https://docs.soda.io/soda-documentation/soda-v3/sodacl-reference/metrics-and-checks
- https://docs.soda.io/soda-documentation/soda-v3/soda-cl-overview

### 3.5 whylogs / WhyLabs

Relevant production pattern:

- compact statistical profiles rather than repeated raw-data export;
- approximate sketches such as cardinality estimators;
- one-pass profiling;
- mergeable partial profiles for distributed/partitioned datasets;
- custom metrics for text and other data types;
- profile history can support monitoring without retaining copies of the raw dataset.

Useful lesson for Foundation:

> Large-file profiling should prefer mergeable summaries and sketches when exact raw-value enumeration is unnecessary.

Adopt:
- one-pass counters;
- compact sketches where exact distinct counts are too costly;
- partition/row-group summaries that can be reduced;
- no requirement to materialize entire large datasets.

Do not adopt initially:
- WhyLabs SaaS;
- whylogs as a required dependency unless its implementation materially reduces our own code.

References:

- https://docs.whylabs.ai/docs/overview-profiles/
- https://docs.whylabs.ai/docs/logger-overview/
- https://docs.whylabs.ai/docs/spark-integration/

### 3.6 OpenLineage

Relevant production pattern:

- distinguish Job from Run;
- give each run an identity;
- represent inputs and outputs explicitly;
- attach structured facets for execution metadata;
- represent exact dataset and field lineage rather than inferring every possible edge.

Useful lesson for Foundation:

> Profiling is an execution that consumes registered artifacts and produces evidence artifacts. That relationship should be explicit and should not create false lineage.

Adopt:
- run identity;
- exact input artifact/snapshot references;
- exact output evidence references;
- field/source relationship evidence where useful.

Do not adopt:
- an OpenLineage backend or event bus at this stage.

References:

- https://openlineage.io/docs/spec/facets/
- https://openlineage.io/docs/spec/facets/job-facets/lineage/
- https://openlineage.io/docs/spec/facets/dataset-facets/lineage/

### 3.7 Deequ

Relevant production pattern:

- automated verification of large datasets;
- profiling and constraint verification are related but distinct;
- large-scale checks can be computed in distributed execution when needed.

Useful lesson for Foundation:

> Quality rules should be written as verifiable constraints, but distributed Spark infrastructure should only be introduced if real workload evidence demands it.

Adopt:
- constraint-oriented thinking.

Reject for now:
- Spark/Deequ runtime complexity.

Reference:

- https://github.com/awslabs/deequ

### 3.8 DVC and lakeFS

Relevant production pattern:

- explicit dependencies and outputs;
- reproducible pipeline stages;
- immutable points in history;
- isolated branches;
- review before merge;
- large data remains external rather than copied into Git.

Useful lesson for Foundation:

> The current Git + external object-storage model is already directionally correct. Add reproducible run evidence before adding another data-versioning platform.

Adopt:
- explicit input/output identities;
- branch + PR;
- deterministic regeneration;
- external large bytes.

Do not adopt now:
- DVC cache;
- lakeFS server.

References:

- https://dvc.org/doc/user-guide/pipelines/defining-pipelines
- https://docs.lakefs.io/guides/version-data/

---

## 4. Result of the benchmark

The earlier Profile V2 proposal was directionally correct but mixed too many responsibilities into profile.json.

The mature pattern is:

~~~text
REGISTERED SOURCE / SNAPSHOT
        |
        v
SCAN PLANNING
        |
        v
PROFILING EXECUTION
        |
        +----> profile_run.json
        |
        v
DESCRIPTIVE PROFILE
        |
        +----> profile.json
        +----> schema.json
        |
        v
SEMANTIC EVIDENCE ENRICHMENT
        |
        v
REUSABLE PROFILE / POLICY CHECKS
        |
        v
VALIDATION EXECUTION
        |
        +----> validation result
        |
        v
GENERATED HUMAN VIEW
        |
        +----> PROFILE.md
        +----> collection matrices/reports
        |
        v
HUMAN PROCESSING DECISION
        |
        v
MAPPING / TRANSFORMATION / VALIDATION
~~~

The key maturity improvement is **separation of evidence from assertions and assertions from execution results**.

---

## 5. Artifact responsibilities

### 5.1 profile.json

Authority for descriptive profile evidence for the current snapshot.

It answers:

> What does this snapshot contain, and what do we actually know about it?

It must not answer:

> Does this source pass our project policy?

Core sections:

~~~text
profile_identity
source_structure
logical_units
field_semantics
language_evidence
arabic_variety_evidence
bilingual_relationships
interaction_evidence
label_semantics
annotation_evidence
noise_characteristics
document_reference_role
quality_observations
source_relationship_evidence
transformation_observations
limitations
unresolved_questions
~~~

Every material semantic claim must carry evidence provenance.

### 5.2 profile_run.json

Authority for how the current profile evidence was generated.

This is the equivalent of a lightweight dbt/OpenLineage-style run artifact.

Required fields should include:

~~~text
profile_run_id
snapshot_id
profiler_name
profiler_version
profile_contract_version
producer_git_sha
started_at
completed_at
status
scan_plan
input_artifact_ids
input_location_ids
input_identity_state
files_considered
files_read
bytes_considered
bytes_read
rows_examined
sampling_method
sampling_seed
columns_examined
metadata_sources_used
configuration_hash
environment_fingerprint
warnings
errors
profile_json_sha256
schema_json_sha256
profile_md_sha256
~~~

Run status vocabulary:

~~~text
COMPLETE
COMPLETE_WITH_WARNINGS
PARTIAL
BLOCKED
FAILED
~~~

profile_run.json is not an additional historical version store.

Only the current run artifact is required in the snapshot profile folder; Git history normally owns previous run versions.

### 5.3 schema.json

Authority for observed logical/physical schema evidence relevant to the snapshot.

Where a source has multiple independent record shapes, schema representation must make that explicit rather than pretending one flat table exists.

### 5.4 PROFILE.md

Human-readable generated interpretation of machine evidence.

It should be reproducibly rendered from the machine-readable artifacts plus clearly marked curated commentary.

It must not become a separate owner of facts.

### 5.5 reusable checks

Profile V2 implementation should add a small machine-readable check definition set.

Checks are distinct from profile metrics.

Examples:

~~~text
PV2-001 snapshot identity resolves in registry
PV2-002 every semantic assertion has evidence provenance
PV2-003 source label is not overwritten by controlled label
PV2-004 real-interaction classification requires supporting evidence
PV2-005 verified dialect classification requires supporting evidence
PV2-006 translation/parallel classification requires relationship evidence
PV2-007 profile partiality is preserved and explicit
PV2-008 rights state is referenced, never inferred by profiler
PV2-009 raw/source fields remain distinct from derived fields
PV2-010 profile run records scan depth
PV2-011 full-scan claim requires byte/row accounting
PV2-012 deterministic sample records its seed/rule
PV2-013 source-reported and derived claims remain distinguishable
~~~

Check definitions should be stable and reusable across snapshots.

### 5.6 validation result

The existing validations.csv authority remains the correct long-term Foundation validation registry.

Profile V2 validation should eventually persist a result artifact and, where appropriate, a validations.csv row.

A validation result should include:

~~~text
validation_id
profile_run_id
snapshot_id
check_set_version
executed_at
status
checks_passed
checks_warned
checks_failed
checks_blocked
check_results[]
producer_git_sha
result_sha256
~~~

No new competing validation registry should be created.

---

## 6. Evidence model

Every material semantic assertion in Profile V2 should use one of these provenance classes:

~~~text
OBSERVED_BYTES
SOURCE_PROVIDED_INLINE
SOURCE_PROVIDED_LOOKUP
SOURCE_DOCUMENTATION
REGISTRY_EVIDENCE
DERIVED_DETERMINISTIC
HUMAN_VERIFIED
MODEL_GENERATED
UNKNOWN
~~~

Each assertion should support:

~~~text
value
evidence_class
evidence_ref
method
confidence
notes
~~~

Confidence must never substitute for evidence class.

Examples:

- a source README saying Saudi dialect -> SOURCE_DOCUMENTATION;
- a field literally containing country=SA -> SOURCE_PROVIDED_INLINE;
- measured Arabic character ratio -> DERIVED_DETERMINISTIC;
- a reviewer confirming intent meaning after inspecting a source guideline -> HUMAN_VERIFIED;
- an LLM guess about a dialect feature -> MODEL_GENERATED, not verified source truth.

---

## 7. Arabic and bilingual evidence rules

### 7.1 Keep three dialect concepts separate

~~~text
source_declared_variety
observed_linguistic_characteristics
verified_variety
~~~

A model or heuristic may propose observed characteristics.

It must not silently populate verified_variety.

### 7.2 Bilingual relationship vocabulary

Relationship classes should include:

~~~text
PARALLEL_TRANSLATION
ENGLISH_GLOSS
ENGLISH_INTENT_DESCRIPTION
ENGLISH_CATEGORY_DESCRIPTION
TRANSLITERATION
ENGLISH_METADATA_ONLY
CODE_SWITCHED_TEXT
ARABIC_EXPLANATION
UNRELATED_MULTILINGUAL_FIELDS
MIXED_OR_UNKNOWN
~~~

Alignment level should be independent:

~~~text
TURN
UTTERANCE
SENTENCE
ROW
INTENT_LOOKUP
DOCUMENT
LOOSE
UNKNOWN
~~~

A pair of Arabic/English columns is not enough evidence for PARALLEL_TRANSLATION.

---

## 8. Intent semantics design

Intent profiling must distinguish:

~~~text
source_intent_id
source_intent_label
source_intent_name_ar
source_intent_name_en
source_intent_description
source_utterance
source_translation
source_gloss
source_parent_intent
source_examples
source_slots
source_lookup_ref

controlled_intent_id
controlled_intent_label
mapping_status
mapping_evidence
~~~

The profiler may discover and describe source semantics.

It must not automatically create controlled Foundation intent mappings.

---

## 9. Interaction provenance

Profile V2 interaction classes:

~~~text
REAL_INTERACTION
REALISTIC_SYNTHETIC
ANNOTATED_UTTERANCE
REVIEW_OPINION
SOCIAL_TEXT
REFERENCE_EXAMPLE
UNKNOWN
~~~

For conversation-like data, profile:

~~~text
conversation_id
turn_structure
speaker_field
speaker_roles
turn_order
customer_agent_evidence
context_dependency
intent_fields
sentiment_fields
outcome_fields
channel_fields
timestamp_fields
~~~

REAL_INTERACTION requires direct evidence.

Dialogue-like structure alone is insufficient.

---

## 10. Reference documents

Books, papers, theses, guidelines, and methods should not be flattened into ordinary evaluation records.

Profile V2 knowledge roles:

~~~text
INTENT_TAXONOMY_REFERENCE
CUSTOMER_SERVICE_DOMAIN_REFERENCE
ARABIC_GRAMMAR_REFERENCE
DIALECT_REFERENCE
TYPO_SPELLING_REFERENCE
ANNOTATION_GUIDELINE_REFERENCE
EVALUATION_METHODOLOGY_REFERENCE
LEXICAL_TERMINOLOGY_REFERENCE
DATASET_DOCUMENTATION
RIGHTS_LICENSE_EVIDENCE
SOURCE_METHODOLOGY_EVIDENCE
GENERAL_REFERENCE
~~~

Document profiles should preserve:

- bibliographic identity;
- page count;
- document role;
- relevant sections/pages when selectively reviewed;
- whether text came from native extraction or OCR;
- exact evidence reference.

Do not OCR or parse 100 reference documents in full simply to make profiles look complete.

---

## 11. Noise and robustness evidence

During discovery, collect observable characteristics rather than correcting the source.

Possible measurements:

- Unicode normalization differences;
- leading/trailing whitespace;
- repeated whitespace;
- repeated-character elongation;
- Arabic/Latin mixed script;
- Arabizi-like patterns;
- emoji frequency;
- punctuation density;
- diacritic density;
- digit frequency;
- URL/email/handle patterns;
- character/token length distributions;
- exact duplicate rate;
- normalized duplicate candidate rate.

Misspelling and grammar error should not be asserted as source truth from a model alone.

The profile should say what was observed and separately state what analytical use that evidence might support.

---

## 12. Efficient scan architecture for ~90 GB

### Level 0 — registry/profile reuse

No source-byte read.

Use:

- registry identities;
- current profile JSON;
- current schema JSON;
- migrated profile summaries;
- rights evidence;
- source documentation already registered.

Purpose:
- discover what is already known;
- construct the scan plan;
- avoid redundant reads.

### Level 1 — metadata-only

Read the minimum structure needed.

Examples:

- Parquet footer/schema/row-group statistics;
- archive member tables;
- file headers/magic;
- audio headers;
- PDF metadata/text-layer availability;
- XLSX workbook/sheet metadata;
- JSON/CSV delimiters/schema samples.

Purpose:
- determine grain/shape;
- identify candidate semantic fields;
- decide whether deeper inspection is necessary.

### Level 2 — deterministic targeted inspection

Read selected fields, members, row groups, pages, or records.

Sampling must record:

- rule;
- seed where randomization exists;
- requested size;
- achieved size;
- partitions/segments represented.

Recommended default for semantic discovery:

- fixed head sample;
- deterministic hashed sample;
- targeted rare/category sample where value distributions justify it.

Do not rely on a head sample alone for dialect/noise conclusions.

### Level 3 — exact full stream

Use only when a decision requires collection-wide evidence, such as:

- exact duplicate counts;
- full content hash;
- exact language/noise prevalence;
- transformation;
- exact cross-source fingerprint generation.

When bytes are streamed fully, compute all useful one-pass evidence together:

~~~text
SHA-256
byte count
record count
parse errors
null counts
script counters
length sketches
duplicate fingerprints
semantic-field counters
selected text fingerprints
~~~

Do not reread the same immutable artifact separately for each metric.

---

## 13. Tooling decisions

### Python 3.12

Keep as orchestration/runtime language.

Reason:
- already locked by repository;
- suitable for heterogeneous formats;
- easy CI and testing.

### PyArrow

Use for:

- Parquet schema/footer metadata;
- row-group statistics;
- selective column reads;
- row-group reads;
- Parquet writing.

Why:

PyArrow can inspect Parquet metadata without reading all data and supports reading selected columns/row groups.

Reference:

- https://arrow.apache.org/docs/python/parquet.html

### DuckDB

Use for:

- collection-wide profile analysis;
- cross-profile queries;
- Parquet metadata inspection;
- relationship/overlap analysis;
- large analytical joins without building a service.

DuckDB supports projection/filter pushdown for Parquet and exposes row-group/column metadata.

References:

- https://duckdb.org/docs/current/data/parquet/metadata
- https://duckdb.org/docs/stable/data/parquet/overview

### Polars

Use for:

- lazy CSV/Parquet/NDJSON profiling;
- projection/predicate pushdown;
- streaming-style data-frame computations where appropriate;
- text/statistical counters.

Use lazy scans by default for large tabular sources.

References:

- https://docs.pola.rs/user-guide/lazy/optimizations/
- https://docs.pola.rs/user-guide/io/parquet/

### Pydantic + JSON Schema

Use Pydantic models in Python to author/validate machine artifacts and export JSON Schema for external readability.

Reason:
- one typed implementation contract;
- deterministic validation;
- readable errors;
- JSON artifacts remain tool-neutral.

Avoid making Markdown the schema authority.

### pytest

Use for:

- contract tests;
- deterministic fixtures;
- semantic-evidence invariants;
- regression fixtures for the pilot;
- failure-mode tests.

### GitHub Actions

Extend the existing repository-quality workflow to run:

~~~text
compile
existing repository validation
Profile V2 schema validation
Profile V2 check validation
pytest
pilot fixture/regeneration checks
~~~

Do not run a 90 GB collection scan in normal pull-request CI.

### Optional compact-sketch support

Before adding whylogs, evaluate whether Foundation can cover its actual requirements with lightweight libraries or local implementations for:

- HyperLogLog approximate cardinality;
- quantile sketches;
- bounded frequent-item summaries;
- MinHash-style cross-source overlap candidates.

Adopt a dependency only when it materially reduces complexity and has deterministic portable serialization.

### Explicitly not justified now

Do not add yet:

- Spark;
- Airflow;
- Dagster;
- Prefect;
- Great Expectations runtime;
- OpenMetadata server;
- Soda Cloud;
- WhyLabs SaaS;
- DVC cache;
- lakeFS server;
- Kafka;
- a separate metadata database.

These become candidates only if an observed operational problem requires them.

---

## 14. Cache and identity policy

Profiling reuse should be based on evidence identity, not filenames.

Preferred cache key order:

1. known artifact SHA-256;
2. immutable external object identity plus verified byte size/version;
3. registered artifact ID + location identity + verified metadata;
4. otherwise no claim of exact cache equivalence.

If a full read computes a previously unknown SHA-256:

- preserve the new hash as new evidence through the appropriate control process;
- do not silently mutate unrelated identity evidence inside the profiler.

---

## 15. Collection-level outputs

After Profile V2 exists across the acquired collection, generate distinct analytical products:

~~~text
collection_profile_coverage
source_to_use_case_matrix
transformation_needs_matrix
source_relationship_report
merge_compatibility_matrix
unresolved_questions_matrix
rights_readiness_matrix
reference_role_matrix
first_project_scenario_analysis
collection_quality_report
~~~

These are generated analytical views.

They are not new authorities for identity, rights, or processing disposition.

---

## 16. Merge compatibility

Do not run a naive all-pairs semantic merge decision over 149 snapshots first.

First group plausible candidates by:

- record family;
- task;
- language;
- domain;
- interaction type;
- label presence;
- bilingual relationship.

Then evaluate candidate relationships using:

~~~text
DIRECTLY_COMPATIBLE
COMPATIBLE_AFTER_MAPPING
COMPLEMENTARY_BUT_SHOULD_REMAIN_SEPARATE
REFERENCE_SUPPORT_ONLY
OVERLAPPING_DERIVATIVE
INCOMPATIBLE
UNKNOWN
~~~

Similarity can create a candidate relationship.

It cannot by itself prove semantic equivalence.

---

## 17. Pilot set

The initial pilot should intentionally test different failure modes rather than simply choose the best sources.

Recommended pilot:

| Snapshot | Source | Primary design stress |
|---|---|---|
| SNP-000008 | ArBanking77 Saudi | intent semantics + multilingual field relationships |
| SNP-000007 | NIYYAH | intent + dialect/review metadata + split evidence |
| SNP-000014 | Alexandria | bilingual nested conversation + translator/reviewer evidence |
| SNP-000042 | Voho Saudi Dialogues | nested multi-turn service dialogue |
| SNP-000021 | Organic Gulf Arabic sample | informal/noisy/code-switch candidate text |
| SNP-000004 | UniMorph Gulf Arabic | lexicon/headerless TSV semantics |
| SNP-000001 | Gumar N-grams | large archive + metadata-first profiling |
| SNP-000086 | OpinRank Dubai | review corpus + deliberately partial aggregate archive |
| SNP-000041 | Emirati Dialect Shows Audio Transcription | speech/transcript alignment |
| SNP-000101 | Emirati Arabic comprehensive grammar | large reference book |
| SNP-000099 | Government smart-app ABSA thesis | methodology/reference extraction |

Pilot success means the contract survives heterogeneous sources without inventing facts.

It does not mean these snapshots have been approved for canonicalization.

---

## 18. Pilot review checklist

For each pilot profile review:

### Identity

- snapshot/resource/artifact links resolve;
- preferred/non-preferred snapshot state is preserved;
- no duplicate authority introduced.

### Structural evidence

- correct logical grain;
- row/document/turn/audio counts have explicit semantics;
- partial/full scan status is honest.

### Semantic evidence

- semantic roles are supported;
- translation/gloss/description are distinguished;
- intent name/definition/utterance are distinguished;
- source/derived/model-generated facts are distinguishable.

### Arabic/GCC evidence

- reported and verified varieties are separate;
- no dialect guess becomes verified truth;
- code-switching evidence is measurable.

### Interaction evidence

- real/synthetic/review/social provenance is explicit;
- speaker/turn claims have supporting evidence.

### Rights

- profiler reads/references rights evidence only;
- profiler never converts license names into action clearance.

### Reproducibility

- run artifact records scan depth;
- deterministic sampling can be reproduced;
- generated artifacts validate;
- repeat run on unchanged input is stable.

---

## 19. Historical CI maturity gate — satisfied by integrated rollout

The original design required collection-wide use to wait until CI demonstrated:

1. all machine artifacts conform to schemas;
2. invalid provenance values fail;
3. unsupported REAL_INTERACTION fails;
4. unsupported verified-dialect claims fail;
5. source/controlled labels cannot collide silently;
6. partial scan cannot claim full scan;
7. deterministic sampling fixture reproduces;
8. profile rendering is deterministic apart from explicitly excluded runtime timestamps/IDs;
9. current repository validator still passes;
10. migrated 149-profile coverage is not lost.

---

## 20. Performance evidence

Every collection run should record enough execution metrics to answer:

- how many snapshots were reused without byte reads;
- how many used metadata-only inspection;
- how many used targeted sampling;
- how many required full scans;
- total bytes considered;
- total bytes actually read;
- total scan duration;
- top cost-driving artifacts;
- cache hits;
- failures/retries.

This makes the claim that unnecessary 90 GB rescanning was avoided measurable rather than rhetorical.

---

## 21. Historical implementation sequence — completed / non-operational

### PR A — Profile V2 contract and pilot framework

Branch:

~~~text
feat/profile-v2-pilot
~~~

Deliver:

- typed Profile V2 contract;
- exported JSON Schema;
- profile-run contract;
- reusable check definitions;
- validator;
- V1 carry-forward adapter;
- pilot format inspectors;
- pilot tests.

No collection-wide run.

### PR B — 11-snapshot pilot evidence

If implementation size makes PR A too large, split generated pilot evidence into a second PR.

Deliver:

- regenerated current profile artifacts for pilot snapshots;
- profile-run artifacts;
- validation results;
- review summary.

Human review occurs before collection rollout.

### PR C — collection-wide Profile V2 run

Branch:

~~~text
analysis/profile-v2-collection
~~~

Run all 149 acquired snapshots using tiered scan planning.

Deliver collection analytical outputs.

No automatic processing dispositions.

### PR D — processing decisions

Historical plan only. The current operational method reviews existing rights
evidence before disposition and uses `DEFER_RIGHTS` when rights are the blocker.

Create/update processing_decisions.csv under the existing control-plane contract.

Do not use this historical PR sequence to reconstruct old branches; use the
current exact next action in `STATE.md`.

---

## 22. Mature patterns deliberately rejected

This benchmark is also a defense against overengineering.

The Foundation does **not** need to look enterprise-grade by number of services.

It should look mature because:

- facts have owners;
- claims have provenance;
- runs are reproducible;
- checks are reusable;
- results are persisted;
- partiality is honest;
- large-data scans are cost-aware;
- source bytes remain immutable;
- lineage is explicit;
- human review happens at consequential decisions;
- CI prevents evidence-contract regressions.

That is the maturity target.

---

## 23. Design acceptance criteria

This design is ready to move into implementation when reviewers agree that:

- profile.json is descriptive rather than a quality-result dump;
- profile_run.json captures execution reproducibility;
- checks are separate reusable assertions;
- validation results are separate from profile evidence;
- human docs are generated views;
- evidence provenance is mandatory;
- real-interaction and dialect claims cannot be inferred silently;
- rights remain owned by rights.csv;
- the scan strategy avoids unnecessary full reads;
- implementation stays within the existing locked Foundation architecture;
- the 11-source pilot adequately challenges the contract;
- no enterprise dependency is being added without a demonstrated need.

---

## 24. Decision summary

### Adopt now as design patterns

- Great Expectations: validation-result and generated-doc separation;
- dbt: run artifact + logical artifact separation;
- OpenMetadata: profiler versus data-quality separation;
- Soda: reusable check definitions and explicit outcomes;
- whylogs: compact/mergeable one-pass summaries;
- OpenLineage: run/input/output identity and precise lineage;
- DVC/lakeFS: reproducibility and review discipline;
- PyArrow/DuckDB/Polars: metadata-first and pushdown-aware scanning.

### Implement directly in Foundation

- Profile V2 schema;
- profile run artifact;
- evidence/provenance model;
- reusable checks;
- validation results;
- deterministic tiered scanner;
- pilot fixtures;
- CI gates;
- collection analytical outputs.

### Do not install without future evidence

- enterprise catalog/observability servers;
- orchestration platform;
- Spark;
- cloud quality SaaS;
- alternate data version-control platform.

The target is not to imitate a mature stack visually.

The target is to make Foundation behavior mature, inspectable, reproducible, efficient, and defensible.

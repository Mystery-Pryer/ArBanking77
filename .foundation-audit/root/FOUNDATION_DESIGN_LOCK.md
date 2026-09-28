# Foundation Design Lock

Status: **LOCKED FOR IMPLEMENTATION**
Primary consumer: `gcc-bilingual-annotation-evaluation-lab`

This document is the architecture and operating contract for
`arabic-annotation-data-processing-foundations`.

The repository exists to produce trustworthy, reproducible, rights-aware data
and evidence products that can be deliberately consumed by downstream GCC
bilingual annotation and evaluation work.

It is not itself an annotation project.

---

## 1. Mission

The foundation will:

1. identify and register source resources and exact acquired states;
2. preserve original source bytes and provenance;
3. profile what is actually present without guessing;
4. record rights, limitations, contradictions, and uncertainty;
5. make an explicit processing decision for every acquired source snapshot;
6. transform selected sources through versioned, deterministic mappings;
7. validate transformed outputs and retain validation evidence;
8. analyze duplicate/overlap relationships without silently deleting evidence;
9. publish immutable, versioned foundation releases for the GCC annotation lab.

The terminal product is **a controlled foundation release**, not merely a
Parquet file, DuckDB database, or research report.

---

## 2. Repository boundary

### Foundation owns

- source/resource identity;
- snapshot/version identity;
- physical artifact and storage-location identity;
- provenance and lineage;
- source profiling;
- source-reported metadata;
- controlled classifications and their evidence basis;
- rights/access/privacy review;
- transformation mappings and code;
- canonical processed datasets;
- quality, duplicate, overlap, and leakage evidence;
- reference/methodology evidence;
- validation results;
- published foundation releases.

### Foundation does not own

- project-specific annotation units;
- Project 01 labels or rubric;
- severity scales;
- model-output judgments;
- adjudication outcomes;
- project-specific gold/reference answers;
- model selection or evaluation verdicts;
- portfolio claims.

Those belong to `gcc-bilingual-annotation-evaluation-lab`.

---

## 3. Non-negotiable data principles

### 3.1 Source bytes are immutable

Original acquired data is never edited in place.

Processing creates new derived artifacts. It never overwrites the source.

### 3.2 One fact, one authority

The canonical registry/profile/validation record owns a fact. Markdown reports
may explain or summarize facts but must not become a competing authority.

### 3.3 No silent omission

Every acquired snapshot must eventually receive an explicit processing
disposition.

### 3.4 No silent deduplication

Duplicate source rows, overlapping corpora, mirrors, subsets, and derivative
datasets are identified and recorded. They are not silently deleted.

### 3.5 No silent normalization

Source text and source labels are preserved. Any normalized/canonical form is a
separate derived field with a named rule and version.

### 3.6 Unknown remains unknown

Missing evidence is represented as unknown, not filled by intuition.

### 3.7 Contradictions are evidence

When authoritative observations or upstream claims disagree, both are retained
with their evidence until a supported resolution exists.

---

## 4. Evidence states

Material claims use these meanings:

- `UPSTREAM_REPORTED` — explicitly stated by the publisher, paper, README,
  dataset card, or authoritative source;
- `OBSERVED` — directly measured/read from acquired source bytes;
- `DERIVED` — produced by a documented deterministic computation;
- `HUMAN_CLASSIFIED` — an explicit human mapping/classification supported by
  recorded evidence;
- `UNKNOWN` — not verified;
- `CONTRADICTED` — reliable evidence sources disagree.

A controlled taxonomy mapping must never silently upgrade an unknown or
upstream claim into an observed fact.

---

## 5. Arabic and dialect preservation policy

Arabic dialect data is observed language evidence, not prose to be corrected.

Rules:

- preserve `text_raw` exactly;
- do not grammar-correct dialectal Arabic;
- do not convert dialect text to MSA by default;
- do not rewrite spelling because it appears unconventional;
- do not remove repeated letters, spacing variation, punctuation, Arabizi, or
  code-switching from the raw field;
- do not assign Saudi/Gulf/sub-dialect identity from intuition;
- do not classify unusual wording as an error unless an explicit evidence-backed
  task defines it that way;
- normalization, search normalization, transliteration, MSA rendering, or
  English meaning must be separate derived fields;
- normalized equality is not the same as raw-text duplication.

Description precedes interpretation. Uncertainty is preserved.

---

## 6. Five conceptual zones

The repository uses five conceptual zones. They are responsibilities, not a
requirement to copy all bytes into Git.

### SOURCE

Original external/acquired bytes. Immutable.

Large bytes may remain in durable external storage. Git stores identity,
locators, hashes when available, and evidence.

### CONTROL

Registry, rights, taxonomy mappings, processing decisions, contracts, and
lineage.

This is the machine-readable control plane.

### CANONICAL

Selected source data transformed into documented canonical record families,
normally stored as versioned Parquet outside Git when large.

### QUALITY

Profiles, validation results, duplicate/overlap analysis, limitations, and
other processing evidence.

### PRODUCT

Immutable release manifests and consumer-facing documentation describing
exactly what the GCC lab is permitted to consume.

Generated DuckDB/query indexes are conveniences and are never authoritative.

---

## 7. Core identity model

Preserve the relationship:

```text
resource -> snapshot -> artifact -> location
```

- **resource**: conceptual dataset/corpus/document family;
- **snapshot**: one concrete version/sample/split/derived state;
- **artifact**: one exact byte object;
- **location**: one physical locator for an artifact.

Stable IDs must not encode mutable titles, countries, licenses, or inferred
semantics.

---

## 8. Registry authority

Bootstrap only the tables required by the active phase. Do not create empty
infrastructure merely because it may be useful later.

Core authority:

- `resources.csv`
- `snapshots.csv`
- `artifacts.csv`
- `locations.csv`
- `resource_artifacts.csv`
- `snapshot_artifacts.csv`
- `aliases.csv`
- `profiles.csv`
- `rights.csv`
- `taxonomy_mappings.csv`
- `processing_decisions.csv`
- `transformations.csv`
- `transformation_runs.csv`
- `lineage.csv`
- `validations.csv`
- `releases.csv`
- `release_members.csv`

When canonical record sets actually exist, add/use:

- `recordsets.csv`
- `fields.csv`

The registry is metadata/control state. Large corpus bytes do not belong in
these CSVs or in Git.

---

## 9. Per-snapshot operating workflow

After bootstrap, work proceeds source/snapshot by source/snapshot.

### Step 1 — Identify

Verify resource, snapshot, artifact, location, version/revision, and available
strong identity.

Do not merge resources from filename similarity alone.

### Step 2 — Profile

Inspect the source at the depth required for the decision.

Record both:

- profile kind;
- inspection mode.

Examples include full scan, metadata scan, deterministic sample, archive
inventory, bibliographic profile, and methodology review.

A profile must state what was and was not inspected.

### Step 3 — Classify and review current rights evidence

Separate source-reported facts from controlled classifications.

Review the rights/access/use evidence already available at the depth needed to
choose a defensible processing disposition. Exhaustive rights clearance is not a
prerequisite to triage: when rights are the unresolved blocker,
`DEFER_RIGHTS` is the correct disposition.

Before any transformation/release action, the action-specific rights required
for that action must be explicit.

### Step 4 — Decide

Assign exactly one current processing disposition, such as:

- `CANONICALIZE`
- `CANONICALIZE_SELECTED`
- `REFERENCE_ONLY`
- `SOURCE_ONLY`
- `DEFER_RIGHTS`
- `DEFER_TECHNICAL`
- `SUPERSEDED`
- `EXCLUDE_WITH_REASON`

No acquired snapshot may disappear from the workflow without a recorded
decision.

### Step 5 — Map before transforming

Define source field -> canonical field mapping, raw-field preservation,
datatypes, null rules, identifiers, exclusions, and normalization behavior
before running a full transform.

### Step 6 — Transform deterministically

Run versioned code against identified inputs.

A run records:

- transformation/version;
- source snapshot IDs;
- git SHA;
- environment/dependency identity;
- parameters;
- output snapshot IDs;
- run manifest;
- status.

### Step 7 — Validate

Persist validation results.

At minimum, where applicable:

- schema contract;
- row accounting;
- deterministic record identity;
- source locator round trip;
- output identity/hash;
- required raw-field preservation;
- declared exclusion accounting;
- registry/lineage integrity.

A console message saying PASS is not sufficient evidence.

### Step 8 — Cross-source quality

Only after comparable representations exist, inspect exact duplicates,
normalized matches, subsets, derivative relationships, leakage, and selected
near-duplicates.

No relationship automatically implies deletion.

### Step 9 — Publish

Selected validated outputs become members of a versioned foundation release.

The annotation lab consumes the release, not arbitrary internal files.

---

## 10. Canonical record families

Do not force all sources into one giant table.

Candidate families are created only when real source mappings require them,
including:

- `text_instance`
- `review`
- `intent_utterance`
- `conversation_turn`
- `parallel_text`
- `speech_segment`
- `lexicon_entry`
- `ngram_stat`
- `reference_chunk`

Reference literature remains clearly separate from corpus/customer utterance
data.

---

## 11. Duplicate and contradiction policy

Always distinguish:

- exact duplicate bytes;
- duplicate resource identity;
- multiple locations of one artifact;
- duplicate source rows;
- normalized-text matches;
- near-duplicate records;
- subsets/derivatives;
- split leakage;
- contradictory upstream documentation;
- contradiction between upstream claims and observed bytes.

The system must prevent an unresolved contradiction from being presented as a
single settled fact.

---

## 12. Release contract

The foundation's published consumer interface to the GCC lab is a versioned logical release,
for example `AFR-000001`.

A release must identify at minimum:

- release ID and contract version;
- producer Git SHA;
- included canonical snapshots/record sets;
- included reference resources when applicable;
- storage locators/identities for large release assets;
- taxonomy/mapping version(s);
- validation result(s);
- rights/use state for the intended consumer;
- lineage/provenance;
- checksums or strong identities where applicable;
- known limitations.

The GCC lab should pin a specific release with a lock file containing the
release ID, producer Git SHA, and manifest identity.

The consumer must not depend on the foundation's internal working paths.

The machine/consumer-facing producer contract is defined in [CONSUMER_CONTRACT.md](CONSUMER_CONTRACT.md). The GCC lab's consumer-side acceptance procedure is `FOUNDATION_HANDOFF.md` in `Mystery-Pryer/gcc-bilingual-annotation-evaluation-lab`.

Release acceptance certifies the release contract: identity, provenance,
processing reproducibility, declared quality checks, rights/use state, and known
limitations. It does **not** certify upstream labels as gold truth, dialect text
as linguistically "correct," or a dataset as suitable for a project-specific
annotation decision. Those judgments remain explicit downstream decisions.

---

## 13. Efficiency rules

- Do not copy large source data into Git for neatness.
- Do not rescan large immutable sources when existing verified evidence answers
  the current question.
- Use metadata pushdown before full scans where appropriate.
- Deep-profile a large source when downstream use actually requires deeper
  evidence.
- Cache disposable intermediate work outside the authoritative control plane.
- Keep DuckDB and search indexes rebuildable.
- Prefer deterministic Python, Parquet, SQL, JSON/YAML contracts, and simple CI.
- Do not adopt Spark, Airflow, Dagster, dbt, DVC, Great Expectations, vector
  databases, or other infrastructure until a demonstrated need exceeds the
  complexity cost.
- Borrow mature design principles without importing unnecessary frameworks.

---

## 14. Bootstrap and migration order

The verified current-data baseline, physical access model, migration handling,
and processing routes are defined in [CURRENT_DATA_INTAKE_PLAN.md](CURRENT_DATA_INTAKE_PLAN.md). That document is operational detail under this design lock and must not contradict this contract.


The legacy repository is an intake source, not a design authority.

Order:

1. bootstrap this repository's protocol and minimum control plane;
2. freeze an exact legacy intake baseline;
3. migrate useful source identities, provenance, profiles, evidence, and
   processing logic under the new contract;
4. reconcile migration completeness mechanically;
5. relocate any source bytes that would otherwise disappear with the legacy
   repository;
6. continue processing per snapshot under this design;
7. complete selected canonical outputs and cross-source quality work;
8. publish the first accepted foundation release;
9. only then allow the new GCC annotation lab to depend on that release.

Do not migrate project-specific annotation/evaluation workflow into this
foundation.

---

## 15. Completion criteria before GCC annotation work

Foundation readiness for the first GCC release requires:

- every in-scope acquired source accounted for;
- no silent or unresolved identity mapping;
- sufficient profile evidence for every selected release member;
- explicit processing disposition for every in-scope acquired snapshot;
- required rights/use state for every release member;
- transformations reproducible from identified inputs;
- validation evidence retained;
- duplicate/overlap relationships evaluated where relevant;
- raw/source provenance round-trip available;
- release manifest immutable and internally consistent;
- known limitations explicit;
- no unsupported linguistic or metadata inference represented as fact.

The requirement is not "no real-world duplicates or contradictions."

The requirement is:

**no silent mistakes, no untracked duplicates, no unresolved contradiction
presented as fact, no unsupported inference presented as observation, and no
source omitted without an explicit disposition.**

---

## 16. Change control

This document is the design lock.

Implementation may add detail, but it must not silently change these boundaries
or principles.

A material architecture change requires an explicit amendment explaining:

1. the demonstrated problem;
2. why the current design cannot solve it simply;
3. the proposed change;
4. impact on source-of-truth rules, provenance, reproducibility, and the GCC
   consumer contract.

---

## 17. Mature reference patterns used

The architecture deliberately borrows principles rather than frameworks:

- Cookiecutter Data Science: immutable raw inputs, reproducible DAG-style flow,
  and keeping large data outside source control:
  https://cookiecutter-data-science.drivendata.org/opinions/
- Kedro Data Catalog: logical catalog separated from physical dataset storage
  and versioned datasets:
  https://docs.kedro.org/en/latest/catalog-data/data_catalog/
- OpenLineage: distinct dataset, job, and run concepts for lineage:
  https://openlineage.io/docs/next/
- dbt project dependencies: producer-owned stable published interfaces for
  downstream consumers:
  https://docs.getdbt.com/docs/mesh/govern/project-dependencies
- Great Expectations: persisted validation results as durable quality evidence:
  https://docs.greatexpectations.io/docs/0.18/reference/learn/terms/validation_result/
- Hugging Face Dataset Cards: consumer-facing dataset context, intended use,
  language/license metadata, and limitations:
  https://huggingface.co/docs/hub/en/datasets-cards
- MLCommons Croissant: interoperable dataset metadata, provenance, and usage
  restriction descriptions:
  https://mlcommons.org/working-groups/data/croissant/

Croissant and dataset cards are optional product-edge exports/documentation;
they are not internal authorities.


---

## 18. Cross-repository handoff readiness

Before implementation reaches the first GCC release, the foundation must produce
the fields and evidence required by `CONSUMER_CONTRACT.md`.

The foundation does not need to know Project 01's rubric or model provider.
It does need to publish sufficient identity, lineage, validation, rights/use,
limitation, and retrieval information for the lab to make those decisions
without inspecting foundation internals.

The first handoff will be exercised as a real consumer test:

~~~text
build AFR candidate
→ validate producer contract
→ lab performs consumer acceptance
→ repair any contract gap
→ freeze accepted AFR release
→ lab pins release
~~~

A release is not considered consumer-ready merely because canonical Parquet was
generated.


---

## 19. Implementation contract

Implementation detail under this design lock is owned by:

- `CONTROL_PLANE_CONTRACT.md` — concrete machine-readable control-plane schemas;
- `MIGRATION_RUNBOOK.md` — pinned legacy migration and reconciliation procedure;
- `PROCESSING_METHOD.md` — practical targeted source-processing and simple Lab handoff method;
- `AGENTS.md` — mandatory implementation operating rules;
- `STATE.md` — repository-level phase and exact next action;
- `scripts/migration/` — deterministic migration code;
- `scripts/validation/` — repository/control-plane validation.

These files may operationalize the locked architecture but must not silently
change its boundaries or evidence principles.

Authority is by concern, not by document age:

- this design lock owns architecture/invariants;
- `CONTROL_PLANE_CONTRACT.md` + registry tables own schemas/mutable facts;
- `PROCESSING_METHOD.md` owns the current per-source method;
- `WORKFLOW_GUARDRAILS.md` owns Git/PR/CI flow;
- `STATE.md` owns the current phase/blocker/next action.

Historical intake, migration, profiling design/checkpoint, and incident documents
are evidence/rationale after their phase closes and cannot become a current work
queue.

The first executable gate is migration reconciliation, not corpus
transformation.

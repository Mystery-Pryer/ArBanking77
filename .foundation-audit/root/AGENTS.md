# AGENTS.md

## Purpose

These rules govern implementation work in
`arabic-annotation-data-processing-foundations`.

The repository's purpose is to produce verified, reproducible, rights-aware
Arabic/GCC foundation releases for downstream annotation/evaluation.

The design is already locked. Implementation must preserve that purpose.

### Authority by concern

When documents disagree, use the authority for that concern rather than the newest
or most detailed prose:

- architecture/invariants → `FOUNDATION_DESIGN_LOCK.md`;
- machine-readable schemas and mutable fact owners → `CONTROL_PLANE_CONTRACT.md`
  plus `control/registry/*`;
- current phase, blocker and exact next action → `STATE.md`;
- current source-processing method → `PROCESSING_METHOD.md`;
- Git/PR/CI execution mechanics → `WORKFLOW_GUARDRAILS.md`;
- consumer-facing release promise → `CONSUMER_CONTRACT.md`.

`CURRENT_DATA_INTAKE_PLAN.md`, `MIGRATION_RUNBOOK.md`, Profile V2 design/
checkpoint documents, and incident reports are historical/evidence documents once
their phase is complete. They must never override the authorities above.

---

## 1. Required startup sequence

Before substantive work:

1. read `AGENTS.md`;
2. read `STATE.md` and its exact next action/blocker;
3. read `FOUNDATION_DESIGN_LOCK.md`;
4. read `CONTROL_PLANE_CONTRACT.md`;
5. read `PROCESSING_METHOD.md` for source/decision/mapping/transformation work;
6. read `WORKFLOW_GUARDRAILS.md`;
7. list open pull requests and inspect applicable validation state before starting work;
8. read `CONSUMER_CONTRACT.md` only when release/consumer rights are in scope;
9. read `CURRENT_DATA_INTAKE_PLAN.md` only for historical intake/storage/baseline
   evidence;
10. read `MIGRATION_RUNBOOK.md` only for migration audit/replay;
11. read `PROFILE_V2_MATURITY_BENCHMARK.md` only when changing the profiling
    contract or its rationale.

Do not use chat history as the authority when repository state exists.

If repository/PR state shows unfinished substantive work, a branch based on an
unmerged branch, contradictory evidence, or required validation that cannot be
reproduced, enter RECOVERY MODE from `WORKFLOW_GUARDRAILS.md`.

Do not enter or remain in recovery merely because old superseded branches still
exist. Recovery ends when current `main` contains the evidence and controls
needed for the current exact next action.

---

## 2. Architecture lock

Do not redesign the foundation during implementation unless a concrete defect
shows that the locked design cannot be implemented safely.

Implementation may add detailed schemas, validators, mappings, transformation
code, evidence and release artifacts, but must not silently change:

- resource → snapshot → artifact → location identity;
- immutable source bytes;
- one fact / one authority;
- no silent omission/deduplication/normalization;
- unknown remains unknown;
- contradiction preservation;
- GCC consumes only accepted AFR releases.

---

## 3. Migration source

The legacy repository is an **intake source only**.

Verified baseline:

~~~text
repository:
Mystery-Pryer/gcc-bilingual-annotation-evaluation-lab-temp

commit:
83f6b3e16272d5a752ad1140986d2ef85bfb9569
~~~

Do not import later legacy changes silently.

A different source commit requires an explicit baseline amendment and
reconciliation.

---

## 4. Canonical ownership

Maintain one mutable owner for each fact.

- identity/storage → `control/registry/*.csv`;
- migrated/deep profiles → `quality/profiles/` + `profiles.csv`;
- rights/use state → `rights.csv`;
- processing disposition → `processing_decisions.csv`;
- transformation definition → `transformations.csv`;
- run state → `transformation_runs.csv`;
- lineage → `lineage.csv`;
- validation result → `validations.csv` + referenced result artifact;
- release → `releases.csv` + immutable release manifest;
- release membership → `release_members.csv`;
- repository continuity → `STATE.md`.

Markdown may explain facts but must not compete with the machine-readable owner.

---

## 5. Migration discipline

During control-plane migration:

- preserve stable legacy IDs unless a demonstrated defect requires remapping;
- preserve contradictions and aliases;
- never invent missing SHA-256 values;
- do not reclassify rights from license intuition;
- do not infer new action permissions from legacy broad fields;
- do not copy empty legacy infrastructure merely for symmetry;
- rewrite profile paths deterministically and copy their referenced artifacts;
- reconcile exact verified baseline counts;
- explain every count difference before declaring migration complete.

---

## 6. Rights discipline

Legacy rights rows are seed evidence, not GCC-use clearance.

The old `training_use`, `evaluation_use`, `commercial_use`, and
`public_portfolio_use` fields are all UNKNOWN at the verified baseline.

Therefore new consumer-action fields start UNKNOWN until re-reviewed:

- private_local_processing;
- human_annotation;
- external_hosted_model_inference;
- derived_private_analysis;
- public_aggregate_reporting;
- public_example_redistribution;
- public_raw_redistribution.

Preserve the legacy license/access/redistribution evidence and source reference.

---

## 7. Processing discipline

Do not begin a full transformation simply because a source is acquired.

Per snapshot:

~~~text
identify
→ review existing profile + existing rights evidence
→ processing decision
→ deepen only if that decision is blocked
→ mapping for CANONICALIZE / CANONICALIZE_SELECTED
→ dry run
→ transform
→ validate
→ cross-source quality
→ release candidate
~~~

A partial profile is not automatically a defect.

The 149-snapshot Profile V2 rollout and collection analysis are the current
decision-support baseline. Do not replay or deepen collection profiling merely
because historical checkpoints exist.

Before any new source-byte read or deep profile, state all four:

- the exact decision/mapping question that is blocked;
- why existing profile/registry evidence cannot answer it;
- the bounded row/byte/file inspection budget;
- the stop condition and authority that will receive the new evidence.

If the existing evidence supports a defensible processing disposition, stop
profiling and record the decision.

`DEFER_RIGHTS`, `DEFER_TECHNICAL`, `REFERENCE_ONLY`, `SOURCE_ONLY`,
`SUPERSEDED`, and `EXCLUDE_WITH_REASON` are valid progress. Do not resolve every
unknown before using them.

Source-byte work uses the registered operational location owned by the control
plane. `resources.csv:primary_url` is provenance/discovery metadata, not an
automatic processing locator. Do not silently fetch an upstream URL when a
registered location is unavailable; update/select a registered location
explicitly.

---

## 8. Evidence integrity

Never claim:

- bytes were verified when not read;
- hashes exist when unknown;
- a profile was full when partial;
- a license permits an action without evidence;
- a transformation succeeded without persisted validation;
- a source is duplicate merely from normalized similarity;
- an upstream label is gold truth;
- a dialect/subdialect identity from intuition.

Blocked/unknown/deferred are valid outcomes.

---

## 9. Learner authorship

This is a private learning/portfolio repository as well as a working producer.

For important portfolio capabilities, the learner should understand and be able
to defend the material decision before AI turns it into polished code or prose.

Important learner-owned reasoning includes, when relevant:

- identifying source grain/schema;
- deciding processing disposition;
- designing source-to-canonical mappings;
- interpreting duplicate/overlap evidence;
- distinguishing anomaly from confirmed defect;
- investigating root cause;
- choosing/justifying validation controls;
- explaining release limitations and supported conclusions.

AI may teach, scaffold, write routine code, automate checks, and review work.
It must not silently become the source authority or make a core judgment that is
later presented as independent learner work.

Do not create a second curriculum/tracker for this repo. Learning evidence comes
from the real implementation artifacts and the learner's ability to explain and
debug them.

---

## 10. Flow control and Git workflow

`WORKFLOW_GUARDRAILS.md` is mandatory.

Core rules:

- repository WIP limit is **1 open PR total**, regardless of title/type;
- every PR targets `main` directly;
- never stack substantive work on an unmerged branch;
- do not start downstream substantive work while the current PR is draft,
  under validation/reconciliation, or unmerged;
- when evidence invalidates an upstream fact, stop dependent work and reconcile the authority before continuing;
- process/incident-repair work may interrupt only to restore repository health and must not add unrelated feature scope.

Use a branch + pull request for substantive implementation changes.

A commit represents a coherent reviewable unit.

A checkpoint is not Done because code exists or a run succeeded. Before the next checkpoint may start:

- all scoped evidence and authoritative facts are reconciled;
- relevant validators pass on the latest commit SHA;
- checkpoint docs being merged are no longer `ACTIVE`;
- `STATE.md` contains the correct post-merge next action;
- the PR is merged to `main`;
- `main` is re-read/verified after merge.

If CI cannot execute because no runner/steps start, classify it as infrastructure failure and follow the single retry/fallback rule in `WORKFLOW_GUARDRAILS.md`. Do not invent a second CI policy here, treat platform failure as data failure, or use it as a reason to replay historical work.

Do not create version-copy files when Git history owns versioning.

---

## 11. Implementation order

Migration is reconciled and the 149-snapshot Profile V2 rollout plus collection
analysis are integrated. The current priority is therefore:

1. create `processing_decisions.csv` for the 149 acquired snapshots from the
   existing evidence baseline;
2. use deferred dispositions instead of launching broad evidence collection
   where a decision is not yet supportable;
3. deepen profile/rights evidence only for a named decision or mapping blocker;
4. create mappings only for `CANONICALIZE` / `CANONICALIZE_SELECTED` snapshots;
5. dry-run and validate one mapping at a time;
6. run full deterministic transforms only after mapping validation;
7. perform relevant cross-source quality checks on comparable outputs;
8. assemble an internally validated AFR candidate;
9. publish AFR ACCEPTED;
10. Lab verifies/consumes the accepted release through its own handoff procedure.

Do not replay completed Profile V2 checkpoints as a prerequisite for step 1.

Do not start Project 01 work in this repository.

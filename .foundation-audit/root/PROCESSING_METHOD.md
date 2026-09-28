# Foundation Processing Method

Status: **IMPLEMENTATION METHOD — PRIVATE LEARNING / PORTFOLIO**

This document defines the practical method used after migration is reconciled.

The goal is simple:

> turn selected Arabic/GCC sources into trustworthy, reusable Foundation data
> that the GCC annotation/evaluation lab can consume without redoing source
> cleaning, provenance work, or basic data-quality investigation.

This is a private learning/portfolio repository. The method should demonstrate
good professional practice without recreating enterprise data-platform
governance.

---

## 1. Target scope

The first Foundation release should prioritize sources that are plausibly useful
for later GCC bilingual annotation/evaluation work, especially where evidence
supports:

- Saudi/GCC Arabic;
- customer service/support;
- retail/e-commerce/business interactions;
- intents and utterances;
- conversational turns;
- reviews/opinion text;
- bilingual/parallel text where genuine alignment exists.

These are priorities, not automatic inclusion rules.

Do not infer dialect, domain, or business relevance from intuition.

Sources outside the first-release priority remain registered and accounted for.

---

## 2. Per-source workflow

The collection-wide profiling baseline is complete enough to begin processing
decisions: all 149 acquired/profiled snapshots are represented in the Profile V2
rollout and collection analysis. That baseline is decision support, not a reason
to rescan the collection.

For each acquired snapshot:

~~~text
IDENTIFY
→ REVIEW EXISTING PROFILE + EXISTING RIGHTS EVIDENCE
→ DECIDE DISPOSITION / PRIORITY
→ DEEPEN ONLY IF THE DECISION IS BLOCKED
→ MAP ONLY IF CANONICALIZING
→ DRY RUN
→ TRANSFORM
→ VALIDATE
→ CROSS-SOURCE DQ
→ RELEASE DECISION
~~~

### 2.1 Identify

Confirm:

- resource/snapshot/artifact/location;
- exact source/version;
- available hash/identity;
- source grain.

### 2.2 Reuse profile evidence

Use the migrated/Profile V2 evidence first.

Deep-profile only when the existing evidence is insufficient to make the next
processing decision or a concrete mapping decision.

Do not rescan large immutable data merely because implementation has started,
because a historical checkpoint once proposed a scan, or because unresolved
questions exist.

A new scan requires a bounded evidence request:

~~~text
blocked_question
why_existing_evidence_is_insufficient
max_rows_or_files_or_bytes
deterministic_sampling_rule
stop_condition
evidence_owner
~~~

If those fields cannot be stated, do not scan.

Full-stream reads are justified only when a complete transform itself requires
the input, an exact metric/hash is necessary for a named decision, or exact
cross-source fingerprinting is required.

### 2.3 Operational source boundary

Source-byte work uses a registered artifact location from
`control/registry/locations.csv`.

Default rule:

- use the location marked `is_primary=true` for the artifact;
- `resources.csv:primary_url` is provenance/discovery metadata, not an automatic
  processing locator;
- a registered secondary location may be used only when the run/evidence records
  that choice;
- never silently fetch/sync/compare an unregistered upstream URL because the
  registered location is inconvenient or unavailable;
- changing the operational source means changing the control-plane location
  authority in a reviewed PR, not editing prose.

Project-controlled forks/mirrors should be registered as pinned locations when
they are the intended processing input. This keeps source execution reproducible
without creating a second prose authority.

### 2.4 Decide disposition and processing priority

Use the single processing-disposition vocabulary owned by
`CONTROL_PLANE_CONTRACT.md`:

~~~text
CANONICALIZE
CANONICALIZE_SELECTED
REFERENCE_ONLY
SOURCE_ONLY
DEFER_RIGHTS
DEFER_TECHNICAL
SUPERSEDED
EXCLUDE_WITH_REASON
~~~

Do not create a second controlled relevance taxonomy.

For first-release sequencing, record the reason in `decision_basis` / evidence
and simply process the strongest direct candidates first. The target-scope
priorities in Section 1 guide sequencing; they are not another source-of-truth
field.

### 2.5 Rights evidence and escalation

Use existing `rights.csv` evidence as an input to the processing decision.

Do not perform exhaustive rights research for all 149 snapshots before triage.
If rights are the blocker for an otherwise useful source, record `DEFER_RIGHTS`
and the missing action/evidence. Detailed rights review is required before a
source is actually canonicalized/released for an intended use, not before every
collection-level disposition can be recorded.

For data likely to become future model-evaluation cases, pay particular
attention to:

- human annotation;
- external hosted-model inference;
- private derived analysis.

Unknown stays unknown.

### 2.6 Map before transform

Document:

- source record grain;
- source fields;
- target canonical family;
- raw fields preserved;
- source labels preserved;
- derived fields;
- null/type rules;
- record-ID rule;
- explicit exclusions.

Do not let transformation code silently become the mapping specification.

### 2.7 Dry run

Before a large transform:

1. process a deterministic small subset;
2. inspect output;
3. validate IDs/schema/provenance/raw preservation;
4. fix the mapping if necessary;
5. then run the full transform.

### 2.8 Transform

Run deterministic versioned code.

Preserve raw source text.

Any normalization, transliteration, MSA rendering, English meaning, or derived
classification must be separate from raw fields.

### 2.9 Validate

Where applicable verify:

- schema;
- row accounting;
- unique/stable record IDs;
- provenance back to source;
- raw-field preservation;
- explicit exclusion counts/reasons;
- output identity/hash;
- lineage/registry integrity.

Persist the validation result.

### 2.10 Cross-source DQ

After comparable outputs exist, investigate:

- exact duplicates;
- normalized matches;
- subsets/derivatives;
- train/dev/test leakage;
- relevant overlap;
- contradictions.

Detecting a duplicate relationship does not automatically mean deleting a
record.

---

## 3. Canonical output

Do not force every source into one table.

Likely record families remain:

~~~text
intent_utterance
conversation_turn
review
text_instance
parallel_text
speech_segment
lexicon_entry
ngram_stat
reference_chunk
~~~

For a text-bearing record intended for later Lab use, preserve enough common
identity to trace it:

~~~text
foundation_record_id
recordset_id
source_snapshot_id
source_record_locator
raw text / family-specific raw fields
source metadata/labels
clearly separated derived metadata
~~~

The exact schema depends on the real source.

---

## 4. What the Lab receives

The Lab should not consume Foundation working folders or internal databases.

Foundation publishes an immutable versioned release such as:

~~~text
AFR-000001
~~~

The release should provide, at minimum:

~~~text
manifest
member index
canonical member locations/identities
provenance/lineage
validation evidence
rights/use state
checksums/strong identities where available
known limitations
~~~

Large canonical Parquet files may remain in approved external storage.

The release manifest points to them.

---

## 5. Simple Foundation → Lab handoff

The handoff is intentionally simple:

~~~text
FOUNDATION
process selected sources
→ validate
→ publish ACCEPTED AFR release

        ↓

GCC LAB
verify release identity / rights / limitations
→ Stage 0 project definition
→ Stage 1 chooses needed release members
→ foundation.lock.json
→ derive project cases
~~~

The Lab does not need to negotiate a machine-readable request with Foundation
before processing.

Foundation already knows its downstream purpose from the shared project design.

If a later real project needs something the release does not contain, that
becomes a normal new processing requirement/release—not a standing enterprise
handshake system.

---

## 6. Efficient implementation order

After migration reconciliation and the completed Profile V2 collection
rollout/analysis:

1. create `processing_decisions.csv`;
2. record one explicit processing disposition for the 149 acquired snapshots
   using current evidence;
3. use `DEFER_RIGHTS` / `DEFER_TECHNICAL` rather than launching broad
   collection-wide investigation when evidence is insufficient;
4. sequence the strongest directly useful `CANONICALIZE` /
   `CANONICALIZE_SELECTED` candidates first;
5. deepen only the profile/rights evidence that blocks a named decision or
   mapping;
6. create source-specific mappings only for sources that will be canonicalized;
7. dry-run and validate each mapping;
8. run full transforms;
9. add relevant cross-source duplicate/overlap analysis;
10. assemble the first AFR release and let the Lab consume it through the
    existing handoff procedure.

Do not try to finish every source before producing useful validated Foundation
products if the release contract can honestly describe what is and is not
included.

---

## 7. Learning / portfolio value

The work should make the reasoning visible.

Good portfolio evidence can come from real tasks such as:

- profiling a messy source;
- identifying source grain/schema;
- finding duplicates or contradictions;
- designing a raw-preserving mapping;
- reconciling rows after filtering;
- validating provenance;
- investigating a DQ issue;
- comparing multiple source structures;
- publishing a reproducible release.

Do not create artificial complexity merely to demonstrate more tools.

The strongest story is:

~~~text
messy source
→ evidence/profile
→ processing decision
→ mapping
→ deterministic transform
→ DQ investigation
→ validation
→ controlled release
→ downstream use
~~~

---

## 8. Tool rule

Default to the simplest tool that makes the result reproducible:

- Python 3.12;
- PyArrow/Polars;
- Parquet ZSTD;
- DuckDB when SQL helps;
- CSV/JSON/YAML control files;
- pytest / GitHub Actions.

Do not add distributed processing, orchestration, catalog servers, or pipeline
frameworks unless the actual workload demonstrates the need.

---

## 9. First-release completion test

The first release is ready when:

- selected members are useful for the intended Lab direction;
- each included recordset has documented grain/schema/provenance;
- raw source evidence is preserved;
- rights needed for intended use are explicit;
- transformations are reproducible;
- row accounting and validation pass;
- relevant duplicate/overlap findings are documented;
- known limitations are explicit;
- the Lab can locate and verify release members without reading Foundation
  internals.

That is sufficient for a strong private learning/portfolio workflow.

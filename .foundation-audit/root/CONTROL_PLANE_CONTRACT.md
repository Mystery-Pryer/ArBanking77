# Foundation Control Plane Contract

Status: **IMPLEMENTATION CONTRACT v1**
Applies to: active Foundation control-plane implementation

This document defines the concrete CSV authorities used by the locked
architecture.

Large source/canonical bytes remain outside Git when appropriate.

---

## 1. Directory layout for the active phase

~~~text
control/
└── registry/

quality/
├── profiles/
└── migration/

scripts/
├── migration/
└── validation/

products/
└── releases/           # created when the first AFR candidate exists
~~~

Do not create other empty infrastructure without a real responsibility.

---

## 2. Existing identity/control tables migrated from the legacy baseline

### resources.csv

Header:

~~~text
resource_id
canonical_name
resource_type
upstream_id
doi
primary_url
publisher_or_creator
publication_date
countries_reported
varieties_reported
languages
modality
domains
task_families
origin_class
annotation_class
description
limitations
last_verified
~~~

### snapshots.csv

~~~text
snapshot_id
resource_id
snapshot_kind
version
upstream_revision
acquired_at
created_at
is_live
acquisition_state
declared_records
verified_records
declared_bytes
verified_bytes
content_fingerprint
schema_hash
is_preferred
notes
~~~

### artifacts.csv

~~~text
artifact_id
sha256
bytes
filename
mime_type
format
artifact_kind
archive_parent_artifact_id
member_path
first_verified
notes
~~~

### locations.csv

~~~text
location_id
artifact_id
storage_class
locator
is_primary
access_verified
last_verified
notes
~~~

During migration, legacy-repository-dependent locators are made explicit:

- legacy `git:<path>` becomes a repository-and-commit-qualified legacy Git
  locator;
- legacy `github_release:<tag>/<asset>` becomes a repository-qualified legacy
  GitHub Release locator.

They remain valid historical/relocation evidence but are not treated as
Foundation-controlled durable locations. They must be relocated before the
legacy repository is deleted.

### Location authority rule

For every registered artifact:

- exactly one location must be marked `is_primary=true`;
- that primary location is the default operational retrieval location;
- other verified locations are mirrors/fallbacks, not automatic alternatives;
- `resources.csv:primary_url` is descriptive provenance/discovery metadata and
  does not authorize an unregistered network fetch;
- source-specific processing must use a registered location;
- if a different fork/mirror should become operational, register/pin it and
  change the primary flag in the control plane under review.

A run may deliberately use a registered secondary location, but the run/evidence
must record that choice. Silent fallback to an upstream URL is forbidden.

### resource_artifacts.csv

Create only when at least one row exists.

~~~text
resource_id
artifact_id
role
is_preferred
notes
~~~

### snapshot_artifacts.csv

~~~text
snapshot_id
artifact_id
role
is_preferred
notes
~~~

### aliases.csv

~~~text
alias
alias_type
canonical_resource_id
source_context
notes
~~~

### profiles.csv

~~~text
profile_id
snapshot_id
profiler_version
profile_json_path
profile_md_path
schema_path
generated_at
profile_status
row_count
schema_hash
warnings_count
notes
~~~

Profile paths are repository-relative under `quality/profiles/`.

### lineage.csv

~~~text
lineage_id
from_type
from_id
relation
to_type
to_id
transformation_id
run_id
notes
~~~

---

## 3. Rights table

The Foundation keeps general source-rights evidence plus the consumer-action
states required by the GCC release contract.

### rights.csv

~~~text
rights_id
resource_id
snapshot_id
license_name
license_url
access_class
redistribution_class
private_local_processing
human_annotation
external_hosted_model_inference
derived_private_analysis
public_aggregate_reporting
public_example_redistribution
public_raw_redistribution
pii_risk
sensitivity_class
terms_evidence_ref
evidence_state
verified_on
notes
~~~

Action-state vocabulary:

~~~text
ALLOWED
RESTRICTED
UNKNOWN
NOT_APPLICABLE
~~~

During baseline migration all seven action-state fields are initialized to
`UNKNOWN`.

Reason: every legacy action-specific permission field is UNKNOWN at the pinned
baseline; no new permission may be inferred from license name or
redistribution class alone.

The following legacy facts are preserved directly:

- license name / URL;
- access class;
- redistribution class;
- PII/sensitivity state;
- terms evidence reference;
- verification date;
- notes.

Migrated access/redistribution classifications use evidence state
`HUMAN_CLASSIFIED` and retain their evidence reference.

A later rights review may create a new/updated rights row under normal Git
history and evidence rules.

---

## 4. Active implementation tables added after migration

### processing_decisions.csv

One current explicit processing disposition per in-scope acquired snapshot.

~~~text
decision_id
snapshot_id
disposition
decision_basis
evidence_refs
decided_on
decided_by
notes
~~~

Allowed disposition:

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

### transformations.csv

~~~text
transformation_id
name
version
code_path
purpose
deterministic
output_contract_path
notes
~~~

### transformation_runs.csv

~~~text
run_id
transformation_id
started_at
completed_at
status
git_sha
environment_hash
input_snapshot_ids
output_snapshot_ids
parameters_json
run_manifest_path
validation_status
notes
~~~

### validations.csv

~~~text
validation_id
subject_type
subject_id
validation_type
validator_name
validator_version
executed_at
status
result_path
errors_count
warnings_count
git_sha
notes
~~~

Validation status:

~~~text
PASS
FAIL
PASS_WITH_WARNINGS
BLOCKED
~~~

### releases.csv

~~~text
release_id
release_contract_version
producer_git_sha
created_at
release_status
manifest_path
manifest_sha256
member_count
validation_summary_path
rights_summary_path
known_limitations_path
supersedes
superseded_by
notes
~~~

Release status:

~~~text
CANDIDATE
ACCEPTED
SUPERSEDED
RETRACTED
~~~

### release_members.csv

~~~text
release_id
member_id
member_role
product_type
recordset_id
artifact_id
location_id
row_count
schema_version
validation_ids
rights_ids
known_limitations
notes
~~~

---

## 5. Canonical-record tables created only when real canonical data exists

### recordsets.csv

~~~text
recordset_id
snapshot_id
name
record_family
grain
primary_key_fields
schema_path
row_count
description
~~~

### fields.csv

~~~text
recordset_id
field_name
data_type
nullable
semantic_role
source_field
controlled_vocabulary
description
~~~

Do not create empty `recordsets.csv` or `fields.csv` during migration.

---

## 6. Legacy tables intentionally not migrated when empty

At the verified baseline these contain zero rows and are therefore not migrated
as empty infrastructure:

- resource_artifacts.csv;
- recordsets.csv;
- fields.csv;
- transformations.csv;
- transformation_runs.csv;
- taxonomy_mappings.csv.

If future Foundation work requires one, create it under this contract at that
time.

---

## 7. Migration path rewrite

Legacy profile references such as:

~~~text
profiles/RES-.../SNP-.../profile.json
~~~

become:

~~~text
quality/profiles/RES-.../SNP-.../profile.json
~~~

The migration script copies all referenced profile JSON/Markdown/schema files
and validates their existence.

---

## 8. Baseline reconciliation gate

The first migrated control plane must reconcile:

~~~text
resources                     189
snapshots                     196
artifacts                     656
locations                     665
snapshot_artifact_links       664
aliases                       267
rights_rows                    61
lineage_edges                   4
acquired_snapshots            149
profile_rows                  149
~~~

Additional verified baseline checks:

~~~text
HF_PRIVATE_BUCKET locations          495
CHATGPT_LIBRARY locations            106
GIT locations                         37
GITHUB_RELEASE locations              27
artifacts with SHA-256                67
artifacts without SHA-256            589
artifacts with multiple locations      9
~~~

Legacy GIT/GITHUB_RELEASE locators must be repository-qualified during
migration.

Differences are not accepted without an explicit migration action/evidence
record.

---

## 9. Hash rule

Known SHA-256 values are preserved.

Blank SHA-256 remains blank.

The migration itself does not invent or derive hashes unless it reads the
corresponding bytes and records that verification as new evidence.

---

## 10. Consumer compatibility

This control plane must be capable of producing the fields promised by
`CONSUMER_CONTRACT.md`.

Internal registry structure is not itself the GCC consumer API.

The consumer API remains an immutable accepted `AFR-xxxx` release.

# Foundation State

> Canonical repository-level continuity and exact next action.

## Current position

~~~text
Foundation phase: PROCESSING_ACTIVE
Migration baseline: 83f6b3e16272d5a752ad1140986d2ef85bfb9569
Migration status: RECONCILED
First AFR release: NOT_STARTED
Collection profiling baseline: COMPLETE — 149-snapshot Profile V2 rollout and collection analysis integrated
Current session: FOUNDATION / S05
Session status: OPEN
Repository blocker: DEGRADED — private-repository GitHub-hosted runner provisioning is unreliable. This does not require replaying profiling work. Source-specific execution should use registered project-controlled locations/environments with working validation where available; Foundation integration still requires applicable validation evidence.
Exact next action: Create control/registry/processing_decisions.csv for all 149 acquired snapshots using the existing Profile V2 collection analysis and current rights evidence. Do not run a new scan unless a specific snapshot disposition cannot be defended from current evidence; record the bounded evidence gap before any inspection.
~~~

## Verified migration baseline

~~~text
resources: 189
snapshots: 196
artifacts: 656
locations: 665
snapshot_artifact_links: 664
aliases: 267
rights_rows: 61
lineage_edges: 4
acquired_snapshots: 149
profile_rows: 149
~~~

## Phase values

Use only:

~~~text
IMPLEMENTATION_PREP
MIGRATION_ACTIVE
MIGRATION_RECONCILED
PROCESSING_ACTIVE
AFR_CANDIDATE
AFR_ACCEPTED
~~~

## Session states

~~~text
OPEN
CLOSED
~~~

## State update rule

Update this file only when one of these changes:

- foundation phase;
- migration status;
- first AFR status;
- collection profiling baseline;
- current session;
- exact next action;
- repository-level blocker.

Per-snapshot processing state belongs to the control plane, not here.

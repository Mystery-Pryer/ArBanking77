# Foundation Workflow Guardrails

Status: **MANDATORY EXECUTION POLICY**

This policy exists to prevent partially completed work stacks, stale downstream
assumptions, hidden parallel work, and work that appears implemented but is not
integrated.

The Foundation is a linear producer workflow. Flow reliability takes priority
over starting the next work item.

## 1. Start gate

Before any substantive work:

1. read `AGENTS.md`, `STATE.md`, and this file;
2. list open pull requests;
3. inspect the applicable validation evidence for the active PR;
4. confirm the active PR is based directly on `main`;
5. confirm there is no contradictory source evidence or unresolved prerequisite
   for the exact next action;
6. confirm the proposed work advances the current phase rather than replaying a
   historical checkpoint already represented on `main`.

If those checks fail, enter **RECOVERY MODE**. A hosted-runner incident by
itself does not justify replaying prior data/profile work.

## 2. Work-in-progress limit

**Repository WIP limit: 1 open PR total.**

PR title/type does not create an exception. `Checkpoint:`, `Process:`,
`Recovery:`, `Incident:`, and any other substantive PR all consume the same
single WIP slot.

If an incident must interrupt active work, either repair it in the current PR
when scope remains coherent, or explicitly close/supersede the active PR before
opening the incident PR. Do not maintain two active PRs.

Substantive work must become visible as a draft PR after its first repository
commit. Old preserved branches with no active PR are history, not WIP.

## 3. No stacked PRs

Every PR branch starts from the current `main` and targets `main` directly.

Do not base new substantive work on an unmerged branch.

Do not start downstream substantive work while the current PR is draft,
under validation/reconciliation, or unmerged.

If parallel thinking is useful, keep it in notes. Do not create another
implementation branch/PR.

## 4. Anti-overprocessing gate

Profiling and inspection are means to a decision, not completion goals.

Before opening source bytes, record the exact blocked decision/mapping question,
why current evidence is insufficient, a bounded inspection budget, and a stop
condition.

Rules:

- do not rerun collection-wide profiling after the validated 149-snapshot
  rollout/analysis unless the profiling contract or registered evidence changes;
- do not reread an immutable source merely because another checkpoint starts;
- do not resolve every unresolved question before assigning a valid deferred or
  non-canonicalizing disposition;
- do not map/transform `REFERENCE_ONLY`, `SOURCE_ONLY`, `DEFER_RIGHTS`,
  `DEFER_TECHNICAL`, `SUPERSEDED`, or `EXCLUDE_WITH_REASON` snapshots;
- stop recovery as soon as `main` contains what the current exact next action
  requires. Chronological replay of old branches is not a goal.

## 5. Stop-the-line rule

When new evidence invalidates an upstream fact or assumption:

1. stop dependent implementation immediately;
2. identify the authoritative fact owner;
3. reconcile the authority and persisted evidence;
4. mark dependent work stale/superseded where necessary;
5. rerun validation on the repaired latest SHA;
6. only then resume downstream work.

Examples include changed row counts, source identity/hash mismatches, rights changes, schema/grain corrections, and lineage corrections.

A downstream artifact built on a known-invalid premise must never be treated as progress.

## 6. Definition of Done

A work item is **Done** only when all of the following are true:

1. the scoped implementation and evidence are complete;
2. authoritative counts, identities, mappings, rights, lineage, and explanatory docs are reconciled;
3. repository/workflow validation passes on the **latest commit SHA**;
4. any checkpoint documentation being merged is no longer marked `ACTIVE`;
5. the PR is based on `main`, has no unresolved prerequisite PR, and is mergeable;
6. `STATE.md` states the correct post-merge next action;
7. the PR is merged to `main`;
8. `main` is re-read/verified after merge;
9. only after steps 1-8 may the next substantive branch/PR be started.

Written code, a successful local run, an uploaded artifact, or an open PR is
not by itself completion.

## 7. CI / workflow incident handling

Treat CI infrastructure failure separately from product/data failure.

If a workflow completes with no executed steps, no assigned runner, or another
clear runner-start failure:

1. record it as a CI/runner incident, not as code/data failure;
2. retry the exact same SHA at most once;
3. if the retry still cannot execute, stop changing code merely to provoke CI;
4. use the single validation fallback below only when its scope fits;
5. keep WIP=1 and continue from the current `STATE.md` next action rather than
   replaying historical branches.

### Single validation fallback during confirmed hosted-runner failure

A PR may be integrated without green hosted CI only when **all** are true:

- the exact SHA failed twice before any workflow step executed;
- the PR is the only open PR and targets `main`;
- the changed-file scope is limited to process/docs, control-plane
  CSV/JSON/specifications, mappings, or validation/framework code;
- there is no new/changed transformation execution code, source/canonical data,
  or ACCEPTED release artifact;
- all applicable checks for the exact head are reproduced independently
  (compilation plus repository/control-plane/schema/framework validators);
- the PR records the failed run attempts, changed-file list, exact commands and
  results used as fallback evidence;
- `main` is re-read immediately after merge.

This fallback exists to prevent a hosted-runner incident from freezing planning,
processing decisions, source-location control, mappings, and repository-health
repairs.

It **cannot** be used to accept:

- transformation execution code whose behavior has not been exercised;
- canonical transformed data;
- transformation-run success;
- validation results for transformed data;
- release candidates or ACCEPTED releases.

Source-specific execution may occur in a registered project-controlled
repository/environment with working validation, but Foundation acceptance must
still record the applicable execution/validation evidence.

Do not use historical successful commits as a reason to reconstruct old branch
chronology. Recovery is driven only by the minimum requirement for the current
exact next action.

## 8. Recovery mode

RECOVERY MODE is mandatory when any of these is true:

- more than one PR is open;
- a PR is based on another unmerged branch;
- latest-SHA CI is failed/unknown for work being treated as complete;
- source evidence contradicts a fact used downstream;
- `STATE.md` does not match actual repository/PR state.

Recovery order:

1. preserve branches/commits so work is not lost;
2. identify the last trustworthy integration point on `main`;
3. identify the **minimum missing capability/evidence for the current exact next
   action**;
4. recover only that minimum unit from `main`; do not replay history by default;
5. close or explicitly supersede invalid/stale sibling or descendant PRs;
6. validate and merge the chosen unit;
7. re-read `main`;
8. **exit recovery immediately** when the current phase can proceed;
9. resume normal WIP=1 flow.

Recovery completeness is determined by present-phase readiness, not by reaching
the tip of an old branch stack.

## 9. CI-enforced controls

`scripts/validation/validate_workflow_guardrails.py`, `scripts/validation/validate_framework_consistency.py`, the control-plane validator, and Repository Quality enforce the controls that can be checked mechanically:

- every PR must target `main`;
- only one PR may be open;
- every ready PR must have the Definition-of-Done attestations checked;
- ready checkpoint work and `main` may not contain checkpoint documents still marked `ACTIVE`;
- `STATE.md` must contain exactly one non-empty exact next action;
- framework phase/status documents cannot contradict `STATE.md`;
- every artifact has exactly one primary registered location;
- active-phase control-plane tables use the contracted schema;
- a present `processing_decisions.csv` covers every acquired snapshot exactly once.

Human/agent judgment is still required for semantic reconciliation, but workflow mechanics must not depend on memory.

`Repository Quality` is the universal lightweight repository gate.
`Profile V2 Regression` is a targeted/supplementary workflow for Profile V2
paths or explicit manual runs; do not configure it as a universal required
check for unrelated PRs, because a path-skipped required workflow can remain
pending and block merging.

## 10. Research basis

This policy adapts established practices to this repository:

- Google Engineering Practices: keep changes small, self-contained, test-backed, and do not break the build:
  https://google.github.io/eng-practices/review/developer/small-cls.html
- GitHub protected-branch/status-check guidance: required checks must pass on the latest SHA before integration:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- DORA: work in small batches to shorten feedback loops and reduce instability:
  https://dora.dev/capabilities/working-in-small-batches/
- The Kanban Guide: explicitly define workflow and control work in progress:
  https://kanbanguides.org/the-kanban-guide/
- GitHub Actions: a path-filtered required workflow can remain pending when
  skipped, so targeted Profile V2 regression is supplementary rather than a
  universal required check:
  https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs

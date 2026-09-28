# CI Runner Incident — 2026-09-28

Status: **MITIGATED — HOSTED RUNNER PROVISIONING INCIDENT**

## Observed symptom

GitHub Actions Repository Quality runs are being created, but the `validate`
job fails before any workflow step executes.

Observed evidence:

- ArBanking Checkpoint 9B PR #44, workflow run `36399497486`:
  `runner_id=0`, no runner name, `steps=[]`.
- Workflow-guardrail PR #45, workflow run `36403775531`, attempt 1:
  `runner_id=0`, `steps=[]`.
- Same PR/run, attempt 2 on the same head SHA:
  `runner_id=0`, `steps=[]`.

The same-SHA retry therefore reproduced the failure before checkout, Python setup,
or any repository validator could run.

## Classification

Do **not** classify these runs as code, transformation, mapping, or data-quality
failures. No repository step executed.

The exact external root cause was not proven from available evidence. Do not
attribute the incident to billing, repository configuration, code, or data
without direct evidence. The only supported conclusion is that the affected
jobs failed before repository steps executed.

## Operating decision

The incident no longer defines the Foundation work queue.

Current operating rules are owned by `WORKFLOW_GUARDRAILS.md` and `STATE.md`.
Hosted-runner failure must not trigger historical replay or broad reprocessing.

- eligible non-transform execution work may use the single documented validation
  fallback after two same-SHA zero-step failures and exact-head independent
  validation;
- source-specific execution may run in a registered project-controlled execution
  location with independent validation;
- transformation execution/canonical outputs/releases still require applicable
  execution and validation evidence before acceptance.

This incident report is evidence/history only.

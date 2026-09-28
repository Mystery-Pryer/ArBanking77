# Arabic Annotation Data Processing Foundations

Producer repository for verified, reproducible, rights-aware Arabic/GCC data
and evidence products deliberately consumed by downstream annotation and
evaluation work.

Primary consumer: `gcc-bilingual-annotation-evaluation-lab`.

The foundation preserves source provenance, profiles and classifies data without
speculation, transforms selected sources through explicit versioned mappings,
retains validation/quality evidence, and publishes controlled foundation
releases.

**Architecture and operating contract:** [FOUNDATION_DESIGN_LOCK.md](FOUNDATION_DESIGN_LOCK.md)

**Historical verified intake baseline (not current work queue):** [CURRENT_DATA_INTAKE_PLAN.md](CURRENT_DATA_INTAKE_PLAN.md)

Implementation must follow the design lock before migration or processing work
begins.


**Producer-side consumer contract:** [CONSUMER_CONTRACT.md](CONSUMER_CONTRACT.md)

Primary downstream consumer:
`Mystery-Pryer/gcc-bilingual-annotation-evaluation-lab`.

The foundation publishes versioned `AFR-xxxx` releases; the lab accepts them
through its own `FOUNDATION_HANDOFF.md`. The lab must not consume arbitrary
foundation working files.


## Implementation

**Concrete control-plane schemas:** [CONTROL_PLANE_CONTRACT.md](CONTROL_PLANE_CONTRACT.md)

**Historical pinned migration/replay procedure:** [MIGRATION_RUNBOOK.md](MIGRATION_RUNBOOK.md)

**Practical post-migration processing method:** [PROCESSING_METHOD.md](PROCESSING_METHOD.md)

**Current implementation state and exact next action:** [STATE.md](STATE.md)

Operational rule: historical intake, migration, profiling-design, checkpoint, and
incident documents explain evidence/history only. They do not override
`STATE.md`, `PROCESSING_METHOD.md`, `CONTROL_PLANE_CONTRACT.md`, or
`WORKFLOW_GUARDRAILS.md` for current execution.

**Mandatory implementation/AI operating rules:** [AGENTS.md](AGENTS.md)

**2026-09-28 workflow breakdown postmortem and prevention controls:**
[quality/operations/FRAMEWORK_BREAKDOWN_POSTMORTEM_2026-09-28.md](quality/operations/FRAMEWORK_BREAKDOWN_POSTMORTEM_2026-09-28.md)

Implementation sequence:

~~~text
verified legacy baseline
→ control-plane migration
→ mechanical reconciliation
→ legacy-dependent storage relocation
→ per-snapshot processing decisions
→ canonical transformations
→ validation / duplicate-overlap review
→ internal AFR candidate validation
→ publish ACCEPTED AFR
→ Lab verifies/consumes the accepted release
~~~

No corpus transformation begins before migration reconciliation.

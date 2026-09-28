# Foundation Migration Runbook

Status: **HISTORICAL REPLAY/AUDIT RUNBOOK — MIGRATION RECONCILED**

Migration is already reconciled on current `main`.

This runbook is retained only to audit or deliberately replay the pinned legacy
migration. It must not be interpreted as the current next action.

This runbook covers only migration/reconciliation of the verified legacy control
plane into the Foundation.

It does not start canonical corpus transformation.

---

## 1. Pinned source

~~~text
Repository:
Mystery-Pryer/gcc-bilingual-annotation-evaluation-lab-temp

Commit:
83f6b3e16272d5a752ad1140986d2ef85bfb9569
~~~

Use an exact checkout of that commit.

Do not migrate arbitrary legacy `main`.

---

## 2. Pre-flight

Before running migration:

1. Foundation branch is current;
2. legacy repo is checked out at the pinned commit;
3. no uncommitted target migration output exists;
4. Python 3.12 is available;
5. `STATE.md` moves to `MIGRATION_ACTIVE` when actual execution begins.

---

## 3. Execute migration

From the Foundation repository:

~~~bash
python scripts/migration/migrate_legacy_control_plane.py \
  --legacy-root /path/to/gcc-bilingual-annotation-evaluation-lab-temp
~~~

The script must fail if the legacy Git SHA is not the pinned baseline.

Before writing any target file, the migration script also preflights the pinned
source assumptions:

- exact verified table counts;
- storage-class counts;
- SHA-256 coverage and multi-location count;
- all expected-empty legacy tables are still empty;
- legacy action-use rights fields remain UNKNOWN;
- every referenced profile artifact exists;
- required Stage 2/3 migration evidence exists;
- legacy GIT/GITHUB_RELEASE locators have the expected source form.

If preflight fails, the target remains untouched.

Expected output:

~~~text
control/registry/
quality/profiles/
quality/migration/
~~~

---

## 4. What the migration copies

Directly migrated machine-readable authority:

- resources;
- snapshots;
- artifacts;
- locations;
- snapshot-artifact links;
- aliases;
- profiles registry;
- lineage.

Migrated with deterministic transformation:

- rights;
- legacy GIT / GITHUB_RELEASE locators are repository-qualified and flagged as
  legacy-dependent so they cannot be mistaken for Foundation paths.

Copied evidence:

- all profile JSON/Markdown/schema files referenced by `profiles.csv`;
- Stage 2 reconciliation summary;
- Stage 2 registry summary;
- Stage 3 profile audit summaries needed to prove the baseline.

Not migrated merely because it exists:

- old architecture documents;
- old project/inception structure;
- legacy status/continuity;
- acquisition workflows;
- empty registry tables;
- project-specific annotation/evaluation artifacts.

Useful legacy code is reference material, not automatically authoritative code.

---

## 5. Validate structure

Run:

~~~bash
python scripts/validation/validate_control_plane.py --expect-baseline
~~~

This checks:

- required headers;
- unique IDs;
- referential integrity;
- known SHA-256 format;
- acquired-snapshot profile coverage;
- profile file existence;
- profile schema hashes;
- rights vocabulary;
- exact migration baseline counts;
- storage distribution;
- SHA-256 coverage;
- multi-location artifact count;
- qualified legacy-dependent locators.

A console PASS is only useful because the generated migration summary and
control files are persisted and reviewable.

---

## 6. Reconciliation review

Read:

~~~text
quality/migration/MIGRATION_SUMMARY.json
quality/migration/RECONCILIATION.md
~~~

Confirm the exact verified counts.

If a count differs:

1. stop;
2. identify the specific objects;
3. classify the difference:
   - migrated;
   - intentionally superseded;
   - external-only;
   - relocated;
   - excluded with reason;
   - not applicable;
4. record the action;
5. rerun migration/validation.

Do not hand-edit counts to match.

---

## 7. Rights migration review

Verify that:

- license/access/redistribution evidence survived;
- all new action-specific use fields are UNKNOWN;
- no hosted-model permission was inferred;
- evidence references remain present.

Current rights evidence is reviewed when assigning a processing disposition; deeper action-specific rights review happens later when an intended transformation/release action requires it.

---

## 8. Legacy-dependent storage review

After registry reconciliation, identify locations that depend on the disposable
legacy repository:

- GITHUB_RELEASE;
- GIT paths;
- any locator whose owner/path disappears when legacy is deleted.

Do not delete/retire an old location until the new Foundation-controlled
location is verified.

HF private bucket locations may remain if durable and valid.

---

## 9. Migration completion gate

Migration becomes `MIGRATION_RECONCILED` only when:

- baseline counts reconcile;
- every acquired snapshot has migrated profile evidence;
- registry validation passes;
- required legacy-dependent objects are identified for relocation;
- migration summary is committed;
- no authority still depends on an undocumented legacy path.

Then the next phase is per-snapshot processing decisions.

---

## 10. What does not happen yet

Do not during this migration step:

- choose Project 01 cases;
- normalize Arabic;
- deduplicate rows silently;
- create final canonical schemas from intuition;
- deep-scan all large datasets unnecessarily;
- infer rights for Groq/Gemini;
- publish AFR-000001.

Those happen only after migration evidence supports the relevant decision.

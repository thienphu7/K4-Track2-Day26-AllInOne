# Role 1 validation — 2026-10-14

This is the historical role 1 checkpoint. Role 2 has since been integrated;
the current combined results and answer adapter are in `SUBMISSION_REVIEW.md`.

## Scope and handoff

Role 1 owns the defensive gateway, answer safety helpers, defensive prompt,
and defense regression tests. Role 2 owns the prosecution detectors and attack
deck refinements saved in `person2.patch`. That patch has not been applied.

The supplied `person1.bundle` restored commit `a4126e3`, authored by
Hoang Thien Phu Le at 11:56:28 +07:00 on 2026-10-14. The follow-up closes
ambiguous header and cross-learner anchor paths, and admits the official
roster card through its documented skill-to-wire mapping.

`git apply --check person2.patch` succeeds on this role 1 version. Role 2 can
apply its saved patch on top of the updated main branch without redoing its work.
No changes were made to `kit/`, `bots/`, `fixtures/`, `deck/`, or `eval/`.

## Rubric coverage

| Area | Defensive behavior | Practical limit |
|---|---|---|
| Enforcement / authority | Known tools and masks, trusted peer admission, audience and learner checks, signed delegation verification when supplied | Registry observations must come from a trusted caller |
| Protocol / writes | Live context leases, write scope, fresh provenance, If-Match, idempotency and rate windows | An authorized call is not proof of a successful write; reconcile ambiguous results |
| Routing / economy | Header routing, deprecated-tool rewrite, narrow catalogs, estimated cost and reserve | Replica freshness needs observed provenance; cost depends on actual returned rows |
| Grounding / safety | Retrieved citation membership, explicit injection signals, private-fragment redaction, equation checks, required-field gate | Membership does not prove semantic truth; patterns do not recognize every injection |
| Answer quality | Prompt requires required fields, conflict disclosure and grounded abstention | ANSWER bypasses the gateway; the answer assembler must call `prepare_answer` |

## Reproduce on Windows

Python 3.12.14; pytest 9.1.1; no third-party runtime dependencies in `agent/`.
The official student world `df8c55dabb35` was downloaded from the upstream release.
Its ZIP SHA256 matched the published checksum:
`e05327c0bd88b2b1ee9c9194a4bee5535964360d97d462144773d02686705810`.
No referee `truth.json` was present. The world and virtual environment are ignored.

```powershell
$env:PYTHONUTF8 = '1'
.venv/Scripts/python.exe -m pytest tests/ -q
.venv/Scripts/python.exe -m pytest tests/ -q --deselect tests/test_isolation.py::test_run_probe_vectors_unsandboxed_baseline
.venv/Scripts/python.exe -m kit.gate_no_key
.venv/Scripts/python.exe validate_deck.py deck/deck.json deck/lineup.json --world kit/world/df8c55dabb35
.venv/Scripts/python.exe spar.py --bot rookie --as defender --seed 1 --quiet
.venv/Scripts/python.exe spar.py --bot operator --as defender --seed 1 --quiet
.venv/Scripts/python.exe spar.py --bot adversary --as defender --seed 1 --quiet
```

The full suite exposed an existing Windows platform failure:
`test_run_probe_vectors_unsandboxed_baseline` calls `msvcrt.open`, which is not
exported by that library. The failing code is in the protected kit; it was
not edited. With only that test deselected, the final suite reports
**4,635 passed, 7 skipped, 1 deselected**. This is not a clean full-suite pass.

`kit.gate_no_key`: PASS, zero violations. Gateway smoke demo: PASS.
Deck validation: zero failures, five existing proxy warnings; this does not
prove the live lethality band and does not include role 2 refinements.

| Defender spar, seed 1 | Student HP | Bot HP | Result |
|---|---:|---:|---|
| rookie | 100 | 100 | draw |
| operator | 20 | 20 | draw |
| adversary | 72 | 0 | student wins |

Spar uses canned tool plans and answers, resets its gateway/context each exchange,
and substitutes bot components for roles outside `--as defender`. These results
exercise the gateway, not live model reasoning, `prompt.md`, `prepare_answer`,
or the complete two-person submission. Semantic referee classes remain pending
locally. A sealed final submission is left to the combined role 1 + role 2 stage.

# Integrated submission review — 2026-10-14

## Assessment

The role 2 checkpoint (`5ff5e2c`, Nguyen Dat) implemented eight rubric classes:
fixture precision 1.000, recall 0.471, F1 0.640. It was a valid partial build,
not evidence of maximum rubric coverage. Its deck and prosecutor were merged
with the existing role 1 work while preserving both authors and role 1 fixes.

The completed version has evidence candidates for all 17 classes, a working
ANSWER-gated loop adapter, and counterexample/integration tests. On the public
40-fixture set it proves all 34 labelled defects, including all near misses,
with precision, recall and F1 all 1.000. It remains silent on the six clean
fixtures; false, unproven, rejected, error and timeout counts are all zero.

This reaches the maximum measured public fixture result, **not a guarantee of
maximum tournament points**. Eight classes require blind semantic adjudication;
the hidden referee truth and live tournament engine are deliberately absent.
The detector patterns do not cover every phrasing, and a finite spar sample
cannot prove the globally best lineup or the live lethality band.

## Work completed after the role checkpoints

- Added stale-read proof from the public drift metadata, plus narrow semantic
  evidence patterns for the eight previously empty adjudicated hooks.
- Added protocol checks for partial results without continuation and span
  citations whose successful frame reads omitted body.
- Kept the four-claim, one-per-family, causal deduplication and 400-character
  argument limits. Actual proof references accompany each claim.
- Distinguished changed If-Match/lease retries from unchanged retries.
- Resolved citation spans and replica-agnostic anchors according to kit syntax,
  in both defense and prosecution; opposite explicit replicas remain distinct.
- Fixed query budget estimates to include the server's five default rows and
  normalized model-provided numeric limit strings before execution.
- Checked private fragments in structured answer fields, empty/nested required
  fields, and delivered final answers through `agent.defender.DefenderAgent`.
- Tested quoted injection/refusal, qualified replica counts, changed retry
  preconditions, safe/unsafe ANSWER delivery and no-I/O prosecution paths.

`DefenderAgent` is an adapter for the normal kit loop and authoritative arena
environment. Callers must choose it and supply the defensive prompt; it does
not replace the arena's gateway enforcement. The supplied `spar.py` uses canned
answers, so adapter behavior is validated by integration tests rather than spar.

The 16 drift paths in `eval/drift_paths.py` come only from the public student
world `df8c55dabb35/drift.json`. Rebuild the snapshot for another world. No hidden
truth, fixture labels, model endpoint or credentials enter the prosecutor.

## Contract and validation

| Requirement | Result |
|---|---|
| Editable source only | No tracked changes to `kit/`, `bots/`, `fixtures/` against shipped commit `6a68efd` |
| Standard-library runtime / denied imports | Submission AST scan passes; no-key gate passes, zero violations |
| Gateway synchronous / pure decisions | Defense tests check authorization, routing, budgets, writes, leases and no file access |
| Prosecutor synchronous / no I/O / deadline / quotas | All public paths tested without file I/O; scorer reports no errors/timeouts; family and causal quotas tested |
| Deck shape | 14 cards: 10 attacks, 4 blanks; unique ten-card lineup; layer/class and real-anchor checks pass |
| Drift legality | Replica-flip path is in the public measured drift set |
| Deck validation | Zero failures, five documented proxy warnings |
| Packaging | `python -m kit.submit --team thienphu7` succeeds without `--force` |
| Full available test suite on Windows | 4,695 passed, 7 skipped, one existing platform test explicitly deselected |

The excluded test is
`tests/test_isolation.py::test_run_probe_vectors_unsandboxed_baseline`: protected
kit code calls `msvcrt.open`, which Windows does not export. This was reproduced
at the role 1 checkpoint and left unchanged under the submission contract.
The reported test result is **not an unqualified full-suite pass**.

The five validator warnings concern its inability to prove the live lethality
band and four pre-existing non-denial defense events. Metadata was not falsified
to silence these warnings. The real validator and submit gate both accept the deck.

## Integrated spar results

`--as all`, student HP then bot HP:

| Bot | Seed 1 | Seed 2 |
|---|---|---|
| rookie | 100–0, win | 100–0, win |
| operator | 100–0, win | 100–0, win |
| adversary | 72–2, win | 48–42, win |

Some protocol defects are deliberately left unclaimed when a higher-weight
infrastructure claim already consumes family A. This follows the one-claim per
family rule rather than indicating another missing hook. Spar resets context
each exchange, so it does not demonstrate cumulative ten-round budget behavior.

## Reproduce

Use Python 3.12 and install pytest in the ignored virtual environment. Install
the official, checksum-verified student world in `kit/world/df8c55dabb35`.

```powershell
$env:PYTHONUTF8 = '1'
.venv/Scripts/python.exe -m pytest tests/ -q --deselect tests/test_isolation.py::test_run_probe_vectors_unsandboxed_baseline
.venv/Scripts/python.exe -m eval.prosecute
.venv/Scripts/python.exe -m kit.gate_no_key
.venv/Scripts/python.exe validate_deck.py deck/deck.json deck/lineup.json --world kit/world/df8c55dabb35
.venv/Scripts/python.exe spar.py --bot rookie --as all --seed 1 --quiet
.venv/Scripts/python.exe spar.py --bot operator --as all --seed 1 --quiet
.venv/Scripts/python.exe spar.py --bot adversary --as all --seed 1 --quiet
.venv/Scripts/python.exe -m kit.submit --team thienphu7
```

The bundle is generated locally at `submissions/thienphu7.bundle` and ignored
by Git. `thienphu7` is the local bundle label; use the registered team name when
submitting to the instructor. Packaging is not an external tournament submission.

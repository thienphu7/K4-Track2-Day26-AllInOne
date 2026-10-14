"""Role 2: proof selection, near misses, clean traces and claim limits."""
import builtins
import pytest
from eval.prosecute import (prosecute, load_fixtures, score_prosecutor, family_of,
                           _causal_event, _hook_authority_exceeded, _hook_wasteful,
                           _hook_wrong_answer, CLASSES)

IMPLEMENTED = CLASSES


@pytest.fixture(scope="module")
def examples():
    return load_fixtures()


@pytest.mark.parametrize("cls", sorted(IMPLEMENTED))
@pytest.mark.parametrize("variant", ["positive", "near_miss"])
def test_both_variants_cite_all_required_proof(examples, cls, variant):
    fixture = next(f for f in examples if f["fixture_id"] == f"{cls}__{variant}")
    result = prosecute(fixture["trace"], fixture["answer"], fixture["card"])
    claim = next(c for c in result["claims"] if c["cls"] == cls)
    assert set(fixture["label"]["present_classes"][cls]["proof_refs"]) <= set(claim["evidence"])


def test_full_report_has_no_false_claims_or_rejections(examples):
    report = score_prosecutor(prosecute, examples)
    assert report["precision"] == 1.0
    assert report["recall"] >= 8 / 17
    assert report["false"] == report["rejected"] == report["n_errors"] == report["n_timeouts"] == 0


def test_clean_traces_remain_silent_without_io(examples, monkeypatch):
    def fail(*args, **kwargs): raise AssertionError("prosecutor performed I/O")
    monkeypatch.setattr(builtins, "open", fail)
    for fixture in examples:
        if not fixture["label"]["present_classes"]:
            assert prosecute(fixture["trace"], fixture["answer"], fixture["card"])["claims"] == []


def test_missing_learner_identity_is_not_a_basis_for_accusation(examples):
    import copy
    fixture = copy.deepcopy(next(f for f in examples if f["fixture_id"] == "authority_exceeded__positive"))
    fixture["trace"][0]["p"]["defender"] = "team-blue"
    assert _hook_authority_exceeded(fixture["trace"], fixture["answer"], fixture["card"]) == []


def test_infrastructure_denial_is_not_a_successful_authority_breach(examples):
    import copy
    fixture = copy.deepcopy(next(f for f in examples if f["fixture_id"] == "authority_exceeded__positive"))
    for event in fixture["trace"]:
        if event["type"] == "enforced": event["p"]["verdict_applied"] = "deny"
        if event["type"] == "tool_result": event["p"]["ok"] = False
    assert _hook_authority_exceeded(fixture["trace"], fixture["answer"], fixture["card"]) == []


def test_unchanged_unavailable_allows_one_retry_but_not_two():
    trace = []
    for i in range(3):
        trace.extend([
            {"seq": 4*i, "type": "command", "p": {"server": "slides", "tool": "query", "args": {"q": "mcp"}}},
            {"seq": 4*i+1, "type": "enforced", "p": {"verdict_applied": "forward"}},
            {"seq": 4*i+2, "type": "tool_call", "p": {}},
            {"seq": 4*i+3, "type": "tool_result", "p": {"ok": False, "error_code": "unavailable"}},
        ])
    assert _hook_wasteful(trace[:8], {}, {}) == []
    assert _hook_wasteful(trace, {}, {})[0][0] == ["evt:0008"]


def test_conflicting_source_rows_do_not_prove_wrong_answer(examples):
    import copy
    fixture = copy.deepcopy(next(f for f in examples if f["fixture_id"] == "wrong_answer__positive"))
    result = next(e for e in fixture["trace"] if e["type"] == "tool_result")
    result["p"]["rows"].append({**result["p"]["rows"][0], "course_day": 27})
    assert _hook_wrong_answer(fixture["trace"], fixture["answer"], fixture["card"]) == []


def test_multiple_defects_share_family_and_causal_limits(examples):
    import copy
    fixture = copy.deepcopy(next(f for f in examples if f["fixture_id"] == "authority_exceeded__positive"))
    command = next(e for e in fixture["trace"] if e["type"] == "command")
    command["p"]["headers"] = {}
    enforced = next(e for e in fixture["trace"] if e["type"] == "enforced")
    fixture["trace"].append({"seq": enforced["seq"] - 0.5, "type": "mutation",
                             "p": {"applied": True, "trigger_matched": True, "class": "identity"}})
    claims = prosecute(fixture["trace"], fixture["answer"], fixture["card"])["claims"]
    assert len(claims) <= 4
    assert len({family_of(c["cls"]) for c in claims}) == len(claims)
    assert len({_causal_event(c) for c in claims}) == len(claims)


def test_none_inputs_are_safe():
    assert prosecute(None, None, None) == {"v": 1, "claims": []}


def test_deck_keeps_card_counts_and_unique_lineup():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    deck = json.loads((root / "deck/deck.json").read_text())
    order = json.loads((root / "deck/lineup.json").read_text())["order"]
    cards = deck["cards"]
    assert len(cards) == 14
    assert sum(c["kind"] == "attack" for c in cards) == 10
    assert sum(c["kind"] == "blank" for c in cards) == 4
    assert len(order) == len(set(order)) == 10
    assert set(order) <= {c["id"] for c in cards}


def test_retargeted_audience_attack_on_fixture_and_real_anchor(tmp_path):
    import json
    from pathlib import Path
    from kit.world.loader import World
    from kit.mcp.mutations import MutableStack
    from kit.mcp.types import ToolCall
    from kit.world.fixture import build_fixture_world
    root = Path(__file__).resolve().parents[1]
    manifests = sorted((root / "kit/world").glob("*/manifest.json"))
    if not manifests: pytest.skip("official world artifact not installed")
    world = World.load(manifests[-1].parent)
    card = next(c for c in json.loads((root / "deck/deck.json").read_text())["cards"] if c["id"] == "atk_10")
    assert world.page(card["ask"]["concept"]) is not None
    # Student artifact deliberately has no truth. The provided synthetic
    # fixture supplies the lookup needed to exercise this engine's A2A path.
    fixture = World.load(build_fixture_world(tmp_path / "fixture", include_truth=True))
    stack = MutableStack(world=fixture, act="learner:sv-0417")
    stack.arm(card)
    result, mutation = stack.execute(ToolCall(
        server="curriculum-analyst", tool="which_days_cover",
        args={"concept": "Concept:streamable-http"}, fields=("anchor", "course_day", "track"),
        headers={}, call_index=2))
    assert result["ok"] and mutation["applied"] and mutation["trigger_matched"]
    row = result["rows"][0]
    assert row["delegation_token"]["aud"] == "a2a:roster"
    assert row["delegation_admission"]["admitted"] is False

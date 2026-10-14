"""Pure safety helpers for retrieved content and final answers.

Gateway checks instruction-shaped note arguments. prepare_answer is an explicit
answer-assembly hook; ANSWER bypasses Gateway.decide, so the caller must invoke
this helper. Citation membership proves retrieval, not semantic correctness.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any, Iterable, Mapping

# kit.world.anchor is a collaborator's file (workspace hard rule 2). Present
# and stable as of this writing; degraded gracefully so `check_grounding`
# still runs (with the anchor-syntax leg of the check skipped, not silently
# treated as passing) if it is ever briefly unimportable.
try:
    from kit.world.anchor import Anchor, AnchorSyntaxError
    _ANCHOR_AVAILABLE = True
except ImportError:  # pragma: no cover - collaborator file
    Anchor = None  # type: ignore[assignment]
    AnchorSyntaxError = ValueError  # type: ignore[assignment, misc]
    _ANCHOR_AVAILABLE = False

__all__ = [
    "GroundingResult",
    "check_grounding",
    "InjectionScanResult",
    "scan_for_injected_instructions",
    "RedactionResult",
    "redact",
    "ArithmeticCheckResult",
    "verify_arithmetic",
    "abstention_policy",
    "prepare_answer",
]


# ---------------------------------------------------------------------------
# 1. GROUNDING — real, working.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GroundingResult:
    grounded: bool
    cited: tuple[str, ...]
    ungrounded: tuple[str, ...]  # cited, syntactically valid, but never retrieved this exchange
    malformed: tuple[str, ...]  # cited but not even valid Anchor syntax


def check_grounding(
    answer: Mapping[str, Any],
    retrieved_anchors: Iterable[str],
    *,
    require_citation: bool = True,
) -> GroundingResult:
    """"Every claim traces to a returned anchor" (this task's own brief),
    made concrete: every string in `answer["cited_anchors"]` must (a) parse
    as valid `ns:slug[/rev][/idx][#span]` syntax (`kit.world.anchor.Anchor`)
    and (b) be a member of `retrieved_anchors` — the anchors YOUR exchange
    actually got back from a `tool_result` this round, not anchors you
    recognise from having seen them before, and not anchors you are
    inferring exist.

    `retrieved_anchors` is YOUR responsibility to assemble honestly — the
    right source is the union of every `tool_result.anchors` your agent
    received this exchange (CONTRACTS.md 5.2's `tool_result` event field),
    never something wider like "every anchor this world index contains".
    Passing a wider set than what you actually retrieved makes this
    function agree with citations that are `ungrounded` in the sense that
    actually matters (CONTRACTS.md 6.1's rubric class) even though this
    function would call them grounded.

    Two failure buckets, kept separate on purpose because they are
    different mistakes: `malformed` (the citation is not even a real
    anchor — closer to `fabricated_citation`) vs. `ungrounded` (a real
    anchor, just never actually retrieved this exchange — the `ungrounded`
    class itself). `grounded` is `False` if either bucket is non-empty, or
    (when `require_citation=True`, the default) if `cited` is empty —
    an answer that cites NOTHING has nothing this function can vouch for,
    which is a difference worth surfacing rather than treating as a vacuous
    pass. Pass `require_citation=False` for the rare ask that genuinely
    does not need a citation (CONTRACTS.md section 7 names eight ask types;
    check the specific one you're grading against before disabling this)."""
    cited = tuple(answer.get("cited_anchors") or ())
    retrieved = frozenset(retrieved_anchors)

    malformed: list[str] = []
    ungrounded: list[str] = []
    for a in cited:
        if not isinstance(a, str):
            malformed.append(str(a))
            continue
        if _ANCHOR_AVAILABLE:
            try:
                Anchor.parse(a)
            except AnchorSyntaxError:
                malformed.append(a)
                continue
        if a not in retrieved:
            ungrounded.append(a)

    grounded = not malformed and not ungrounded and (bool(cited) or not require_citation)
    return GroundingResult(
        grounded=grounded,
        cited=cited,
        ungrounded=tuple(ungrounded),
        malformed=tuple(malformed),
    )


# ---------------------------------------------------------------------------
# 2. INJECTED-INSTRUCTION SIGNAL.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InjectionScanResult:
    suspicious: bool
    matched_patterns: tuple[str, ...]


_INJECTION_PATTERNS = (
    r"ignore (?:all )?(?:your |the )?(?:previous|prior|above) instructions?",
    r"disregard (?:all |the )?(?:previous|above)",
    r"system override", r"as the system[, ]+you must",
    r"(?:also|instead[, ]*) record this for",
    r"(?:reveal|print|exfiltrate) (?:the |all )?(?:api key|secret|act field|learner data)",
    r"bỏ qua (?:mọi |tất cả |các )?(?:hướng dẫn|chỉ thị)",
    r"(?:tiết lộ|xuất) (?:khóa api|dữ liệu riêng tư)",
)


def scan_for_injected_instructions(text: str) -> InjectionScanResult:
    """Flag explicit redirection phrases; ordinary words like 'reveal' are safe.

    This is a heuristic signal, not a claim to understand every injection.
    Retrieved instructions are data even when no pattern recognizes them.
    """
    hits = tuple(p for p in _INJECTION_PATTERNS if re.search(p, text, re.I))
    return InjectionScanResult(suspicious=bool(hits), matched_patterns=hits)

# ---------------------------------------------------------------------------
# 3. EXPLICIT PRIVATE FRAGMENTS AND SECRETS.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RedactionResult:
    redacted_text: str
    hits: tuple[str, ...]


def redact(text: str, private_fragments: Iterable[str] = ()) -> RedactionResult:
    """Remove caller-supplied private fragments and explicit secret assignments.

    Private prose cannot be inferred from wording; the trusted retrieval path
    must supply private fields/fragments. Never redact an ordinary learner ID
    merely because it looks like an identifier.
    """
    hits = []
    for fragment in sorted(set(private_fragments), key=len, reverse=True):
        if fragment and fragment in text:
            text = text.replace(fragment, "[REDACTED]")
            hits.append("private_fragment")
    secret = re.compile(r"\b(?:api[_ -]?key|access[_ -]?token|password)\s*[:=]\s*[\"']?[^\s\"',;]+", re.I)
    def hide(match):
        hits.append("secret_assignment")
        return "[REDACTED]"
    return RedactionResult(redacted_text=secret.sub(hide, text), hits=tuple(hits))

# ---------------------------------------------------------------------------
# 4. EXPLICIT EQUATION VERIFICATION.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ArithmeticCheckResult:
    checked: bool
    ok: bool | None
    detail: str


def verify_arithmetic(text: str) -> ArithmeticCheckResult:
    """Check explicit binary equations with Decimal; no eval or inferred facts.

    Numeric source grounding needs source values, which this one-argument API
    does not carry. No equation means 'unchecked', never 'verified'.
    """
    number = r"-?\d+(?:\.\d+)?"
    equations = re.findall(rf"({number})\s*([+*/×÷-])\s*({number})\s*=\s*({number})", text)
    if not equations:
        return ArithmeticCheckResult(False, None, "no supported equation to verify")
    with localcontext() as context:
        context.prec = 40
        for left, op, right, claimed in equations:
            a, b, c = Decimal(left), Decimal(right), Decimal(claimed)
            try:
                if op == "+": actual = a + b
                elif op == "-": actual = a - b
                elif op in ("*", "×"): actual = a * b
                else:
                    if b == 0: return ArithmeticCheckResult(True, False, "division by zero")
                    actual = a / b
            except InvalidOperation:
                return ArithmeticCheckResult(True, False, "invalid arithmetic")
            if actual != c:
                return ArithmeticCheckResult(True, False, "equation does not hold")
    return ArithmeticCheckResult(True, True, "all supported equations hold")

# ---------------------------------------------------------------------------
# 5. ABSTENTION POLICY — real, naive.
# ---------------------------------------------------------------------------


def abstention_policy(grounding: GroundingResult) -> bool:
    """`True` iff you should abstain (answer with an honest "insufficient
    grounding" rather than submit this ANSWER as-is). Naive on purpose: it
    reuses the ONE guardrail this file can actually vouch for
    (`check_grounding`) and nothing else — your own confidence, a
    conflicting second source (`unflagged_conflict`, CONTRACTS.md 6.1),
    and the ask's own `require`d fields (CONTRACTS.md section 7) all go
    completely unweighed here. CONTRACTS.md's own prompt guidance
    (kit/loop/prompt.py's `SYSTEM_PROMPT`) puts it plainly: "a wrong answer
    costs more than an honest 'insufficient grounding'" — this function is
    the bare floor of that policy, not the ceiling."""
    return not grounding.grounded


def prepare_answer(answer: Mapping[str, Any], retrieved_anchors: Iterable[str], *,
                   required_fields: Iterable[str] = (), private_fragments: Iterable[str] = ()) -> dict:
    """Explicit final-answer gate; returns a safe abstention if checks fail."""
    candidate = dict(answer)
    text = str(candidate.get("text") or "")
    redaction = redact(text, private_fragments)
    candidate["text"] = redaction.redacted_text
    grounding = check_grounding(candidate, retrieved_anchors)
    arithmetic = verify_arithmetic(candidate["text"])
    missing = any(candidate.get(key) is None for key in required_fields)
    if not grounding.grounded or missing or arithmetic.ok is False or redaction.hits:
        return {"text": "Insufficient safe, grounded evidence to answer.",
                "cited_anchors": [], "abstained": True}
    return candidate

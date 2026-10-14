"""Answer-gated kit loop for callers that run a model through an arena environment.

The environment remains the authoritative gateway/execution boundary. This
adapter only checks the delivered ANSWER against this exchange's observations.
It does not execute tools directly or manufacture registry observations.
"""
import json

from kit.loop.agent import Agent
from agent.guardrails import prepare_answer


class DefenderAgent(Agent):
    """Use like kit.loop.Agent, with ask and optional defensive_prompt.

    Pass the contents of prompt.md through defensive_prompt when constructing
    the loop. The normal kit system prompt is retained and the policy appended.
    Observations must be the actual results from the trusted arena environment.
    """
    def __init__(self, model, env, *, ask, defensive_prompt="", private_fragments=(), **kwargs):
        self.ask = dict(ask)
        self.private_fragments = tuple(private_fragments)
        if defensive_prompt:
            kwargs["system_prompt"] = kwargs["system_prompt"] + "\n\n" + defensive_prompt
        super().__init__(model, env, **kwargs)

    def _execute(self, action):
        if action["kind"] == "answer":
            anchors, fragments = set(), list(self.private_fragments)
            for observation in self.observations:
                if observation.get("ok") is not True: continue
                anchors.update(a for a in observation.get("anchors") or () if isinstance(a, str))
                for row in observation.get("rows") or ():
                    if not isinstance(row, dict): continue
                    if isinstance(row.get("anchor"), str): anchors.add(row["anchor"])
                    if row.get("private") is True:
                        fragments.extend(v for v in row.values() if isinstance(v, str))
                    private = row.get("private_fields") or {}
                    if isinstance(private, dict):
                        fragments.extend(v for v in private.values() if isinstance(v, str))
            action["args"] = prepare_answer(action["args"], anchors,
                                             required_fields=self.ask.get("require") or (),
                                             private_fragments=fragments)
            action["raw"] = "ANSWER " + json.dumps(action["args"], ensure_ascii=False)
        return super()._execute(action)

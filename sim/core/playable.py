"""Playable edicts — pause at fat moments, apply one governor bias, resume.

Does nothing unless run_sim(playable=True). Never touches the world RNG.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

from sim.core.governor import Governor


EDICTS: List[Dict[str, str]] = [
    {
        "id": "food",
        "command": "focus food",
        "title": "Feed the people",
        "hurt": "Farms first. Science and army slow.",
    },
    {
        "id": "science",
        "command": "focus science",
        "title": "Pursue science",
        "hurt": "Library, lab, observatory. The town eats less labour.",
    },
    {
        "id": "army",
        "command": "focus army",
        "title": "Raise the army",
        "hurt": "Soldiers eat. Science waits.",
    },
]

REASON_TEXT = {
    "opening": "The tribe looks to you. Where do we put our labour?",
    "era4": "A settlement reached Era 4. What do we pursue?",
    "inquiry": "Inquiry is unlocked. Science is possible. What now?",
    "discovery": "First discovery. Do we double down, or steady the town?",
    "drought": "Drought. Regrowth is thin. How do we answer?",
}

# One decision per tick, this order if several fire together.
REASON_PRIORITY = ("drought", "era4", "inquiry", "discovery", "opening")


@dataclass
class PlayableState:
    policy: str = "first"  # human | first | seeded
    seed: int = 0
    asked: Set[str] = field(default_factory=set)
    last_age_up4: int = 0
    last_discovery: int = 0
    had_inquiry: bool = False
    picker: Optional[Callable[[Dict[str, Any]], str]] = None


def _has_inquiry(settlements: List[Dict[str, Any]]) -> bool:
    return any("inquiry" in (s.get("subjects") or []) for s in settlements)


def detect_reason(
    state: PlayableState,
    tick: int,
    metrics: Dict[str, Any],
    settlements: List[Dict[str, Any]],
    drought_this_tick: bool,
) -> Optional[str]:
    now_inquiry = _has_inquiry(settlements)
    inquiry_new = now_inquiry and not state.had_inquiry
    state.had_inquiry = now_inquiry

    age4 = int(metrics.get("age_up4_events", 0) or 0)
    era4_new = age4 > state.last_age_up4
    state.last_age_up4 = age4

    disc = int(metrics.get("discovery_events", 0) or 0)
    disc_new = disc > state.last_discovery
    state.last_discovery = disc

    candidates = []
    if drought_this_tick and "drought" not in state.asked:
        candidates.append("drought")
    if era4_new and "era4" not in state.asked:
        candidates.append("era4")
    if inquiry_new and "inquiry" not in state.asked and "era4" not in candidates:
        candidates.append("inquiry")
    if disc_new and "discovery" not in state.asked:
        candidates.append("discovery")
    if tick == 0 and "opening" not in state.asked:
        candidates.append("opening")

    for reason in REASON_PRIORITY:
        if reason in candidates:
            return reason
    return None


def _seeded_index(seed: int, reason: str) -> int:
    # Separate from world RNG. Stable for (seed, reason).
    h = (int(seed) * 1000003) ^ (sum((i + 1) * ord(c) for i, c in enumerate(reason)) * 9176)
    return abs(h) % len(EDICTS)


def _print_decision(payload: Dict[str, Any]) -> None:
    reason = payload["reason"]
    tick = payload["tick"]
    print()
    print("=" * 60)
    print(f"  TICK {tick}  —  {reason.upper()}")
    print("=" * 60)
    print(REASON_TEXT.get(reason, reason))
    settlements = payload.get("settlements") or []
    if settlements:
        bits = []
        for s in settlements:
            era = s.get("era", 2)
            pop = s.get("population", 0)
            food = s.get("food_stock", 0)
            bits.append(f"{s.get('id','?')} era{era} pop={pop} food={food:.0f}")
        print("  " + " | ".join(bits))
    print()
    for i, e in enumerate(EDICTS, 1):
        print(f"  [{i}] {e['title']:<18}  {e['hurt']}")
    print()


def _human_pick(payload: Dict[str, Any]) -> str:
    import sys
    _print_decision(payload)
    if not sys.stdin.isatty():
        return EDICTS[0]["id"]
    while True:
        raw = input("Choice [1-3] (Enter=1): ").strip()
        if raw == "":
            return EDICTS[0]["id"]
        if raw in ("1", "2", "3"):
            return EDICTS[int(raw) - 1]["id"]
        for e in EDICTS:
            if raw.lower() == e["id"]:
                return e["id"]
        print("  Pick 1, 2, or 3.")


def pick_edict(state: PlayableState, payload: Dict[str, Any]) -> str:
    if state.picker is not None:
        chosen = state.picker(payload)
    elif state.policy == "human":
        chosen = _human_pick(payload)
    elif state.policy == "seeded":
        chosen = EDICTS[_seeded_index(state.seed, payload["reason"])]["id"]
    else:
        chosen = EDICTS[0]["id"]
    valid = {e["id"] for e in EDICTS}
    return chosen if chosen in valid else EDICTS[0]["id"]


def apply_edict(gov: Governor, brains: Dict[str, Any], edict_id: str, logger, tick: int, reason: str) -> None:
    edict = next(e for e in EDICTS if e["id"] == edict_id)
    status = gov.apply_command(edict["command"])
    bias = gov.bias_weights()
    for brain in brains.values():
        if hasattr(brain, "governor_bias"):
            brain.governor_bias = bias
    logger.event({
        "type": "decision_taken",
        "tick": tick,
        "reason": reason,
        "edict": edict_id,
        "command": edict["command"],
        "status": status,
        "state": gov.to_dict(),
    })
    logger.event({
        "type": "governor_command",
        "tick": tick,
        "command": edict["command"],
        "status": status,
        "state": gov.to_dict(),
        "reason": reason,
    })


def maybe_decide(
    state: PlayableState,
    gov: Governor,
    brains: Dict[str, Any],
    logger,
    tick: int,
    metrics: Dict[str, Any],
    settlements: List[Dict[str, Any]],
    drought_this_tick: bool = False,
) -> Optional[str]:
    reason = detect_reason(state, tick, metrics, settlements, drought_this_tick)
    if reason is None:
        return None
    state.asked.add(reason)
    payload = {
        "tick": tick,
        "reason": reason,
        "prompt": REASON_TEXT.get(reason, reason),
        "choices": list(EDICTS),
        "settlements": [
            {k: s.get(k) for k in ("id", "era", "population", "food_stock", "subjects")}
            for s in settlements
        ],
    }
    logger.event({
        "type": "decision_offered",
        "tick": tick,
        "reason": reason,
        "choices": [e["id"] for e in EDICTS],
    })
    edict_id = pick_edict(state, payload)
    apply_edict(gov, brains, edict_id, logger, tick, reason)
    if state.picker is None and state.policy != "human":
        print(f"  edict @ tick {tick} [{reason}] → {edict_id}")
    return edict_id

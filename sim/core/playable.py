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

# One-time choice after Observatory: farm bonus vs bank knowledge (or auto).
DISCOVERY_EDICTS: List[Dict[str, str]] = [
    {
        "id": "farm",
        "command": "focus food",
        "title": "Claim the farm bonus",
        "hurt": "Spend knowledge for permanent +8% farm yield. Stockpile is gone.",
    },
    {
        "id": "bank",
        "command": "focus food",
        "title": "Bank the knowledge",
        "hurt": "Hold the stockpile. No farm bonus. Growth stays hungry while you wait.",
    },
    {
        "id": "auto",
        "command": "focus science",
        "title": "Auto-claim every discovery",
        "hurt": "Spend as knowledge arrives. Science path races. Food labour suffers.",
    },
]

REASON_TEXT = {
    "opening": "The tribe looks to you. Where do we put our labour?",
    "era4": "A settlement reached Era 4. What do we pursue?",
    "inquiry": "Inquiry is unlocked. Science is possible. What now?",
    "discovery": "Observatory is ready. Knowledge can become farm yield — or stay banked.",
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
    player_ids: Optional[Set[str]] = None


def _has_inquiry(settlements: List[Dict[str, Any]]) -> bool:
    return any("inquiry" in (s.get("subjects") or []) for s in settlements)


def _discovery_opportunity(settlements: List[Dict[str, Any]]) -> bool:
    """True when a town has enough knowledge for a discovery and none yet taken."""
    cost = 40.0  # SETTLEMENT_RULES discovery_cost; kept local to avoid import cycle
    return any(
        float(s.get("knowledge", 0) or 0) >= cost and int(s.get("discoveries", 0) or 0) == 0
        for s in settlements
    )


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

    era4_now = any(int(s.get("era", 2)) >= 4 for s in settlements)
    era4_new = era4_now and "era4" not in state.asked

    # Opportunity-based (before spend). Pending mode leaves knowledge unspent.
    disc_new = _discovery_opportunity(settlements) and "discovery" not in state.asked

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


def _choices_for(reason: str) -> List[Dict[str, str]]:
    if reason == "discovery":
        return list(DISCOVERY_EDICTS)
    return list(EDICTS)


def _seeded_index(seed: int, reason: str, n: int) -> int:
    # Separate from world RNG. Stable for (seed, reason).
    h = (int(seed) * 1000003) ^ (sum((i + 1) * ord(c) for i, c in enumerate(reason)) * 9176)
    return abs(h) % n


def _print_decision(payload: Dict[str, Any]) -> None:
    reason = payload["reason"]
    tick = payload["tick"]
    choices = payload.get("choices") or EDICTS
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
    for i, e in enumerate(choices, 1):
        print(f"  [{i}] {e['title']:<22}  {e['hurt']}")
    print()


def _human_pick(payload: Dict[str, Any]) -> str:
    import sys
    choices = payload.get("choices") or EDICTS
    _print_decision(payload)
    if not sys.stdin.isatty():
        return choices[0]["id"]
    while True:
        raw = input("Choice [1-3] (Enter=1): ").strip()
        if raw == "":
            return choices[0]["id"]
        if raw in ("1", "2", "3"):
            return choices[int(raw) - 1]["id"]
        for e in choices:
            if raw.lower() == e["id"]:
                return e["id"]
        print("  Pick 1, 2, or 3.")


def pick_edict(state: PlayableState, payload: Dict[str, Any]) -> str:
    choices = payload.get("choices") or EDICTS
    if state.picker is not None:
        chosen = state.picker(payload)
    elif state.policy == "human":
        chosen = _human_pick(payload)
    elif state.policy == "seeded":
        chosen = choices[_seeded_index(state.seed, payload["reason"], len(choices))]["id"]
    else:
        chosen = choices[0]["id"]
    valid = {e["id"] for e in choices}
    return chosen if chosen in valid else choices[0]["id"]


def apply_edict(
    gov: Governor,
    brains: Dict[str, Any],
    edict_id: str,
    logger,
    tick: int,
    reason: str,
    player_ids: Optional[Set[str]] = None,
    choices: Optional[List[Dict[str, str]]] = None,
) -> None:
    pool = choices or EDICTS
    edict = next((e for e in pool if e["id"] == edict_id), pool[0])
    command = edict.get("command")
    status = None
    if command:
        status = gov.apply_command(command)
        bias = gov.bias_weights()
        for aid, brain in brains.items():
            if player_ids is not None and aid not in player_ids:
                continue
            if hasattr(brain, "governor_bias"):
                brain.governor_bias = bias
    logger.event({
        "type": "decision_taken",
        "tick": tick,
        "reason": reason,
        "edict": edict_id,
        "command": command,
        "status": status,
        "state": gov.to_dict() if command else None,
    })
    if command:
        logger.event({
            "type": "governor_command",
            "tick": tick,
            "command": command,
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
    sm=None,
) -> Optional[str]:
    reason = detect_reason(state, tick, metrics, settlements, drought_this_tick)
    if reason is None:
        return None
    state.asked.add(reason)
    choices = _choices_for(reason)
    payload = {
        "tick": tick,
        "reason": reason,
        "prompt": REASON_TEXT.get(reason, reason),
        "choices": choices,
        "settlements": [
            {k: s.get(k) for k in ("id", "era", "population", "food_stock", "subjects", "faction", "knowledge", "discoveries")}
            for s in settlements
        ],
    }
    logger.event({
        "type": "decision_offered",
        "tick": tick,
        "reason": reason,
        "choices": [e["id"] for e in choices],
    })
    edict_id = pick_edict(state, payload)
    apply_edict(gov, brains, edict_id, logger, tick, reason, player_ids=state.player_ids, choices=choices)

    # Discovery axis: set permanent mode + optional immediate claim.
    if reason == "discovery" and sm is not None:
        if edict_id == "bank":
            sm.discovery_mode = "bank"
            logger.event({"type": "discovery_mode", "tick": tick, "mode": "bank"})
        else:
            # farm or auto → claim from now on
            sm.discovery_mode = "auto"
            logger.event({"type": "discovery_mode", "tick": tick, "mode": "auto", "claim": edict_id})
            # Force the spend that was held while pending.
            for s in settlements:
                if s.get("faction", "player") == "player":
                    sm._try_discovery(s["id"], s, tick)

    if state.picker is None and state.policy != "human":
        print(f"  edict @ tick {tick} [{reason}] → {edict_id}")
    return edict_id

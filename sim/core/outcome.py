"""Win / lose clock. Rival / poles mode. Never touches the world RNG."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Set


SCIENCE_DISCOVERIES = 2

SCIENCE_REASON = {
    "player": "The west finished the science path first.",
    "rival": "The east finished the science path first.",
    "north": "The north finished the science path first.",
    "south": "The south finished the science path first.",
}

DOMINATION_REASON = {
    "player": "The last other people are gone. The west remains.",
    "rival": "The last other people are gone. The east remains.",
    "north": "The last other people are gone. The north remains.",
    "south": "The last other people are gone. The south remains.",
}


def _towns(settlements: Iterable[Dict[str, Any]], faction: str) -> list:
    return [s for s in settlements if s.get("faction", "player") == faction]


def side_from_world(sm, world, faction: str) -> Dict[str, Any]:
    towns = _towns(sm.all(), faction)
    pop = sum(int(s.get("population") or 0) for s in towns)
    era = max((int(s.get("era") or 2) for s in towns), default=2)
    discoveries = sum(int(s.get("discoveries") or 0) for s in towns)
    observatory = False
    if world is not None:
        for s in towns:
            sid = s.get("id")
            if sid and sm.settlement_has_observatory(sid, world):
                observatory = True
                break
    return {
        "pop": pop,
        "era": era,
        "discoveries": discoveries,
        "observatory": observatory,
        "towns": len(towns),
    }


def _pack(tick: int, winner: str, kind: str, reason: str) -> Dict[str, Any]:
    return {
        "type": "outcome",
        "tick": tick,
        "winner": winner,
        "kind": kind,
        "reason": reason,
    }


def detect_early(
    tick: int,
    sides: Dict[str, Dict[str, Any]],
    founded: Set[str],
) -> Optional[Dict[str, Any]]:
    present = [f for f in sides if f in founded]
    if len(present) >= 2:
        alive = [f for f in present if int(sides[f].get("pop") or 0) > 0]
        if not alive:
            return _pack(tick, "draw", "domination", "The tribes fell.")
        if len(alive) == 1:
            f = alive[0]
            return _pack(tick, f, "domination", DOMINATION_REASON.get(f, "The last other people are gone."))

    sci = []
    for f, s in sides.items():
        if bool(s.get("observatory")) and int(s.get("discoveries") or 0) >= SCIENCE_DISCOVERIES:
            sci.append((f, int(s.get("discoveries") or 0)))
    if not sci:
        return None
    best = max(d for _, d in sci)
    top = [f for f, d in sci if d == best]
    if len(top) == 1:
        f = top[0]
        return _pack(tick, f, "science", SCIENCE_REASON.get(f, "They finished the science path first."))
    return _pack(tick, "draw", "science", "Several finished the science path together.")


def detect_survival(
    tick: int,
    sides: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    ranked = sorted(
        sides.items(),
        key=lambda kv: (
            int(kv[1].get("era") or 2),
            int(kv[1].get("pop") or 0),
            int(kv[1].get("discoveries") or 0),
        ),
        reverse=True,
    )
    if not ranked:
        return _pack(tick, "draw", "survival", "The clock ran out. Empty land.")
    best_f, best = ranked[0]
    if len(ranked) >= 2:
        _, nxt = ranked[1]
        if (
            int(best.get("era") or 2) == int(nxt.get("era") or 2)
            and int(best.get("pop") or 0) == int(nxt.get("pop") or 0)
        ):
            return _pack(tick, "draw", "survival", "The clock ran out. Even on people.")
    if int(best.get("era") or 2) >= 4:
        return _pack(tick, best_f, "survival", "The clock ran out. A city, and more people.")
    return _pack(tick, best_f, "survival", "The clock ran out. They outgrew the others.")

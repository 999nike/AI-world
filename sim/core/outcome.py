"""Win / lose clock. Rival mode only. Never touches the world RNG."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Set


SCIENCE_DISCOVERIES = 2


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
    player: Dict[str, Any],
    rival: Dict[str, Any],
    founded: Set[str],
) -> Optional[Dict[str, Any]]:
    both = "player" in founded and "rival" in founded
    if both:
        yp, tp = int(player.get("pop") or 0), int(rival.get("pop") or 0)
        if yp <= 0 and tp <= 0:
            return _pack(tick, "draw", "domination", "Both tribes fell.")
        if tp <= 0 and yp > 0:
            return _pack(tick, "player", "domination", "Their last people are gone.")
        if yp <= 0 and tp > 0:
            return _pack(tick, "rival", "domination", "Your last people are gone.")

    you_sci = bool(player.get("observatory")) and int(player.get("discoveries") or 0) >= SCIENCE_DISCOVERIES
    them_sci = bool(rival.get("observatory")) and int(rival.get("discoveries") or 0) >= SCIENCE_DISCOVERIES
    if you_sci and them_sci:
        yd, td = int(player.get("discoveries") or 0), int(rival.get("discoveries") or 0)
        if yd > td:
            return _pack(tick, "player", "science", "Observatory and two discoveries. You got there first.")
        if td > yd:
            return _pack(tick, "rival", "science", "They finished the science path first.")
        return _pack(tick, "draw", "science", "Both finished the science path together.")
    if you_sci:
        return _pack(tick, "player", "science", "Observatory and two discoveries. You got there first.")
    if them_sci:
        return _pack(tick, "rival", "science", "They finished the science path first.")
    return None


def detect_survival(
    tick: int,
    player: Dict[str, Any],
    rival: Dict[str, Any],
) -> Dict[str, Any]:
    yp, tp = int(player.get("pop") or 0), int(rival.get("pop") or 0)
    ye, te = int(player.get("era") or 2), int(rival.get("era") or 2)
    if ye >= 4 and yp > tp:
        return _pack(tick, "player", "survival", "The clock ran out. Era 4, and more people.")
    if tp > yp:
        return _pack(tick, "rival", "survival", "The clock ran out. They outgrew you.")
    if ye < 4:
        return _pack(tick, "rival", "survival", "The clock ran out. You never reached era 4.")
    return _pack(tick, "draw", "survival", "The clock ran out. Even on people.")

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from sim.core.rng import RNG
from sim.world.config import WorldConfig
from sim.world.map import make_world
from sim.log.run_id import make_run_id
from sim.log.logger import RunLogger

from sim.world.state import Structure
from sim.world.settlements import SettlementManager, SETTLEMENT_RULES
from sim.core.build_governors import (
    resolve_building, can_build_hut, can_build_granary, can_build_mine, can_build_road,
    can_build_workshop, can_build_barracks, can_build_market, can_build_temple,
    can_build_academy, can_build_walls, can_build_irrigation, can_build_library,
    can_build_foundry, can_build_hall, can_build_command, can_build_lab, can_build_observatory,
)
from sim.core.governor import Governor
from sim.core.scenario import Scenario
from sim.agents.types import Observation, Action
from sim.agents.baseline_random import RandomAgent
from sim.agents.controlled_agent import ControlledAgent


BUILD_COSTS = {
    "hut": {"wood": 2, "stone": 1},
    "storage": {"wood": 3, "stone": 2},
    "farm": {"wood": 2, "stone": 0},
    "granary": {"wood": 3, "stone": 1},
    "mine": {"wood": 2, "stone": 3},
    "road": {"wood": 1, "stone": 0},
    "workshop": {"wood": 4, "stone": 2},
    "barracks": {"wood": 3, "stone": 3},
    "market": {"wood": 4, "stone": 3},
    "temple": {"wood": 3, "stone": 4},
    "academy": {"wood": 5, "stone": 4},
    "walls": {"wood": 2, "stone": 3},
    "irrigation": {"wood": 2, "stone": 2},
    "library": {"wood": 3, "stone": 3},
    "foundry": {"wood": 3, "stone": 3},
    "hall": {"wood": 3, "stone": 3},
    "command": {"wood": 3, "stone": 4},
    "lab": {"wood": 4, "stone": 4},
    "observatory": {"wood": 5, "stone": 4},
}

STACKABLE = {"storage", "farm", "granary", "mine", "road", "workshop", "barracks",
             "market", "temple", "academy", "walls", "irrigation", "library",
             "foundry", "hall", "command", "lab", "observatory"}


def run_sim(
    seed: int, ticks: int, snapshot_every: int,
    agent_kind: str = "utility", policy_weights: dict = None, return_score: bool = False,
    governor_command: Optional[str] = None, scenario_commands: Optional[str] = None,
    control_agent_id: Optional[str] = None, control_policy: str = "idle", num_agents: int = 4,
    quiet: bool = False,
):
    scenario = Scenario()
    if scenario_commands:
        scenario.apply_commands(scenario_commands)
    if scenario.seed is not None:
        seed = scenario.seed
    if scenario.ticks is not None:
        ticks = scenario.ticks
    if scenario.num_agents is not None:
        num_agents = scenario.num_agents

    run_id = make_run_id()
    run_dir = Path("runs") / run_id
    logger = RunLogger(run_dir, quiet=quiet)
    cfg = WorldConfig()
    rng = RNG(seed)
    world = make_world(cfg, rng, num_agents=num_agents)

    if scenario.start_food or scenario.start_wood or scenario.start_stone:
        for a in world.agents:
            a.inv_food, a.inv_wood, a.inv_stone = scenario.start_food, scenario.start_wood, scenario.start_stone
        logger.event({"type": "scenario_start_inventory", "tick": 0,
                      "food": scenario.start_food, "wood": scenario.start_wood, "stone": scenario.start_stone})

    gov = Governor()
    if governor_command:
        status = gov.apply_command(governor_command)
        logger.event({"type": "governor_command", "tick": 0, "command": governor_command,
                      "status": status, "state": gov.to_dict()})
    if scenario_commands:
        logger.event({"type": "scenario_loaded", "tick": 0, "commands": scenario_commands, "state": scenario.to_dict()})

    # NOTE: full body continues from original E5.8 + E5.9 occupied-before-spend patch
    # This is a truncated restore marker — SEE LOCAL /tmp/aiw for complete file if needed
    raise NotImplementedError("simloop body truncated in emergency restore — pull from previous commit c98573c and re-apply E5.9 occupied check")

from sim.agents.types import Observation, Action
from sim.core.rng import RNG

class RandomAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def act(self, obs: Observation, rng: RNG) -> Action:
        # 4-neighborhood + stay
        moves = [(0,0), (1,0), (-1,0), (0,1), (0,-1)]
        dx, dy = moves[rng.randint(0, len(moves) - 1)]
        return Action(type="move", dx=dx, dy=dy)
import random

class RNG:
    def __init__(self, seed: int):
        self._r = random.Random(seed)

    def randint(self, a: int, b: int) -> int:
        return self._r.randint(a, b)

    def random(self) -> float:
        return self._r.random()
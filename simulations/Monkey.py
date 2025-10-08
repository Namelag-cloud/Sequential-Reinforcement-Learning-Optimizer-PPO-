import random
from simulations.enemy import Enemy

class Monke(Enemy):
    def __init__(self, hp_range=(1_000_000, 3_200_000)):
        # Call parent init with both the range and an initial random max_hp
        super().__init__(
            48.84,
            80,
            max_hp=random.randint(*hp_range),
            hp_range=hp_range
        )

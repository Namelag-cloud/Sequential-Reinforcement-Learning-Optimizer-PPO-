import random 

class Enemy:
    def __init__(self, defense_mod, resistance_mod, max_hp=500000, hp_range=None):
        self.defense_mod = defense_mod
        self.resistance_mod = resistance_mod
        self.hp_range = hp_range
        self.max_hp = max_hp
        self.current_hp = max_hp

    def reset(self):
        if self.hp_range:
            self.max_hp = random.randint(*self.hp_range)
        self.current_hp = self.max_hp

    def take_damage(self, amount):
        """Apply damage and reduce current HP."""
        # Reduce the current HP by the amount of damage taken
        self.current_hp = max(0, self.current_hp - amount)

    def is_dead(self):
        """Check if the enemy is defeated."""
        # Return True if the current HP is less than or equal to 0
        return self.current_hp <= 0

    def get_hp_percent(self):
        """Return current HP as a fraction between 0 and 1."""
        # Return the current HP as a fraction of the maximum HP
        return self.current_hp / self.max_hp

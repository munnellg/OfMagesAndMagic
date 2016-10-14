import random

class Mage:
    def __init__(self):
        self.name  = "Mary"
        self.health = 50
        self.attack = 0
        self.defense = 50
        self.speed = 0
        self.element = "Thunder"

        self.max_hp = self.health
        self.spells = [
            "Jolt",
        ]

    def make_move(self, allies, enemies):
        return ("Jolt", enemies)

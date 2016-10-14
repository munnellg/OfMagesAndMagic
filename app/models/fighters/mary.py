import random

class Fighter:
    def __init__(self):
        self.name  = "Mary"
        self.max_hp = 50
        self.hp = self.max_hp
        self.attack = 0
        self.defense = 50
        self.speed = 0
        self.element = "Thunder"

        self.moves = [
            "Jolt",
        ]

    def make_move(self, allies, enemies):
        return ("Jolt", enemies)


fighter = Fighter()

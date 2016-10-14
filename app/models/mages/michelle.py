class Mage:
    def __init__(self):
        self.name  = "Michelle"
        self.health = 50
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.element = "Ice"

        self.max_hp = self.health
        self.spells = [
            "Glacier"
        ]

    def make_move(self, allies, enemies):
        return ("Glacier", enemies)

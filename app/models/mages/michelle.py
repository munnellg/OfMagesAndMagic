class Mage:
    def __init__(self):
        self.name  = "Michelle"
        self.health = 60
        self.attack = 10
        self.defense = 20
        self.speed = 10
        self.element = "Water"

        self.max_hp = self.health
        self.spells = [
            "Healing Wave", "Water Jet"
        ]

        self.move_count = 0

    def make_move(self, allies, enemies):
        return ("Water Jet", enemies)

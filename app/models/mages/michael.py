class Mage:
    def __init__(self):
        self.name  = "Michael"
        self.health = 50
        self.attack = 20
        self.defense = 10
        self.speed = 20
        self.element = "Water"
        self.last_move = ""

        self.max_hp = self.health
        self.spells = [
            "Water Jet"
        ]

    def make_move(self, allies, enemies):
        return ("Water Jet", enemies)

class Mage:
    def __init__(self):
        self.name  = "John"
        self.health = 50
        self.attack = 10
        self.defense = 10
        self.speed = 30

        self.element = "Fire"

        self.max_hp = self.health
        self.spells = [
            "Lava Storm",
            "Solar Blaze",
            "Unmake",
            "Kinetic Blast"
        ]

        self.turn = 0

    def make_move(self, allies, enemies):
        self.turn = self.turn + 1

        if self.turn <= 2:
            return ("Solar Blaze", self)
        elif self.turn <= 4:
            return ("Unmake", enemies)
        else:
            return ("Kinetic Blast", enemies)

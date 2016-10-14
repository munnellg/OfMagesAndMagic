class Mage:
    def __init__(self):
        self.name  = "John"
        self.health = 50
        self.attack = 30
        self.defense = 10
        self.speed = 10
        self.element = "Fire"

        self.max_hp = self.health
        self.spells = [
            "Fireball"
        ]

    def make_move(self, allies, enemies):
        return ("Fireball", enemies)

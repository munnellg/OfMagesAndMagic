class Fighter:
    def __init__(self):
        self.name  = "John"
        self.max_hp = 50
        self.hp = self.max_hp
        self.attack = 30
        self.defense = 10
        self.speed = 10
        self.element = "Fire"

        self.moves = [
            "Fireball"
        ]

    def make_move(self, allies, enemies):
        return ("Fireball", enemies)

fighter = Fighter()

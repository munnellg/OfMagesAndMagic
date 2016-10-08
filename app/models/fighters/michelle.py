class Fighter:
    def __init__(self):
        self.name  = "Michelle"
        self.max_hp = 50
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.element = "Ice"

        self.hp = self.max_hp
        self.moves = [
            "Glacier"
        ]

    def make_move(self, allies, enemies):
        return ("Glacier", enemies)

fighter = Fighter()

class Fighter:
    def __init__(self):
        self.name  = "Michael"
        self.max_hp = 50
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.element = "Water"
        self.last_move = ""

        self.moves = [
            "Water Jet"
        ]

    def make_move(self, allies, enemies):
        return ("Water Jet", enemies)

fighter = Fighter()

class Fighter:
    def __init__(self):
        self.name  = "Jill"
        self.max_hp = 50
        self.hp = self.max_hp

        self.attack = 0
        self.defense = 40
        self.speed = 10
        self.element = "Dark"

        self.cur_move = 0

        self.moves = [
            "Sludge Puddle",
            "Disorienting Mist",
            "Withering Glance",
            "Fractured Armour"
        ]

    def make_move(self, allies, enemies):
        self.cur_move += 1
        self.cur_move %= len(self.moves)
        return (self.moves[self.cur_move], enemies)

fighter = Fighter()

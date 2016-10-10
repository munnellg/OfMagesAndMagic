class Fighter:
    def __init__(self):
        self.name  = "James"
        self.max_hp = 60        
        self.attack = 14
        self.defense = 13
        self.speed = 13
        self.element = "Ice"

        self.hp = self.max_hp
        self.moves = [
            "Kinetic Blast",
            "Ice Breaker",
        ]

    def find_target(self, enemies):
        i = 0

        while enemies[i].hp == 0 and i<len(enemies)-1:
            i += 1

        return enemies[i]

    def make_move(self, allies, enemies):
        target = self.find_target(enemies)

        if target.element != "Fire":
            return("Ice Breaker", target)
        else:
            return("Kinetic Blast", target)

fighter = Fighter()

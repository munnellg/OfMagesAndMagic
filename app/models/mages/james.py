class Mage:
    def __init__(self):
        self.name  = "James"
        self.health = 60
        self.attack = 14
        self.defense = 13
        self.speed = 13
        self.element = "Ice"

        self.max_hp = self.health
        self.spells = [
            "Kinetic Blast",
            "Ice Breaker",
        ]

    def find_target(self, enemies):
        i = 0

        while enemies[i].health == 0 and i<len(enemies)-1:
            i += 1

        return enemies[i]

    def make_move(self, allies, enemies):
        target = self.find_target(enemies)

        if target.element != "Fire":
            return("Ice Breaker", target)
        else:
            return("Kinetic Blast", target)

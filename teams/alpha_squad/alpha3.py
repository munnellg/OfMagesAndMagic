class Mage:
    def __init__(self):
        self.name = "Alpha 3"

        self.health  = 50
        self.attack  = 20
        self.defense = 10
        self.speed   = 20

        self.element = "Ice"
        self.spells = [ "Ice Breaker" ]

    def make_move(self, allies, enemies):
        return ("Ice Breaker", enemies)

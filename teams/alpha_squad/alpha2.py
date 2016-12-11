class Mage:
    def __init__(self):
        self.name  = "Alpha 2"

        self.health  = 50
        self.attack  = 20
        self.defense = 10
        self.speed   = 20

        self.element = "Earth"

        self.spells = [ "Rock Smash" ]

    def make_move(self, allies, enemies):
        return("Rock Smash", enemies)

class Mage:
    def __init__(self):

        self.name = "Alpha 4"

        self.health  = 50
        self.attack  = 20
        self.defense = 10
        self.speed   = 20

        self.element = "Fire"

        self.spells = [ "Fireball" ]

    def make_move(self, allies, enemies):
        return("Fireball",enemies)
    

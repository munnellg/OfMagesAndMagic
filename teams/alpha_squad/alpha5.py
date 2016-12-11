class Mage:
    def __init__(self):

        self.name = "Alpha 5"

        self.health  = 50
        self.attack  = 20
        self.defense = 10
        self.speed   = 20

        self.element = "Thunder"
        self.spells = ["Jolt"]


    def make_move(self, allies, enemies):
        return ("Jolt", enemies)

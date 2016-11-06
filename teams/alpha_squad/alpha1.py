class Mage:
    def __init__(self):
        self.name = "Adzy Cage"
        self.element = "Water"
        
        self.health = 30
        self.attack = 30
        self.defense = 20
        self.speed = 20

        self.spells = ["Water Jet", "Tidal Wave"]
        
        return

    def make_move(self, allies, enemies):        
        return ("Water Jet", enemies)

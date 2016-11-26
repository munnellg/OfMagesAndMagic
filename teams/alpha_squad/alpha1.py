class Mage:
    def __init__(self):
        self.name = "Adzy Cage"
        self.element = "Water"

        self.health = 50
        self.attack = 20
        self.defense = 10
        self.speed = 20

        self.spells = ["Monsoon", "Absorb", "Water Jet", "Tidal Wave"]

        return

    def make_move(self, allies, enemies):
        for enemy in enemies:
            if enemy.element in ["Earth", "Fire"] and enemy.health > 0:
                return ("Absorb", enemy)
        return ("Absorb", enemies)

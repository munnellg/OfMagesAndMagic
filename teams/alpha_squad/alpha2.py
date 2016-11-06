class Mage:
    def __init__(self):
        self.name  = "Dan"
        self.health = 60
        self.attack = 10
        self.defense = 20
        self.speed = 10
        self.element = "Earth"

        self.max_hp = self.health
        self.spells = [
            "Rock Smash",
            "Granite Armour",
            "Landslide",
            "Bassault"
        ]

    def make_move(self, allies, enemies):
        if enemies[0].element == "Fire" and enemies[0].health >0:
            return("Bassault", enemies[0])
        elif enemies[1].element == "Fire" and enemies[1].health >0:
            return("Bassault", enemies[1])
        else:
            return ("Landslide", enemies)

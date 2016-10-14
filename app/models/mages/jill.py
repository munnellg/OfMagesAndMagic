class Mage:
    def __init__(self):
        self.name  = "Jill"
        self.health = 50
        self.attack = 0
        self.defense = 40
        self.speed = 10
        self.element = "Earth"

        self.cur_spell = 0

        self.max_hp = self.health
        self.spells = [
            "Rock Smash",
            "Landslide"
        ]

    def make_move(self, allies, enemies):
        self.cur_spell += 1
        self.cur_spell %= len(self.spells)
        return (self.spells[self.cur_spell], enemies)

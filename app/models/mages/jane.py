class Mage:
    def __init__(self):
        self.name  = "Jane"
        self.health = 45
        self.attack = 25
        self.defense = 25
        self.speed = 5
        self.element = "Water"

        self.max_hp = self.health
        self.spells = [
            "Tidal Wave",
            "Water Jet",
            "Kinetic Blast"
        ]

    def count_weak_enemies(self, enemies):
        count = 0
        for enemy in enemies:
            if enemy.element == "Fire" and enemy.health > 0:
                count += 1
        return count

    def find_live_target(self, enemies):
        for enemy in enemies:
            if enemy.health != 0:
                return enemy
        return enemies[0]

    def find_weak_target(self, enemies):
        for enemy in enemies:
            if enemy.element == "Fire" and enemy.health != 0:
                return enemy
        return enemies[0]

    def make_move(self, allies, enemies):
        weak = self.count_weak_enemies(enemies)

        if weak > 1:
            return ("Tidal Wave", enemies)
        elif weak == 1:
            return ("Water Jet", self.find_weak_target(enemies))
        else:
            return ("Kinetic Blast", self.find_live_target(enemies))

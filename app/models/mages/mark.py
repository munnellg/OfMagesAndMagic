class Mage:
    def __init__(self):
        self.name  = "Mark"
        self.health = 50
        self.attack = 40
        self.defense = 5
        self.speed = 5
        self.element = "Fire"

        self.spells = [
            "Fireball",
            "Kinetic Blast"
        ]

        self.order = ""

    def find_target(self, enemies):
        target = enemies[0]
        for enemy in enemies[1:]:
            if enemy.element == "Ice":
                target = enemy
            elif enemy.element not in ["Water", "Fire"] and target.element != "Ice":
                target = enemy
        return target

    def make_move(self, allies, enemies):
        if self.health <= 20:
            self.order = "Heal Me"

        target = self.find_target(enemies)

        if target.element not in ["Water", "Fire"]:
            return ("Fireball", target)
        else:
            return ("Kinetic Blast", target)

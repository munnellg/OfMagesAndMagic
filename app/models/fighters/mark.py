class Fighter:
    def __init__(self):
        self.name  = "Mark"
        self.max_hp = 50
        self.hp = self.max_hp
        self.attack = 40
        self.defense = 5
        self.speed = 5
        self.element = "Fire"

        self.moves = [
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
        if self.hp <= 20:
            self.order = "Heal Me"

        target = self.find_target(enemies)

        if target.element not in ["Water", "Fire"]:
            return ("Fireball", target)
        else:
            return ("Kinetic Blast", target)

fighter = Fighter()

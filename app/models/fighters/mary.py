import random

class Fighter:
    def __init__(self):
        self.name  = "Mary"
        self.max_hp = 50
        self.hp = self.max_hp
        self.attack = 0
        self.defense = 50
        self.speed = 0
        self.element = "Light"

        self.moves = [
            "Healing Light",
            "Healing Wave",
            "Fleet Feet",
            "Eagle Eyes"
        ]

    def find_mark(self, allies):
        for ally in allies:
            if ally.name == "Mark":
                return ally

    def find_most_damaged_ally(self, allies):
        md = allies[0]
        max_damage = md.max_hp - md.hp

        for ally in allies[1:]:
            if ally.max_hp - ally.hp > max_damage:
                md = ally
                max_damage = ally.max_hp - ally.hp

        return md

    def compute_average_damage(self, allies):
        total = 0
        for ally in allies:
            if ally.hp > 0:
                total += ally.max_hp - ally.hp
        return total // len(allies)
    def make_move(self, allies, enemies):
        mark = self.find_mark(allies)
        highest_damage = self.find_most_damaged_ally(allies)

        if mark.order == "Heal Me" and mark.hp > 0:
            mark.order = ""
            return ("Healing Light", mark)
        elif self.compute_average_damage(allies) > 20:
            return ("Healing Wave", allies)
        elif highest_damage.max_hp - highest_damage.hp > 30:
            return ("Healing Light", highest_damage)
        else:
            return (self.moves[random.randint(2,3)], allies)


fighter = Fighter()

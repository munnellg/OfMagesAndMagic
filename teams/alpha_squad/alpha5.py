class Mage:
    def __init__(self):
        # We'll enter our bot's stats here
        # health, attack, defense, speed
        # element
        # spells
        # name
        self.name = "Harambe" 
        self.health = 19
        self.attack = 40
        self.defense = 1
        self.speed = 40
        self.element = "Thunder"
        self.spells = ["Storm", "Jolt"]
        return

    def make_move(self, allies, enemies):
        # Tell our bot to do something!
        # This is where the smart part of your AI will go
        return ("Jolt", enemies)

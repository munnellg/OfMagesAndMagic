class Mage:
    def __init__(self):
        # We'll enter our bot's stats here
        # health, attack, defense, speed
        # element
        # spells
        # name
        self.attack  = 40
        self.speed   = 30
        self.defense = 15
        self.health  = 15

        self.element = "Water"

        self.spells = ["Power Swirl"]

        self.name = "Test 1"
        return

    def make_move(self, allies, enemies):
        # Tell our bot to do something!
        # This is where the smart part of your AI will go
        return ("Power Swirl", enemies)

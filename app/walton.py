import time
from app.models.magic import SpellBook
from app.models.league import build_league
from app.models.battle import Battle

class Walton:
    def __init__(self):
        SpellBook.load_spell_book('data/magic/magic.xml')
        # exit()
        self.league = build_league()
        self.battle = Battle(self.league[0], self.league[1])

    def run(self):
        print("Starting Battle!")
        print(self.battle)

        while self.battle.is_in_battle():
            self.battle.update()
            print(self.battle)
            
        print("Team {} won".format(self.battle.get_winner() + 1))
        print(self.battle)

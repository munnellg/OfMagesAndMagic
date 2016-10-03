from random import shuffle
from app.models.league import build_league
from app.models.battle import Battle

class Walton:
    def __init__(self):
        self.league = build_league()
        self.battle = Battle(self.league[0], self.league[1])

    def run(self):

        while self.battle.is_in_battle():
            self.battle.update()

        print("Team {} won".format(self.battle.get_winner() + 1))
        for i in range(len(self.league[0])):
            print(self.league[0][i].name, self.league[0][i].hp, "|", self.league[1][i].name, self.league[1][i].hp)

import random
from app.models.team import Team

class Move:
    def __init__(self, fighter, ally_team, enemy_team):
        self.fighter = fighter
        self.ally_team = ally_team
        self.enemy_team = enemy_team
        self.rank = self.fighter.get_stat('speed')

    def execute(self):
        self.fighter.make_move(self.ally_team, self.enemy_team)

class BattleRound:
    def __init__(self, team1, team2):
        self.move_order = [Move(fighter, team1, team2) for fighter in team1]
        self.move_order += [Move(fighter, team2, team1) for fighter in team2]
        self.move_order.sort(key=lambda move: -move.rank)

        self.cur_move = 0

    def next_move(self):
        self.move_order[self.cur_move].execute()
        self.cur_move += 1
        return self.cur_move >= len(self.move_order)

class Battle:
    class __BattleInBattle:
        def __init__(self, battle):
            self.battle = battle

        def update(self):
            self.battle.play_next_move()
            if self.battle.is_battle_over():
                self.battle.set_state('battle_over')

    class __BattleOver:
        def __init__(self, battle):
            self.battle = battle

        def update(self):
            return

    def __init__(self, team1, team2):
        self.team1 = Team(team1)
        self.team2 = Team(team2)
        self.cur_round = None
        self.round_counter = 0

        self.cur_state = 'in_battle'
        self.states = {
            'in_battle'   : Battle.__BattleInBattle,
            'battle_over' : Battle.__BattleOver
        }
        self.state = self.states[self.cur_state](self)

        self.start_new_round()

    def update(self):
        self.state.update()

    def set_state(self, state):
        if state not in self.states:
            return

        self.cur_state = state
        self.state = self.states[self.cur_state](self)

    def play_next_move(self):
        if self.cur_round.next_move():
            self.start_new_round()

    def start_new_round(self):
        self.cur_round = BattleRound(self.team1, self.team2)

    def is_in_battle(self):
        return self.cur_state == 'in_battle'

    def is_battle_over(self):
        return self.get_winner() >= 0

    def get_winner(self):
        if self.team2.is_defeated():
            return 0

        if self.team1.is_defeated():
            return 1
        return -1

    def __str__(self):
        text = "Team 1\n"
        for fighter in self.team1:
            text += str(fighter) + "\n"
        text += "\n"

        text += "Team2\n"
        for fighter in self.team2:
            text += str(fighter) + "\n"        
        return text

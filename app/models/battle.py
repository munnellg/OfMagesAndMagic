import random
from app.models.team import Team

class Move:
    def __init__(self, mage, ally_team, enemy_team):
        self.mage = mage
        self.ally_team = ally_team
        self.enemy_team = enemy_team
        self.rank = self.mage.get_stat('speed')

    def execute(self):
        return self.mage.make_move(self.ally_team, self.enemy_team)
        print("")

class BattleRound:
    def __init__(self, team1, team2):
        self.move_order = [Move(mage, team1, team2) for mage in team1 if mage.is_conscious()]
        self.move_order += [Move(mage, team2, team1) for mage in team2 if mage.is_conscious()]
        random.shuffle(self.move_order)
        self.move_order.sort(key=lambda move: -move.rank)

        self.cur_move = 0

    def next_move(self):
        result = self.move_order[self.cur_move].execute()
        self.cur_move += 1
        while self.cur_move < len(self.move_order) and not self.move_order[self.cur_move].mage.is_conscious():
            self.cur_move += 1
        return result

    def round_over(self):
        return self.cur_move >= len(self.move_order)

class Battle:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

        self.team1.reinitialize()
        self.team2.reinitialize()

        self.cur_round = None
        self.round_counter = 0
        self.max_round = 10

        self.start_new_round()

    def set_state(self, state):
        if state not in self.states:
            return

        self.cur_state = state
        self.state = self.states[self.cur_state](self)

    def play_next_move(self):
        if not self.is_battle_over():
            result = self.cur_round.next_move()
            if self.cur_round.round_over():
                self.start_new_round()
            result["finished"] = False
            return result
        return { "finished" : True }

    def start_new_round(self):
        self.cur_round = BattleRound(self.team1, self.team2)
        self.round_counter += 1

    def get_round_number(self):
        return self.round_counter

    def is_battle_over(self):
        return self.team2.is_defeated() or self.team1.is_defeated() or self.round_counter > self.max_round

    def award_victory(self, team_no):
        if team_no == 2:
            for mage in self.team1:
                mage.cur_hp = 0
        elif team_no == 1:
            for mage in self.team2:
                mage.cur_hp = 0

    def get_winner(self):
        if self.team2.is_defeated():
            return self.team1.get_short_name()

        if self.team1.is_defeated():
            return self.team2.get_short_name()

        if self.round_counter > self.max_round:
            dt1 = [tm.get_remaining_health_percentage() for tm in self.team1]
            dt2 = [tm.get_remaining_health_percentage() for tm in self.team2]
            dt1 = sum(dt1)
            dt2 = sum(dt2)
            
            return self.team1.get_short_name() if dt1 > dt2 else self.team2.get_short_name()

        return None

    def __str__(self):
        text = "Round {}\n".format(self.round_counter) if not self.is_battle_over() else "{} won\n".format(self.get_winner())
        text += str(self.team1)
        text += '\n'
        text += str(self.team2)

        return text

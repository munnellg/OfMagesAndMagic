from app.models.battle import Battle
from collections import defaultdict
class League:
    def __init__(self, teams, n_winners=1):
        self.winners = []
        self.n_winners = min(n_winners, len(teams))
        self.initialize_matches(teams)

    def initialize_matches(self, teams):
        self.teams = teams      # Teams in the league
        self.matches = []       # League match pairings
        self.current_match = 0  # The index of the current match to be played
        self.scores = {}        # Every team's scores in the league

        # Every team battles the team to their right
        for i in range(len(self.teams)-1):
            self.matches.append( (self.teams[i], self.teams[i+1]) )

        if len(self.teams) > 2:
            self.matches.append( (self.teams[-1], self.teams[0]) )

        # Initialize scores for every team
        for team in self.teams:
            self.scores[team.get_short_name()] = 0

    def get_matches_list(self):
        return self.matches

    def get_current_match(self):
        return self.current_match

    def get_scores(self):
        return self.scores

    def record_result(self, battle):
        self.scores[battle.get_winner()] += 1

    def winners_chosen(self):
        ranks = defaultdict(list)
        team_scores = []
        for team in self.teams:
            score = self.scores[team.get_short_name()]
            ranks[score].append(team)
            team_scores.append(score)

        team_scores = sorted(set(team_scores), key=lambda x: -x)
        for score in team_scores:
            if len(self.winners) >= self.n_winners:
                break
            if len(ranks[score]) + len(self.winners) <= self.n_winners:                
                self.winners += ranks[score]
            else:
                self.initialize_matches(ranks[score])
                return False
        return True

    def finished(self):
        return self.current_match >= len(self.matches)

    def get_winners(self):
        return self.winners

    def get_next_battle(self):
        if not self.finished():
            b = Battle( *self.matches[self.current_match] )
            self.current_match += 1
            return b

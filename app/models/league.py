from app.models.battle import Battle

class League:
    def __init__(self, teams):
        self.teams = teams      # Teams in the leage
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
            self.scores[team.get_name()] = 0

    def get_matches_list(self):
        return self.matches

    def get_current_match(self):
        return self.current_match

    def get_scores(self):
        return self.scores

    def record_result(self, battle):
        return

    def league_finished(self):
        return self.current_match == len(self.matches)

    def get_next_battle(self):
        if not self.league_finished():
            b = Battle( *self.matches[self.current_match] )
            self.current_match += 1
            return b

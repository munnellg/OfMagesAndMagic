from app.models.fighter_status import FighterStatus

class Team:
    def __init__(self, team_members):
        self.team_status  = [FighterStatus(fighter) for fighter in team_members]

    def is_defeated(self):
        teamhp = sum(int(fighter.cur_hp) for fighter in self.team_status)
        return teamhp == 0

    def __iter__(self):
        return iter(self.team_status)

    def __getitem__(self, i):
        return self.team_status[i]

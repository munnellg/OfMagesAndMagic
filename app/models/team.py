from app.models.fighter_manager import FighterManager

class Team(list):
    def __init__(self, team_name, team_members):
    	self.team_name = team_name
    	self.constructors = team_members
    	self.initialize_team_members()

    def initialize_team_members(self):
    	for fighter in self.constructors:
    		self.append(FighterManager(fighter()))

    def reinitialize(self):
    	self[:] = []
    	self.initialize_team_members()

    def is_defeated(self):
        teamhp = sum(int(fighter.cur_hp) for fighter in self)
        return teamhp == 0

    def __str__(self):
    	text = self.team_name + "\n"

        for fighter in self:
            text += str(fighter) + "\n"
        text += "\n"
        return text

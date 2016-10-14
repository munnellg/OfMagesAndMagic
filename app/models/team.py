from app.models.mage_manager import MageManager

class Team(list):
    def __init__(self, team_name, team_members):
    	self.team_name = team_name
    	self.constructors = team_members
    	self.initialize_team_members()

    def initialize_team_members(self):
    	for mage in self.constructors:
    		self.append(MageManager(mage()))

    def reinitialize(self):
    	self[:] = []
    	self.initialize_team_members()

    def is_defeated(self):
        teamhp = sum(int(mage.cur_hp) for mage in self)
        return teamhp == 0

    def __str__(self):
    	text = self.team_name + "\n"

        for mage in self:
            text += str(mage) + "\n"        
        return text

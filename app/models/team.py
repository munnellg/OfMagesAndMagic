import json
import importlib
from app.models.mage_manager import MageManager

class Team(list):
    def __init__(self, team_name, team_members):
        self.team_name = team_name
        self.constructors = team_members
        self.initialize_team_members()

    def initialize_team_members(self):
        for mage in self.constructors:
            manager = MageManager(mage())
            self.append(manager)

    def reinitialize(self):
        self[:] = []
        self.initialize_team_members()

    def is_defeated(self):
        teamhp = sum(int(mage.cur_hp) for mage in self)
        return teamhp == 0

    def get_short_name(self):
        if len(self.team_name)> 32:
            return self.team_name[:28] + "..."
        else:
            return self.team_name

    def __str__(self):
        text = self.team_name + "\n"

        for mage in self:
            text += str(mage) + "\n"

        return text

def load_teams(path):
    json_data=open(path).read()
    json_data = json.loads(json_data)

    teams = {}
    for team in json_data:
        teams[team] = []
        for mage in json_data[team]:
            try:
                i = importlib.import_module(mage)
                teams[team].append(i.Mage)
            except Exception,e:
                print(e)

    return [Team(team, teams[team]) for team in teams]

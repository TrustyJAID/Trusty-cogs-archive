from .teams import teams
from .errors import *
from datetime import datetime


class Pickems:
    def __init__(self, message:int, channel:int, game_start:str, home_team:str, away_team:str, votes:list, winner:str=None):
        super().__init__()
        self.message = message
        self.channel = channel
        self.game_start = datetime.strptime(game_start, "%Y-%m-%dT%H:%M:%SZ")
        self.home_team = home_team
        self.away_team = away_team
        self.votes = votes
        self.home_emoji = "{}".format(teams[home_team]["emoji"]) if home_team in teams else "nhl:496510372828807178"
        self.away_emoji = "{}".format(teams[away_team]["emoji"]) if away_team in teams else "nhl:496510372828807178"
        self.winner = winner

    def add_vote(self, user_id, team):
        time_now = datetime.utcnow()
        if time_now > self.game_start:
            raise VotingHasEndedError("The game has already started")
        team_choice = None
        if str(team.id) in self.home_emoji:
            team_choice = self.home_team
        if str(team.id) in self.away_emoji:
            team_choice = self.away_team
        user_voted = False
        for user, choice in self.votes:
            if user_id == user:
                self.votes.remove((user, choice))
                self.votes.append((user_id, team_choice))
                raise UserHasVotedError("{} has already voted, removing prior vote".format(user_id))
        if not user_voted and team_choice is not None:
            self.votes.append((user_id, team_choice))

                

    def to_json(self) -> dict:
        return {
            "message" : self.message,
            "channel" : self.channel,
            "game_start" : self.game_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "home_team" : self.home_team,
            "away_team" : self.away_team,
            "votes" : self.votes,
            "winner" : self.winner
        }

    @classmethod
    def from_json(cls, data: dict):
        return cls(data["message"], data["channel"], data["game_start"],
                   data["home_team"], data["away_team"], data["votes"], data["winner"])
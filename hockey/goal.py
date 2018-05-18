from typing import Tuple
from discord.ext import commands
from .teams import teams

import discord
default_team = {"channel":[], "created_channel":[], "goal_id":{}, "game_state":"Null", "period":0, "game_start":""}
class Goal:
    def __init__(self, event_id:str, team_name:str, scorer_id:int, description:str, period:int, period_ord:str,
                 time:int, home_score:int, away_score:int, strength:str, empty_net:bool=False):
        super().__init__()
        self.event_id = event_id
        self.team_name = team_name
        self.scorer_id = scorer_id
        self.headshot = "https://nhl.bamcontent.com/images/headshots/current/168x168/{}.jpg".format(scorer_id)
        self.description = description
        self.period = period
        self.period_ord = period_ord
        self.time = time
        self.home_score = home_score
        self.away_score = away_score
        self.strength = strength
        self.empty_net = empty_net        

    def to_json(self) -> dict:
        return {
            "event_id" : self.event_id,
            "team_name" : self.team_name,
            "scorer_id" : self.scorer_id,
            "description" : self.description,
            "period" : self.period,
            "period_ord" : self.period_ord,
            "time" : self.time,
            "home_score" : self.home_score,
            "away_score" : self.away_score,
            "strength" : self.strength,
            "empty_net" : self.empty_net
        }


    @classmethod
    async def from_json(cls, data: dict):
        return cls(data["gameData"]["status"]["abstractGameState"],
                   )
from typing import Tuple
from discord.ext import commands
from .teams import teams

import discord
class Standings:
    def __init__(self, name:str, division:str, conference:str, division_rank:int, conference_rank:int,
                 league_rank:int, wins:int, losses:int, ot:int, gp:int, pts:int, streak:int, streak_type:str,
                 goals:int, gaa:int, last_updated:str):
        super().__init__()
        self.name = name
        self.division = division
        self.conference = conference
        self.division_rank = division_rank
        self.conference_rank = conference_rank
        self.league_rank = league_rank
        self.wins = wins
        self.losses = losses
        self.ot = ot
        self.gp = gp
        self.pts = pts
        self.streak = streak
        self.streak_type = streak_type
        self.goals = goals
        self.gaa = gaa
        self.last_updated = last_updated

    def to_json(self) -> dict:
        return {
            "team" : self.team,
            "division": self.division_rank,
            "conference" : self.conference_rank,
            "division_rank" : self.division_rank,
            "conference_rank" : self.conference_rank,
            "league_rank" : self.league_rank,
            "wins" : self.wins,
            "losses" : self.losses,
            "ot" : self.ot,
            "gp" : self.gp,
            "pts" : self.pts,
            "streak" : self.streak,
            "streak_type" : self.streak_type,
            "goals" : self.goals,
            "gaa" : self.gaa,
            "last_updated": self.last_updated

        }


    @classmethod
    async def from_json(cls, data: dict, division:str, conference:str):
        return cls(data["team"]["name"],
                   division,
                   conference,
                   data["divisionRank"],
                   data["conferenceRank"],
                   data["leagueRank"],
                   data["leagueRecord"]["wins"],
                   data["leagueRecord"]["losses"],
                   data["leagueRecord"]["ot"],
                   data["gamesPlayed"],
                   data["points"],
                   data["streak"]["streakNumber"],
                   data["streak"]["streakType"],
                   data["goalsScored"],
                   data["goalsAgainst"],
                   data["lastUpdated"]
                   )
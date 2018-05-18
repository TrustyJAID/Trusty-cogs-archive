from typing import Tuple
from discord.ext import commands
from .teams import teams

import discord
default_team = {"channel":[], "created_channel":[], "goal_id":{}, "game_state":"Null", "period":0, "game_start":""}
class Game:
    def __init__(self, game_state:str, home_team: str, away_team:str, period:int,
                 home_shots:int, away_shots:int, home_score:int, away_score:int, game_start:str, goals:list,
                 home_goals:list, away_goals:list, home_abr:str, away_abr:str, period_ord:str, period_time_left:str, plays:list):
        super().__init__()
        self.game_state = game_state
        self.home_team = home_team
        self.away_team = away_team
        self.home_shots = home_shots
        self.away_shots = away_shots
        self.home_score = home_score
        self.away_score = away_score
        self.goals = goals
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.home_abr = home_abr
        self.away_abr = away_abr
        self.period = period
        self.period_ord = period_ord
        self.period_time_left = period_time_left
        self.plays = plays
        self.game_start = game_start
        self.home_logo = teams[home_team]["logo"]
        self.away_logo = teams[away_team]["logo"]
        self.home_emoji = "<:{}>".format(teams[home_team]["emoji"])
        self.away_emoji = "<:{}>".format(teams[away_team]["emoji"])

    def to_json(self) -> dict:
        return {
            "game_state" : self.game_state,
            "home_team" : self.home_team,
            "away_team" : self.away_team,
            "home_shots" : self.home_shots,
            "away_shots" : self.away_shots,
            "home_score" : self.home_score,
            "away_score" : self.away_score,
            "goals" : self.goals,
            "home_goals" : self.home_goals,
            "away_goals" : self.away_goals,
            "home_abr" : self.home_abr,
            "away_abr" : self.away_abr,
            "period" : self.period,
            "period_ord" : self.period_ord,
            "period_time_left" : self.period_time_left,
            "plays" : self.plays,
            "game_start" : self.game_start,
            "home_logo" : self.home_logo,
            "away_logo" : self.away_logo,
            "home_emoji" : self.home_emoji,
            "away_emoji" : self.away_emoji
        }


    @classmethod
    async def from_json(cls, data: dict):
        event = data["liveData"]["plays"]["allPlays"]
        home_team = data["gameData"]["teams"]["home"]["name"]
        away_team = data["gameData"]["teams"]["away"]["name"]
        
        goals = [goal for goal in event if goal["result"]["eventTypeId"] == "GOAL"\
        or (goal["result"]["eventTypeId"] in ["SHOT", "MISSED_SHOT"] and goal["about"]["ordinalNum"] == "SO")]

        if "currentPeriodOrdinal" in data["liveData"]["linescore"]:
            period_ord = data["liveData"]["linescore"]["currentPeriodOrdinal"]
            period_time_left = data["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            events = data["liveData"]["plays"]["allPlays"]
        else:
            period_ord = "0"
            period_time_left = "0"
            events = ["."]
        return cls(data["gameData"]["status"]["abstractGameState"],
                   data["gameData"]["teams"]["home"]["name"],
                   data["gameData"]["teams"]["away"]["name"],
                   data["liveData"]["linescore"]["currentPeriod"],
                   data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"],
                   data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"],
                   data["liveData"]["linescore"]["teams"]["home"]["goals"],
                   data["liveData"]["linescore"]["teams"]["away"]["goals"],
                   data["gameData"]["datetime"]["dateTime"],
                   goals,
                   [goal for goal in goals if home_team in goal["team"]["name"]],
                   [goal for goal in goals if away_team in goal["team"]["name"]],
                   data["gameData"]["teams"]["away"]["abbreviation"],
                   data["gameData"]["teams"]["home"]["abbreviation"],
                   period_ord,
                   period_time_left,
                   events
                   )
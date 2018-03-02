import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
# from .utils.dataIO import dataIO
from redbot.core import checks
from redbot.core import Config
from PIL import Image
from PIL import ImageColor
import numpy as np
import glob
import json
import numpy as np
from .teams import teams
from .teamentry import TeamEntry
import logging 
from .menu import hockey_menu
from .embeds import *

try:
    from .oilers import Oilers
except ImportError:
    pass

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
logging.basicConfig(level=logging.INFO)
class Hockey:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        default_global = {"teams":[]}
        for team in teams:
            team_entry = TeamEntry("Null", team, 0, [], {}, [], "")
            default_global["teams"].append(team_entry.to_json())
        team_entry = TeamEntry("Null", "all", 0, [], {}, [], "")
        default_global["teams"].append(team_entry.to_json())
        default_guild = {"standings_channel":None, "standings_type":None, "post_standings":False, "standings_msg":None,
                         "create_channels":False, "category":None, "gdc_team":None}

        self.config = Config.get_conf(self, 13457745779)
        self.config.register_global(**default_global, force_registration=True)
        self.url = "https://statsapi.web.nhl.com"
        self.teams = teams
        self.headshots = "https://nhl.bamcontent.com/images/headshots/current/168x168/{}.jpg"
        self.loop = bot.loop.create_task(self.get_team_goals())
        # self.new_loop = None

    def __unload(self):
        self.session.close()
        self.loop.cancel()
        # self.new_loop.cancel()


    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def testgoallights(self, ctx):
        hue = Oilers(self.bot)
        await hue.oilersgoal2()

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def add_team_data(self, ctx):
        team_data = await self.config.teams()
        team_entry = TeamEntry("Null", "all", 0, [], {}, [], "")
        team_data.append(team_entry.to_json())
        await self.config.teams.set(team_data)

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def clear_broken_channels(self, ctx):
        team_list = await self.config.teams()
        for team in team_list:
            remove_list = []
            team_list.remove(team)
            for channel in team["channel"]:
                chn = self.bot.get_channel(id=channel)
                if chn is None:
                    remove_list.append(channel)
            for channel in remove_list:
                print(channel)
                team["channel"].remove(channel)
            team_list.append(team)
        await self.config.teams.set(team_list)
        await ctx.send("done")

    async def get_team_goals(self):
        """Loop to check what teams are playing and see if a goal was scored"""
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Hockey"):
            async with self.session.get(self.url + "/api/v1/schedule") as resp:
                data = await resp.json()

            games = [game["link"] for game in data["dates"][0]["games"] if game["status"]["abstractGameState"] != "Final"]
            posted_standings = True
            while games != []:
                to_remove = []
                posted_standings = False
                for link in games:
                    # print(link)
                    try:
                        async with self.session.get(self.url + link) as resp:
                            data = await resp.json()
                    except Exception as e:
                        print(e)
                        continue
                    # print(data)
                    await self.check_game_state(data)
                    game_state = data["gameData"]["status"]["abstractGameState"]
                    home_team = data["gameData"]["teams"]["home"]["name"]
                    away_team = data["gameData"]["teams"]["away"]["name"]
                    print("{} @ {}".format(away_team, home_team))
                    if game_state == "Preview":
                        continue
                    game_start = data["gameData"]["datetime"]["dateTime"]
                    event = data["liveData"]["plays"]["allPlays"]
                    
                    home_shots = data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
                    home_score = data["liveData"]["linescore"]["teams"]["home"]["goals"]
                    
                    away_shots = data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
                    away_score = data["liveData"]["linescore"]["teams"]["away"]["goals"]
                    goals = [goal for goal in event if goal["result"]["eventTypeId"] == "GOAL" or (goal["result"]["eventTypeId"] == "MISSED_SHOT" and goal["about"]["ordinalNum"] == "SO")]
                    home_goals = [goal for goal in goals if home_team in goal["team"]["name"]]
                    away_goals = [goal for goal in goals if away_team in goal["team"]["name"]]
                    home_msg, away_msg = await self.get_shootout_display(goals, home_team, away_team)
                    score_msg = {"Home":home_team, "Home Score":home_score, "Home Shots":home_shots,
                                 "Away": away_team, "Away Score":away_score, "Away Shots":away_shots,
                                 "shootout":{"home_msg": home_msg, "away_msg":away_msg}}                
                    if len(goals) != 0:
                        await self.check_team_goals(goals, home_team, score_msg, False)
                        await self.check_team_goals(goals, away_team, score_msg, False)
                        await self.check_team_goals(home_goals, home_team, score_msg, True)
                        await self.check_team_goals(away_goals, away_team, score_msg, True)


                    if game_state == "Final":
                        all_teams = await self.config.teams()
                        home = await self.get_team(home_team)
                        away = await self.get_team(away_team)
                        all_teams.remove(home)
                        all_teams.remove(away)
                        home["goal_id"] = {}
                        away["goal_id"] = {}
                        all_teams.append(home)
                        all_teams.append(away)
                        await self.config.teams.set(all_teams)
                        to_remove.append(link)

                for link in to_remove:
                    try:
                        games.remove(link)
                    except:
                        pass
                await asyncio.sleep(120)
            print("is_playing")
            if not posted_standings:
                print("test")
                await self.post_automatic_standings()
            all_teams = await self.config.teams()
            for team in await self.config.teams():
                all_teams.remove(team)
                team["goal_id"] = {}
                team["game_state"] = "Null"
                team["game_start"] = ""
                team["period"] = 0
                all_teams.append(team)

            await self.config.teams.set(all_teams)
            await asyncio.sleep(300)

    async def check_game_state(self, data):
        game_state = data["gameData"]["status"]["abstractGameState"]
        game_start = data["gameData"]["datetime"]["dateTime"]
        home_team = data["gameData"]["teams"]["home"]["name"]
        away_team = data["gameData"]["teams"]["away"]["name"]
        post_state = ["all", home_team, away_team]
        away_abr = data["gameData"]["teams"]["away"]["abbreviation"]
        home_abr = data["gameData"]["teams"]["home"]["abbreviation"]
        home_logo = self.teams[home_team]["logo"]
        away_logo = self.teams[away_team]["logo"]
        team_url = self.teams[home_team]["team_url"]
        timestamp = datetime.strptime(game_start, "%Y-%m-%dT%H:%M:%SZ")
        game_state = data["gameData"]["status"]["abstractGameState"]
        h_emoji = "<:{}>".format(self.teams[home_team]["emoji"])
        a_emoji = "<:{}>".format(self.teams[away_team]["emoji"])
        title = "{away} @ {home} {state}".format(away=away_team, home=home_team, state=game_state)
        colour = int(self.teams[home_team]["home"].replace("#", ""), 16)
        # print("gamecheck")
        home = await self.get_team(home_team)
        away = await self.get_team(away_team)
        team_list = await self.config.teams()
        em = discord.Embed(timestamp=timestamp)       
        

        # Home team checking

        if game_state == "Preview":
            """Checks if the the game state has changes from Final to Preview
               Could be unnecessary since after Game Final it will check for next game
            """
            if home["game_state"] != game_state:
                team_list.remove(home)
                team_list.remove(away)
                home["game_state"] = game_state
                away["game_state"] = game_state
                home["game_start"] = game_start
                away["game_start"] = game_start
                team_list.append(home)
                team_list.append(away)
                print("test")
                await self.config.teams.set(team_list)

                em.add_field(name="Home Team", value="{} {}".format(h_emoji, home_team))
                em.add_field(name="Away Team", value="{} {}".format(a_emoji, away_team))
                for state in post_state:
                    team = state if state != "all" else home_team
                    alt_team = [state for state in post_state if state != "all" and state != team][0]
                    em.colour = int(self.teams[team]["home"].replace("#", ""), 16)
                    logo = self.teams[team]["logo"]
                    alt_logo = self.teams[alt_team]["logo"]
                    em.set_author(name=title, url=team_url, icon_url=logo)
                    em.set_thumbnail(url=logo)
                    em.set_footer(text="Game start ", icon_url=alt_logo)
                    for channels in await self.get_team_channels(state):
                        channel = self.bot.get_channel(id=channels)
                        if channel is None:
                            continue
                        try:
                            await channel.send(embed=em)
                        except Exception as e:
                            print("Problem posting in channel <#{}> : {}".format(channels, e))
                # Create channel and look for game day thread

        if game_state == "Live":
            """Checks what the period is and posts the game is starting in the appropriate channel"""
            home_shots = data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
            home_score = data["liveData"]["linescore"]["teams"]["home"]["goals"]
            away_team = data["liveData"]["linescore"]["teams"]["away"]["team"]["name"]
            away_shots = data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
            away_score = data["liveData"]["linescore"]["teams"]["away"]["goals"]
            home_str = "Goals: **{}** \nShots: **{}**".format(home_score, home_shots)
            away_str = "Goals: **{}** \nShots: **{}**".format(away_score, away_shots)
            period = data["liveData"]["linescore"]["currentPeriod"]
            period_ord = data["liveData"]["linescore"]["currentPeriodOrdinal"]
            em.add_field(name=home_team, value=home_str, inline=True)
            em.add_field(name=away_team, value=away_str, inline=True)

            if home["period"] != period:
                team_list.remove(home)
                team_list.remove(away)
                home["period"] = period
                away["period"] = period
                home["game_state"] = game_state
                away["game_state"] = game_state
                team_list.append(home)
                team_list.append(away)
                await self.config.teams.set(team_list)

                msg = "**{} Period starting {} at {}**"
                print(msg.format(period_ord, away_team, home_team))
                for state in post_state:
                    team = state if state != "all" else home_team
                    alt_team = [state for state in post_state if state != "all" and state != team][0]
                    em.colour = int(self.teams[team]["home"].replace("#", ""), 16)
                    logo = self.teams[team]["logo"]
                    alt_logo = self.teams[alt_team]["logo"]
                    em.set_author(name=title, url=team_url, icon_url=logo)
                    em.set_thumbnail(url=logo)
                    em.set_footer(text="Game start ", icon_url=alt_logo)
                    for channels in await self.get_team_channels(state):
                        channel = self.bot.get_channel(id=channels)
                        if channel is None:
                            continue
                        guild = channel.guild
                        # print(home_role)
                        home_role, away_role = await self.get_team_role(guild, home_team, away_team)
                        try:
                            await channel.send(msg.format(period_ord, away_role, home_role), embed=em)
                        except Exception as e:
                            print("Problem posting in channel <#{}> : {}".format(channels, e))
            # Say game starting in all channels


        if game_state == "Final":
            """Final game state checks"""

            if home["game_state"] != game_state and home["game_state"] != "Null":
                team_list.remove(home)
                team_list.remove(away)
                home["game_state"] = "Null"
                away["game_state"] = "Null"
                home["period"] = 0
                away["period"] = 0
                team_list.append(home)
                team_list.append(away)
                await self.config.teams.set(team_list)

                home_shots = data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
                home_score = data["liveData"]["linescore"]["teams"]["home"]["goals"]
                away_team = data["liveData"]["linescore"]["teams"]["away"]["team"]["name"]
                away_shots = data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
                away_score = data["liveData"]["linescore"]["teams"]["away"]["goals"]
                home_str = "Goals: **{}** \nShots: **{}**".format(home_score, home_shots)
                away_str = "Goals: **{}** \nShots: **{}**".format(away_score, away_shots)
                em.add_field(name=home_team, value=home_str, inline=True)
                em.add_field(name=away_team, value=away_str, inline=True)
                # Post game final data and check for next game
                msg = "Game Final {} @ {}"
                print(msg.format(home_team, away_team))
                # print("Final")
                # Clears the game data from the settings file
                for state in post_state:
                    team = state if state != "all" else home_team
                    alt_team = [state for state in post_state if state != "all" and state != team][0]
                    em.colour = int(self.teams[team]["home"].replace("#", ""), 16)
                    logo = self.teams[team]["logo"]
                    alt_logo = self.teams[alt_team]["logo"]
                    em.set_author(name=title, url=team_url, icon_url=logo)
                    em.set_thumbnail(url=logo)
                    em.set_footer(text="Game start ", icon_url=alt_logo)
                    for channels in await self.get_team_channels(state):
                        channel = self.bot.get_channel(id=channels)
                        if channel is None:
                            continue
                        guild = channel.guild
                        try:
                            await channel.send(embed=em)
                        except Exception as e:
                            print("Problem posting in channel <#{}> : {}".format(channels, e))

        
    async def get_team_channels(self, team):
        for teams in await self.config.teams():
            if teams["team_name"] == team:
                return teams["channel"]
        return []

    async def get_team(self, team):
        for teams in await self.config.teams():
            if teams["team_name"] == team:
                return teams
        return None
        
    async def get_team_role(self, guild, home_team, away_team):
        home_role = None
        away_role = None
        
        for role in guild.roles:
            if "Canadiens" in home_team and "Canadiens" in role.name:
                home_role = role.mention
            elif role.name == home_team:
                home_role = role.mention
            if "Canadiens" in away_team and "Canadiens" in role.name:
                away_role = role.mention
            elif role.name == away_team:
                away_role = role.mention
        if home_role is None:
            home_role = home_team
        if away_role is None:
            away_role = away_team
        return home_role, away_role


    async def get_shootout_display(self, goals, home_team, away_team):
        home_msg = ""
        away_msg = ""
        score = "☑"
        miss = "❌"
        for goal in goals:
            if goal["result"]["eventTypeId"] == "MISSED_SHOT" and goal["about"]["ordinalNum"] == "SO":
                if goal["team"]["name"] == home_team:
                    home_msg += miss
                if goal["team"]["name"] == away_team:
                    away_msg += miss
            if goal["result"]["eventTypeId"] == "GOAL" and goal["about"]["ordinalNum"] == "SO":
                if goal["team"]["name"] == home_team:
                    home_msg += score
                if goal["team"]["name"] == away_team:
                    away_msg += score
        return home_msg, away_msg


    async def check_team_goals(self, goals, team, score_msg, is_all=False):
        team_data = await self.get_team(team)
        all_data = await self.get_team("all")
        team_list = await self.config.teams()
        

        goal_ids = [str(goal_id["result"]["eventCode"]) for goal_id in goals]
        goal_list = list(team_data["goal_id"])
        all_goal_list = list(all_data["goal_id"])
        # print(goals)
        for goal in goals:
            goal_id = str(goal["result"]["eventCode"])
            if not is_all:
                if goal_id not in goal_list:
                    # Posts goal information and saves data for verification later
                    msg_list = await self.post_team_goal(goal, team, score_msg)
                    team_list.remove(team_data)
                    team_data["goal_id"][goal_id] = {"goal":goal,"messages":msg_list}
                    team_list.append(team_data)
                    await self.config.teams.set(team_list)
                    continue
                if goal_id in goal_list:
                    # Checks if the goal data has changed and edits all previous posts with new data
                    old_goal = team_data["goal_id"][goal_id]["goal"]
                    if goal != old_goal:
                        print("attempting to edit")
                        old_msgs = team_data["goal_id"][goal_id]["messages"]
                        team_list.remove(team_data)
                        team_data["goal_id"][goal_id]["goal"] = goal
                        team_list.append(team_data)
                        await self.config.teams.set(team_list)
                        await self.post_team_goal(goal, team, score_msg, old_msgs)
            if is_all:
                # print("all")
                if goal_id not in all_goal_list:
                    msg_list = await self.post_team_goal(goal, "all", score_msg)
                    team_list.remove(all_data)
                    all_data["goal_id"][goal_id] = {"goal":goal, "messages":msg_list}
                    team_list.append(all_data)
                    await self.config.teams.set(team_list)
                    continue
                if goal_id in all_goal_list:
                    old_goal = all_data["goal_id"][goal_id]["goal"]
                    if goal != old_goal:
                        print("attempting to edit")
                        old_msgs = all_data["goal_id"][goal_id]["messages"]
                        team_list.remove(all_data)
                        all_data["goal_id"][goal_id]["goal"] = goal
                        team_list.append(all_data)
                        await self.config.teams.set(team_list)
                        await self.post_team_goal(goal, "all", score_msg, old_msgs)
        if not is_all:
            # to_remove = [goal for goal in goal_list if goal not in goal_ids]
            for old_goal in goal_list:
                # print(old_goal)
                if old_goal not in goal_ids:
                    print(old_goal)
                    try:
                        old_msgs = team_data["goal_id"][old_goal]["messages"].items()
                    except Exception as e:
                        print(e)
                        continue
                    for channel_id, message_id in old_msgs:
                        channel = self.bot.get_channel(id=int(channel_id))
                        try:
                            message = await channel.get_message(message_id)
                            await message.delete()
                            
                        except Exception as e:
                            print("something wrong with {} {}: {}".format(team, old_goal, e))
                            pass
                        try:
                            team_list.remove(team_data)
                            del team_data["goal_id"][old_goal]
                            team_list.append(team_data)
                            await self.config.teams.set(team_list)
                        except Exception as e:
                            print(e)
                            pass
                        print("done")
                    try:
                        all_old_msgs = all_data["goal_id"][old_goal]["messages"].items()
                    except Exception as e:
                        print(e)
                        continue
                    
                    for channel_id, message_id in all_old_msgs:
                        try:
                            channel = self.bot.get_channel(id=int(channel_id))

                            message = await channel.get_message(message_id)
                            await message.delete()
                        except Exception as e:
                            print("something wrong with all {}: {}".format(old_goal, e))
                            pass
                        try:
                            team_list.remove(all_data)
                            del all_data["goal_id"][old_goal]
                            team_list.append(all_data)
                            await self.config.teams.set(team_list)
                        except Exception as e:
                            print(e)
                            pass
                    print("should reach here")

    async def post_team_goal(self, goal, team, score_msg, og_msg=None):
        """Creates embed and sends message if a team has scored a goal"""
        team_data = await self.get_team(team)
        scorer = self.headshots.format(goal["players"][0]["player"]["id"])
        scoring_team = self.teams[goal["team"]["name"]]
        period = goal["about"]["ordinalNum"]
        home = goal["about"]["goals"]["home"]
        away = goal["about"]["goals"]["away"]
        h_emoji = "<:{}>".format(self.teams[score_msg["Home"]]["emoji"])
        a_emoji = "<:{}>".format(self.teams[score_msg["Away"]]["emoji"])
        period_time_left = goal["about"]["periodTimeRemaining"]
        event = goal["result"]["event"]
        shootout = False
        if period == "SO":
            shootout = True
        try:
            strength = goal["result"]["strength"]["name"]
        except KeyError:
            strength = ""
        if strength == "Even":
            strength = "Even Strength"
        try:
            if goal["result"]["emptyNet"]:
                strength = "Empty Net"
        except KeyError:
            pass
        if not shootout:
            em = discord.Embed(description=goal["result"]["description"],
                               colour=int(self.teams[goal["team"]["name"]]["home"].replace("#", ""), 16))
            em.set_author(name="🚨 " + goal["team"]["name"] + " " + strength + " " + event + " 🚨", 
                          url=self.teams[goal["team"]["name"]]["team_url"],
                          icon_url=self.teams[goal["team"]["name"]]["logo"])
            home_str = "Goals: **{}** \nShots: **{}**".format(home, score_msg["Home Shots"])
            away_str = "Goals: **{}** \nShots: **{}**".format(away, score_msg["Away Shots"])
            em.add_field(name="{} {} {}".format(h_emoji, score_msg["Home"], h_emoji), value=home_str, inline=True)
            em.add_field(name="{} {} {}".format(a_emoji, score_msg["Away"], a_emoji), value=away_str, inline=True)
            # em.add_field(name="Shots " + score_msg["Home"], value=score_msg["Home Shots"], inline=True)
            # em.add_field(name="Shots " + score_msg["Away"], value=score_msg["Away Shots"], inline=True)
            if team != "all":
                em.set_thumbnail(url=scorer)
            em.set_footer(text="{} left in the {} period"
                          .format(period_time_left, period), icon_url=self.teams[goal["team"]["name"]]["logo"])
            em.timestamp = datetime.strptime(goal["about"]["dateTime"], "%Y-%m-%dT%H:%M:%SZ")
        else:
            if "missed" in event.lower():
                em = discord.Embed(description=strength + " " + event + " by " + goal["result"]["description"],
                               colour=int(self.teams[goal["team"]["name"]]["home"].replace("#", ""), 16))
                em.set_author(name=goal["team"]["name"] + " " + event, 
                              url=self.teams[goal["team"]["name"]]["team_url"],
                              icon_url=self.teams[goal["team"]["name"]]["logo"])
            else:
                em = discord.Embed(description="Shootout " + event + " by " + goal["result"]["description"],
                               colour=int(self.teams[goal["team"]["name"]]["home"].replace("#", ""), 16))
                em.set_author(name="🚨 " + goal["team"]["name"] + " Shootout " + event + " 🚨", 
                          url=self.teams[goal["team"]["name"]]["team_url"],
                          icon_url=self.teams[goal["team"]["name"]]["logo"])
            home_msg = score_msg["shootout"]["home_msg"]
            away_msg = score_msg["shootout"]["away_msg"]
            em.add_field(name=score_msg["Home"], value=home_msg)
            em.add_field(name=score_msg["Away"], value=away_msg)
            if team != "all":
                em.set_thumbnail(url=scorer)
            em.set_footer(text="{} left in the {} period"
                          .format(period_time_left, period), icon_url=self.teams[goal["team"]["name"]]["logo"])
            em.timestamp = datetime.strptime(goal["about"]["dateTime"], "%Y-%m-%dT%H:%M:%SZ")
        msg_list = {}
        if og_msg is None:
            if "oilers" in goal["team"]["name"].lower() and "missed" not in event.lower() and team != "all":
                try:
                    hue = Oilers(self.bot)
                    await hue.oilersgoal2()
                except:
                    pass
            for channels in team_data["channel"]:
                try:
                    role = None
                    channel = self.bot.get_channel(id=channels)
                    if channel is None:
                        continue
                    guild = channel.guild
                    for roles in guild.roles:
                        if roles.name == goal["team"]["name"] + " GOAL":
                            role = roles
                    if role is None or "missed" in event.lower():
                        msg = await channel.send(embed=em)
                        msg_list[str(channel.id)] = msg.id
                    else:  
                        msg = await channel.send(role.mention, embed=em)
                        msg_list[str(channel.id)] = msg.id
                except:
                    print("Could not post goal in {}".format(channels))
                    pass
            # print(msg_list)
            return msg_list
        else:
            for channel_id, message_id in og_msg.items():
                try:
                    role = None
                    channel = self.bot.get_channel(id=int(channel_id))
                    if channel is None:
                        continue
                    # print("channel {} ID {}".format(channel, message_id))
                    message = await channel.get_message(message_id)
                    # print("I can get the message")
                    guild = message.guild
                    for roles in guild.roles:
                        if roles.name == goal["team"]["name"] + " GOAL":
                            role = roles
                    if role is None or "missed" in event.lower():
                        await message.edit(embed=em)
                    else:  
                        await message.edit(content=role.mention, embed=em)
                except:
                    print("Could not edit goal in {}".format(channel_id))
            return

    @commands.group(pass_context=True, name="hockey", aliases=["nhl"])
    async def hockey_commands(self, ctx):
        """Various Hockey related commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def reset(self, ctx):
        all_teams = await self.config.teams()
        for team in await self.config.teams():
            all_teams.remove(team)
            team["goal_id"] = {}
            team["game_state"] = "Null"
            team["game_start"] = ""
            team["period"] = 0
            all_teams.append(team)

        await self.config.teams.set(all_teams)
        await ctx.send("Done.")

    @hockey_commands.command(name="poststandings", aliases=["poststanding"])
    async def post_standings(self, ctx, standings_type:str, channel:discord.TextChannel=None):
        """Posts automatic standings when all games for the day are done"""
        guild = ctx.message.guild
        if channel is None:
            channel = ctx.message.channel
        standings_list = ["metropolitan", "atlantic", "pacific", "central", "eastern", "western", "all"]
        if standings_type.lower() not in standings_list:
            await ctx.send("You must choose from {}".format(", ".join(s for s in standings_list)))
            return
        await self.config.guild(guild).standings_type.set(standings_type)
        await self.config.guild(guild).standings_channel.set(channel.id)
        await ctx.send("Sending standings to {}".format(channel.mention))

        async with self.session.get("https://statsapi.web.nhl.com/api/v1/standings") as resp:
            data = await resp.json()
        conference = ["eastern", "western"]
        division = ["metropolitan", "atlantic", "pacific", "central"]
        division_data = []
        conference_data = []
        eastern = [team for record in data["records"] for team in record["teamRecords"] if record["conference"]["name"] =="Eastern"]
        western = [team for record in data["records"] for team in record["teamRecords"] if record["conference"]["name"] =="Western"]
        conference_data.append(eastern)
        conference_data.append(western)
        division_data = [record for record in data["records"]]

        if standings_type in division:
            division_search = None
            for record in division_data:
                if standings_type.lower() == record["division"]["name"].lower():
                    division_search = record
            index = division_data.index(division_search)
            em = await self.division_standing_embed(division_data, index)
        elif standings_type.lower() in conference:
            if standings_type.lower() == "eastern":
                em = await self.conference_standing_embed(conference_data, 0)
            else:
                em = await self.conference_standing_embed(conference_data, 1)
        elif standings_type == "all":
            em = await self.all_standing_embed(division_data, 0)
        message = await channel.send(embed=em)
        await self.config.guild(guild).standings_msg.set(message.id)
        await ctx.send("{} standings will now be automatically updated in {}".format(standings_type, channel.mention))
        await self.config.guild(guild).post_standings.set(True)


    @hockey_commands.command()
    async def togglestandings(self, ctx):
        """Toggles the standings on or off."""
        guild = ctx.message.guild
        cur_state = not await self.config.guild(guild).post_standings()
        await self.config.guild(guild).post_standings.set(cur_state)
        await ctx.send("Done.")

    @hockey_commands.command(hidden=True)
    async def enablestandings(self, ctx, guild_id):
        """Toggles the standings on or off."""
        guild = self.bot.get_guild(guild_id)
        cur_state = not await self.config.guild(guild).post_standings()
        await self.config.guild(guild).post_standings.set(cur_state)
        await ctx.send("Done.")


    @hockey_commands.command(pass_context=True, name="add", aliases=["add_goals"])
    @checks.admin_or_permissions(manage_channels=True)
    async def add_goals(self, ctx, team, channel:discord.TextChannel=None):
        """Adds a hockey team goal updates to a channel do 'all' for all teams"""
        all_team_data = await self.config.teams()
        if team.lower() == "all":
            team = "all"
        else:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await self.bot.say("{} is not an available team!".format(team))
                return
        team_data = await self.get_team(team)
        if channel is None:
            channel = ctx.message.channel
        
        if channel.id in team_data["channel"]:
            await ctx.message.channel.send( "I am already posting {} goals in {}!".format(team, channel.mention))
            return
        all_team_data.remove(team_data)
        team_data["channel"].append(channel.id)
        all_team_data.append(team_data)
        await self.config.teams.set(all_team_data)
        await ctx.send("{} goals will be posted in {}".format(team, channel.mention))


    @hockey_commands.command(pass_context=True, name="del", aliases=["remove", "rem"])
    @checks.admin_or_permissions(manage_channels=True)
    async def remove_goals(self, ctx, team, channel:discord.TextChannel=None):
        """Removes a teams goal updates from a channel"""
        all_team_data = [team for team in await self.config.teams()]
        if team.lower() == "all":
            team = "all"
        else:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await self.bot.say("{} is not an available team!".format(team))
                return
        team_data = await self.get_team(team)
        if channel is None:
            channel = ctx.message.channel
    
        if channel.id in team_data["channel"]:
            all_team_data.remove(team_data)
            team_data["channel"].remove(channel.id)
            all_team_data.append(team_data)
            await self.config.teams.set(all_team_data)
            await ctx.send("{} goals will stop being posted in {}".format(team, channel.mention))

    @hockey_commands.command(pass_context=True, name="role")
    async def team_role(self, ctx, *, team):
        """Set your role to a team role"""
        guild = ctx.message.guild
        try:
            role = [role for role in guild.roles if (team.lower() in role.name.lower() and "GOAL" not in role.name)][0]
            await ctx.message.author.add_roles(role)
            await ctx.message.channel.send( "Role applied.")
        except:
            await ctx.message.channel.send( "{} is not an available role!".format(team))

    @hockey_commands.command(pass_context=True, name="goals")
    async def team_goals(self, ctx, *, team=None):
        """Subscribe to goal notifications"""
        guild = ctx.message.guild
        member = ctx.message.author
        if team is None:
            team = [role.name for role in member.roles if role.name in self.teams]
            for t in team:
                roles = [role for role in guild.roles if role.name == t + " GOAL"]
                for role in roles:
                    await ctx.message.author.add_roles(role)
                await ctx.message.channel.send( "Role applied.")
        else:
            try:
                role = [role for role in guild.roles if (team.lower() in role.name.lower() and role.name.endswith("GOAL"))][0]
                await ctx.message.author.add_roles(role)
                await ctx.message.channel.send( "Role applied.")
            except:
                await ctx.message.channel.send("{} is not an available role!".format(team))


    async def post_automatic_standings(self):
        print("Updating Standings.")
        async with self.session.get("https://statsapi.web.nhl.com/api/v1/standings") as resp:
            data = await resp.json()
        conference = ["eastern", "western"]
        division = ["metropolitan", "atlantic", "pacific", "central"]
        division_data = []
        conference_data = []
        eastern = [team for record in data["records"] for team in record["teamRecords"] if record["conference"]["name"] =="Eastern"]
        western = [team for record in data["records"] for team in record["teamRecords"] if record["conference"]["name"] =="Western"]
        conference_data.append(eastern)
        conference_data.append(western)
        division_data = [record for record in data["records"]]
        all_guilds = await self.config.all_guilds()
        print(all_guilds)
        for guilds in all_guilds:
            print(guilds)
            guild = self.bot.get_guild(guilds)
            if await self.config.guild(guild).post_standings():
                print("hi there")
                try:

                    search = await self.config.guild(guild).standings_type()
                    channel = self.bot.get_channel(await self.config.guild(guild).standings_channel())
                    message = await channel.get_message(await self.config.guild(guild).standings_msg())
                    print("{}-{}-{}".format(search, channel.id, message.id))
                except Exception as e:
                    print(e)
                    continue
                if search.lower() in division:
                    division_search = None
                    for record in division_data:
                        if search.lower() == record["division"]["name"].lower():
                            division_search = record
                    index = division_data.index(division_search)
                    em = await division_standing_embed(division_data, index)
                elif search.lower() in conference:
                    if search.lower() == "eastern":
                        em = await conference_standing_embed(conference_data, 0)
                    else:
                        em = await conference_standing_embed(conference_data, 1)
                elif search.lower() == "all":
                    em = await all_standing_embed(division_data)
                if message is not None:
                    await message.edit(embed=em)


    @hockey_commands.command(pass_context=True)
    async def standings(self, ctx, *, search=None):
        """Displays current standings for each division"""
        async with self.session.get("https://statsapi.web.nhl.com/api/v1/standings") as resp:
            data = await resp.json()
        conference = ["eastern", "western", "conference"]
        division = ["metropolitan", "atlantic", "pacific", "central", "division"]
        try:
            team = [team_name for team_name in self.teams if search.lower() in team_name.lower()][0]
        except:
            team = None
        division_data = []
        conference_data = []
        team_data = []
        eastern = [team for record in data["records"] for team in record["teamRecords"] if record["conference"]["name"] =="Eastern"]
        western = [team for record in data["records"] for team in record["teamRecords"] if record["conference"]["name"] =="Western"]
        all_teams = [team for record in data["records"] for team in record["teamRecords"]]
        conference_data.append(eastern)
        conference_data.append(western)
        all_teams = sorted(all_teams, key=lambda k: int(k["leagueRank"]))
        division_data = [record for record in data["records"]]
        if search is None or search.lower() in division:
            if search is not None:
                division_search = None
                for record in division_data:
                    if search.lower() == record["division"]["name"].lower():
                        division_search = record
            if division_search is not None:
                index = division_data.index(division_search)
                await hockey_menu(ctx, "division", division_data, None, index)
            else:
                await hockey_menu(ctx, "division", division_data)
        elif search.lower() in conference:
            if search.lower() == "eastern":
                await hockey_menu(ctx, "conference", conference_data, None, 0)
            else:
                await hockey_menu(ctx, "conference", conference_data, None, 1)
        elif search.lower() == "all":
            await hockey_menu(ctx, "all", division_data)
        elif team is not None or "team" in search.lower():
            if team is None:
                await hockey_menu(ctx, all_teams, "teams")
            else:
                team_data = None
                for teams in all_teams:
                    if teams["team"]["name"] == team:
                        team_data = teams
                index = all_teams.index(team_data)
                await hockey_menu(ctx, "teams", all_teams, None, index)

    @hockey_commands.command(pass_context=True, aliases=["score"])
    async def games(self, ctx, *, team=None):
        """Gets all NHL games this season or selected team"""
        games_list = []
        page_num = 0
        today = datetime.today()
        year = 2017
        year2 = 2018
        url = "{base}/api/v1/schedule?startDate={year}-9-1&endDate={year2}-9-1"\
              .format(base=self.url, year=year, year2=year2)
        
        if team is not None:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await ctx.message.channel.send( "{} Does not appear to be an NHL team!".format(team))
                return
            url += "&teamId={}".format(self.teams[team]["id"])
        async with self.session.get(url) as resp:
            data = await resp.json()
        for dates in data["dates"]:
            games_list += [game for game in dates["games"]]
        for game in games_list:
            game_time = datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ")
            if game_time >= today:
                page_num = games_list.index(game)
                break
        if games_list != []:
            await hockey_menu(ctx, "game", games_list, None, page_num)
        else:
            await ctx.message.channel.send( "{} have no recent or upcoming games!".format(team))

    @hockey_commands.command(pass_context=True)
    async def players(self, ctx, *, search):
        """Gets the current team roster"""
        rosters = {}
        players = []
        teams = [team for team in self.teams if search.lower() in team.lower()]
        if teams != []:
            for team in teams:
                url = "{}/api/v1/teams/{}/roster".format(self.url, self.teams[team]["id"])
                async with self.session.get(url) as resp:
                    data = await resp.json()
                for player in data["roster"]:
                    players.append(player)
        else:
            for team in self.teams:
                url = "{}/api/v1/teams/{}/roster".format(self.url, self.teams[team]["id"])
                async with self.session.get(url) as resp:
                    data = await resp.json()
                # print(data)
                try:
                    rosters[team] = data["roster"]
                except KeyError:
                    pass
            
            for team in rosters:
                # print(team)
                for player in rosters[team]:
                    # print(player["person"])
                    if search.lower() in player["person"]["fullName"].lower():
                        players.append(player)
        
        if players != []:
            await hockey_menu(ctx, "roster", players)
        else:
            await ctx.message.channel.send( "{} is not an NHL team or Player!".format(search))


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
                            await self.bot.delete_message(message)
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
            await self.bot.add_roles(ctx.message.author, role)
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
                role = [role for role in guild.roles if role.name == t + " GOAL"]
                for roles in role:
                    await self.bot.add_roles(ctx.message.author, roles)
                await ctx.message.channel.send( "Role applied.")
        else:
            try:
                role = [role for role in guild.roles if (team.lower() in role.name.lower() and role.name.endswith("GOAL"))][0]
                await self.bot.add_roles(ctx.message.author, role)
                await ctx.message.channel.send( "Role applied.")
            except:
                await ctx.message.channel.send( "{} is not an available role!".format(team))

    async def game_menu(self, ctx, post_list: list,
                         team_set=None,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""

        game = post_list[page]
        print(self.url + game["link"])
        async with self.session.get(self.url + game["link"]) as resp:
            game_data = await resp.json()
        home_team = game_data["liveData"]["linescore"]["teams"]["home"]["team"]["name"]
        home_shots = game_data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
        home_score = game_data["liveData"]["linescore"]["teams"]["home"]["goals"]
        away_team = game_data["liveData"]["linescore"]["teams"]["away"]["team"]["name"]
        away_shots = game_data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
        away_score = game_data["liveData"]["linescore"]["teams"]["away"]["goals"]
        home_logo = self.teams[home_team]["logo"] if team_set is None else self.teams[team_set]["logo"]
        away_logo = self.teams[away_team]["logo"] if team_set is None else self.teams[team_set]["logo"]
        team_url = self.teams[home_team]["team_url"] if team_set is None else self.teams[team_set]["team_url"]
        game_time = game["gameDate"]
        timestamp = datetime.strptime(game_time, "%Y-%m-%dT%H:%M:%SZ")
        game_state = game_data["gameData"]["status"]["abstractGameState"]
        h_emoji = "<:{}>".format(self.teams[home_team]["emoji"])
        a_emoji = "<:{}>".format(self.teams[away_team]["emoji"])
        title = "{away} @ {home} {state}".format(away=away_team, home=home_team, state=game_state)
        if team_set is None:
            colour = int(self.teams[home_team]["home"].replace("#", ""), 16)
        else:
            colour = int(self.teams[team_set]["home"].replace("#", ""), 16)
        em = discord.Embed(timestamp=timestamp, colour=colour)
        em.set_author(name=title, url=team_url, icon_url=home_logo)
        em.set_thumbnail(url=home_logo)
        em.set_footer(text="Game start ", icon_url=away_logo)
        if game_state == "Preview":
            em.add_field(name="Home Team", value="{} {}".format(h_emoji, home_team))
            em.add_field(name="Away Team", value="{} {}".format(a_emoji, away_team))
        if game_state != "Preview":
            event = game_data["liveData"]["plays"]["allPlays"]
            goals = [goal for goal in event if goal["result"]["eventTypeId"] == "GOAL"]
            home_msg = "Goals: **{}** \nShots: **{}**".format(home_score, home_shots)
            away_msg = "Goals: **{}** \nShots: **{}**".format(away_score, away_shots)
            em.add_field(name="{} {} {}".format(h_emoji, home_team, h_emoji), value=home_msg)
            em.add_field(name="{} {} {}".format(a_emoji, away_team, a_emoji), value=away_msg)
            if goals != []:
                goal_msg = ""
                first_goals = [goal for goal in goals if goal["about"]["ordinalNum"] == "1st"]
                second_goals = [goal for goal in goals if goal["about"]["ordinalNum"] == "2nd"]
                third_goals = [goal for goal in goals if goal["about"]["ordinalNum"] == "3rd"]
                ot_goals = [goal for goal in goals if goal["about"]["ordinalNum"] == "OT"]
                so_goals = [goal for goal in goals if goal["about"]["ordinalNum"] == "SO"]
                list_goals = {"1st":first_goals, "2nd":second_goals, "3rd":third_goals, "OT":ot_goals, "SO":so_goals}
                for goals in list_goals:
                    ordinal = goals
                    goal_msg = ""
                    for goal in list_goals[ordinal]:
                        goal_msg += "{} Goal By {}\n\n".format(goal["team"]["name"], goal["result"]["description"])
                    if goal_msg != "":
                        em.add_field(name="{} Period Goals".format(ordinal), value=goal_msg)
            if game_state == "Live":
                period_time_left = game_data["liveData"]["linescore"]["currentPeriodTimeRemaining"]
                em.description = event[-1]["result"]["description"]
                period = game_data["liveData"]["linescore"]["currentPeriodOrdinal"]
                if period_time_left[0].isdigit():
                    msg = "{} Left in the {} period".format(period_time_left, period)
                else:
                    msg = "{} of the {} period".format(period_time_left, period)
                em.add_field(name="Period", value=msg)
                
        
        if not message:
            message = await ctx.send(embed=em)
            await message.add_reaction("⬅")
            await message.add_reaction("❌")
            await message.add_reaction("➡")
        else:
            # message edits don't return the message object anymore lol
            await message.edit(embed=em)
        check = lambda react, user:user == ctx.message.author and react.emoji in ["➡", "⬅", "❌"] and react.message.id == message.id
        try:
            react, user = await self.bot.wait_for("reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await message.remove_reaction("⬅", self.bot.user)
            await message.remove_reaction("❌", self.bot.user)
            await message.remove_reaction("➡", self.bot.user)
            return None
        else:
            reacts = {v: k for k, v in numbs.items()}
            react = reacts[react.emoji]
            if react == "next":
                next_page = 0
                if page == len(post_list) - 1:
                    next_page = 0  # Loop around to the first item
                else:
                    next_page = page + 1
                try:
                    await message.remove_reaction("➡", ctx.message.author)
                except:
                    pass
                return await self.game_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            elif react == "back":
                next_page = 0
                if page == 0:
                    next_page = len(post_list) - 1  # Loop around to the last item
                else:
                    next_page = page - 1
                try:
                    await message.remove_reaction("⬅", ctx.message.author)
                except:
                    pass
                return await self.game_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            else:
                return await message.delete()

    async def roster_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        player_list = post_list[page]
        async with self.session.get(self.url + player_list["person"]["link"] + "?expand=person.stats&stats=yearByYear") as resp:
            player_data = await resp.json()
        player = player_data["people"][0]
        year_stats = [league for league in player["stats"][0]["splits"] if league["league"]["name"] == "National Hockey League"][-1]
        name = player["fullName"]
        number = player["primaryNumber"]
        position = player["primaryPosition"]["name"]
        headshot = self.headshots.format(player["id"])
        team = player["currentTeam"]["name"]
        em = discord.Embed(colour=int(self.teams[team]["home"].replace("#", ""), 16))
        em.set_author(name="{} #{}".format(name, number), url=self.teams[team]["team_url"], icon_url=self.teams[team]["logo"])
        em.add_field(name="Position", value=position)
        em.set_thumbnail(url=headshot)
        if position != "Goalie":
            post_data = {"Shots" : year_stats["stat"]["shots"],
                        "Goals" : year_stats["stat"]["goals"],
                        "Assists" : year_stats["stat"]["assists"],
                        "Hits" : year_stats["stat"]["hits"],
                        "Face Off Percent" : year_stats["stat"]["faceOffPct"],
                        "+/-" : year_stats["stat"]["plusMinus"],
                        "Blocked Shots" : year_stats["stat"]["blocked"],
                        "PIM" : year_stats["stat"]["pim"]}
            for key, value in post_data.items():
                if value != 0.0:
                    em.add_field(name=key, value=value)
        else:
            saves = year_stats["stat"]["saves"]
            save_percentage = year_stats["stat"]["savePercentage"]
            goals_against_average = year_stats["stat"]["goalAgainstAverage"]
            em.add_field(name="Saves", value=saves)
            em.add_field(name="Save Percentage", value=save_percentage)
            em.add_field(name="Goals Against Average", value=goals_against_average)
        
        if not message:
            message = await ctx.send(embed=em)
            await message.add_reaction("⬅")
            await message.add_reaction("❌")
            await message.add_reaction("➡")
        else:
            # message edits don't return the message object anymore lol
            await message.edit(embed=em)
        check = lambda react, user:user == ctx.message.author and react.emoji in ["➡", "⬅", "❌"] and react.message.id == message.id
        try:
            react, user = await self.bot.wait_for("reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await message.remove_reaction("⬅", self.bot.user)
            await message.remove_reaction("❌", self.bot.user)
            await message.remove_reaction("➡", self.bot.user)
            return None
        else:
            reacts = {v: k for k, v in numbs.items()}
            react = reacts[react.emoji]
            if react == "next":
                next_page = 0
                if page == len(post_list) - 1:
                    next_page = 0  # Loop around to the first item
                else:
                    next_page = page + 1
                try:
                    await message.remove_reaction("➡", ctx.message.author)
                except:
                    pass
                return await self.roster_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            elif react == "back":
                next_page = 0
                if page == 0:
                    next_page = len(post_list) - 1  # Loop around to the last item
                else:
                    next_page = page - 1
                try:
                    await message.remove_reaction("⬅", ctx.message.author)
                except:
                    pass
                return await self.roster_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            else:
                return await message.delete()

    async def post_automatic_standings(self):
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
        all_teams = sorted(all_teams, key=lambda k: int(k["leagueRank"]))
        division_data = [record for record in data["records"]]

        for guilds in self.config.get_guilds():
            guild = self.bot.get_guild(guild)
            if await self.config.guild(guild).post_standings():
            
                search = await self.config.guild(guild).standings_type()
                channel = self.bot.get_channel(id=await self.config.guild(guild).standings_channel())
                message = await channel.get_message(id=await self.config.guild(guild).standings_msg())

                if search in division:
                    division_search = None
                    for record in division_data:
                        if search.lower() == record["division"]["name"].lower():
                            division_search = record
                    index = division_data.index(division_search)
                    em = await self.division_standing_embed(division_data, index)
                elif search.lower() in conference:
                    if search.lower() == "eastern":
                        em = await self.conference_standing_embed(conference_data, 0)
                    else:
                        em = await self.conference_standing_embed(conference_data, 1)
                elif search.lower() == "all":
                    await self.standings_menu(ctx, division_data, "all")
                if message is not None:
                    await message.edit(embed=em)

    async def division_standing_embed(self, post_list, page=0):
        em = discord.Embed()
        standing_list = post_list[page]
        conference = standing_list["conference"]["name"]
        division = standing_list["division"]["name"]
        for team in standing_list["teamRecords"]:
            team_name = team["team"]["name"]
            emoji = "<:" + self.teams[team_name]["emoji"] + ">"
            wins = team["leagueRecord"]["wins"]
            losses = team["leagueRecord"]["losses"]
            ot = team["leagueRecord"]["ot"]
            gp = team["gamesPlayed"]
            pts = team["points"]
            pl = team["divisionRank"]
            division_logo = self.teams["Team {}".format(division)]["logo"]
            msg = "GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**".format(pl=pl,emoji=emoji, wins=wins, losses=losses, ot=ot, pts=pts, gp=gp)
            timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
            em.add_field(name=pl + ". " + emoji + " " + team_name, value=msg, inline=False)
            em.timestamp = timestamp
            em.set_footer(text="Stats last Updated", icon_url=division_logo)
            em.set_thumbnail(url=division_logo)
            em.colour = int(self.teams["Team {}".format(division)]["home"].replace("#", ""), 16)
            em.set_author(name=division + " Division", url="https://www.nhl.com/standings", icon_url=division_logo)
        return em

    async def conference_standing_embed(self, post_list, page=0):
        em = discord.Embed()
        standing_list = post_list[page]
        conference = "Eastern" if page == 0 else "Western"
        new_list = sorted(standing_list, key=lambda k: int(k["conferenceRank"]))
        for team in new_list:
            team_name = team["team"]["name"]
            emoji = "<:" + self.teams[team_name]["emoji"] + ">"
            wins = team["leagueRecord"]["wins"]
            losses = team["leagueRecord"]["losses"]
            ot = team["leagueRecord"]["ot"]
            gp = team["gamesPlayed"]
            pts = team["points"]
            pl = team["conferenceRank"]
            msg = "GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**".format(pl=pl,emoji=emoji, wins=wins, losses=losses, ot=ot, pts=pts, gp=gp)
            timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
            em.add_field(name=pl + ". " + emoji + " " + team_name, value=msg, inline=True)
            em.timestamp = timestamp
            em.set_footer(text="Stats last Updated")
        if conference == "Eastern":
            em.colour = int("c41230", 16)
            em.set_author(name=conference + " Conference", url="https://www.nhl.com/standings", icon_url="https://upload.wikimedia.org/wikipedia/en/thumb/1/16/NHL_Eastern_Conference.svg/1280px-NHL_Eastern_Conference.svg.png")
        if conference == "Western":
            em.colour = int("003e7e", 16)
            em.set_author(name=conference + " Conference", url="https://www.nhl.com/standings", icon_url="https://upload.wikimedia.org/wikipedia/en/thumb/6/65/NHL_Western_Conference.svg/1280px-NHL_Western_Conference.svg.png")
        return em

    async def team_standing_embed(self, post_list, page=0):
        em = discord.Embed()
        standing_list = post_list[page]
        team = standing_list
        team_name = team["team"]["name"]
        league_rank = team["leagueRank"]
        division_rank = team["divisionRank"]
        conference_rank = team["conferenceRank"]
        emoji = "<:" + self.teams[team_name]["emoji"] + ">"
        wins = team["leagueRecord"]["wins"]
        losses = team["leagueRecord"]["losses"]
        ot = team["leagueRecord"]["ot"]
        gp = team["gamesPlayed"]
        pts = team["points"]
        streak = "{} {}".format(team["streak"]["streakNumber"], team["streak"]["streakType"])
        goals = team["goalsScored"]
        goals_against = team["goalsAgainst"]
        timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
        em.set_author(name="# {} {}".format(league_rank, team_name), url="https://www.nhl.com/standings", icon_url=self.teams[team_name]["logo"])
        em.colour = int(self.teams[team_name]["home"].replace("#", ""), 16)
        em.set_thumbnail(url=self.teams[team_name]["logo"])
        em.add_field(name="Division", value="# " + division_rank)
        em.add_field(name="Conference", value="# " + conference_rank)
        em.add_field(name="Wins", value=wins)
        em.add_field(name="Losses", value=losses)
        em.add_field(name="OT", value=ot)
        em.add_field(name="Points", value=pts)
        em.add_field(name="Games Played", value=gp)
        em.add_field(name="Goals Scored", value=goals)
        em.add_field(name="Goals Against", value=goals_against)
        em.add_field(name="Current Streak", value=streak)
        em.timestamp = timestamp
        em.set_footer(text="Stats last Updated", icon_url=self.teams[team_name]["logo"])
        return em

    async def all_standing_embed(self, post_standings, page=0):
        em = discord.Embed()
        em.set_author(name="NHL Standings", url="https://www.nhl.com/standings/2017/wildcard", icon_url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
        em.set_thumbnail(url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
        # standing_list = post_list[page]
        for division in post_standings:
            msg = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"  
            division_name = division["division"]["name"]
            for team in division["teamRecords"]:
                team_name = team["team"]["name"]
                emoji = "<:" + self.teams[team_name]["emoji"] + ">"
                wins = team["leagueRecord"]["wins"]
                losses = team["leagueRecord"]["losses"]
                ot = team["leagueRecord"]["ot"]
                gp = team["gamesPlayed"]
                pts = team["points"]
                pl = team["divisionRank"]
                # division_logo = self.teams["Team {}".format(division)]["logo"]
                msg += "{rank}. <:{team}> GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**\n".format(pl=pl,emoji=emoji, wins=wins, losses=losses, ot=ot, pts=pts, gp=gp, rank=pl, team=self.teams[team_name]["emoji"])
                timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
            msg += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
            em.add_field(name=division_name, value=msg, inline=True)
            # em.add_field(name="▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
        em.timestamp = timestamp
        em.set_footer(text="Stats Last Updated", icon_url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
        return em


    async def standings_menu(self, ctx, post_list: list,
                         display_type,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        # Change between standing pages
        #This part builds the embed depending on display_type argument    
        if display_type == "division":
            em = await self.division_standing_embed(post_list, page)
        if display_type == "conference":
            em = await self.conference_standing_embed(post_list, page)
        if display_type == "teams":
            em = await self.team_standing_embed(post_list, page)
        if display_type == "all":
            em = await self.all_standing_embed(post_list, page)

        # This part controls the logic for changing pages
        if not message:
            message = await ctx.send(embed=em)
            await message.add_reaction("⬅")
            await message.add_reaction("❌")
            await message.add_reaction("➡")
        else:
            # message edits don't return the message object anymore lol
            await message.edit(embed=em)
        check = lambda react, user:user == ctx.message.author and react.emoji in ["➡", "⬅", "❌"] and react.message.id == message.id
        try:
            react, user = await self.bot.wait_for("reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await message.remove_reaction("⬅", self.bot.user)
            await message.remove_reaction("❌", self.bot.user)
            await message.remove_reaction("➡", self.bot.user)
            return None
        else:
            reacts = {v: k for k, v in numbs.items()}
            react = reacts[react.emoji]
            if react == "next":
                next_page = 0
                if page == len(post_list) - 1:
                    next_page = 0  # Loop around to the first item
                else:
                    next_page = page + 1
                try:
                    await message.remove_reaction("➡", ctx.message.author)
                except:
                    pass
                return await self.standings_menu(ctx, post_list, display_type, message=message,
                                             page=next_page, timeout=timeout)
            elif react == "back":
                next_page = 0
                if page == 0:
                    next_page = len(post_list) - 1  # Loop around to the last item
                else:
                    next_page = page - 1
                try:
                    await message.remove_reaction("⬅", ctx.message.author)
                except:
                    pass
                return await self.standings_menu(ctx, post_list, display_type, message=message,
                                             page=next_page, timeout=timeout)
            else:
                return await message.delete()


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
                index = division_data.index(division_search)
                await self.standings_menu(ctx, division_data, "division", None, index)
            else:
                await self.standings_menu(ctx, division_data, "division")
        elif search.lower() in conference:
            if search.lower() == "eastern":
                await self.standings_menu(ctx, conference_data, "conference", None, 0)
            else:
                await self.standings_menu(ctx, conference_data, "conference", None, 1)
        elif search.lower() == "all":
            await self.standings_menu(ctx, division_data, "all")
        elif team is not None or "team" in search.lower():
            if team is None:
                await self.standings_menu(ctx, all_teams, "teams")
            else:
                team_data = None
                for teams in all_teams:
                    if teams["team"]["name"] == team:
                        team_data = teams
                index = all_teams.index(team_data)
                await self.standings_menu(ctx, all_teams, "teams", None, index)

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
            await self.game_menu(ctx, games_list, team, None, page_num)
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
            await self.roster_menu(ctx, players)
        else:
            await ctx.message.channel.send( "{} is not an NHL team or Player!".format(search))


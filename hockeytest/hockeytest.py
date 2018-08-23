import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
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
from .game import Game

try:
    from .oilers import Oilers
except ImportError:
    pass


logging.basicConfig(level=logging.INFO)
class Hockeytest:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        default_global = {"teams":[], "created_gdc":False}
        for team in teams:
            team_entry = TeamEntry("Null", team, 0, [], {}, [], "")
            default_global["teams"].append(team_entry.to_json())
        team_entry = TeamEntry("Null", "all", 0, [], {}, [], "")
        default_global["teams"].append(team_entry.to_json())
        default_guild = {"standings_channel":None, "standings_type":None, "post_standings":False, "standings_msg":None,
                         "create_channels":False, "category":None, "gdc_team":None, "gdc":[], "delete_gdc":True}
        default_channel = {"team":None, "to_delete":False}

        self.config = Config.get_conf(self, 13457745779)
        self.config.register_global(**default_global, force_registration=True)
        self.url = "https://statsapi.web.nhl.com"
        self.teams = teams
        self.headshots = "https://nhl.bamcontent.com/images/headshots/current/168x168/{}.jpg"
        # self.loop = bot.loop.create_task(self.get_team_goals())

    def __unload(self):
        self.session.close()
        # self.loop.cancel()
        # self.new_loop.cancel()


    @commands.command(hidden=True)
    @checks.is_owner()
    async def makeobj(self, ctx):
        """Test stuff"""
        async with self.session.get("https://statsapi.web.nhl.com/api/v1/game/2017021007/feed/live") as resp:
            data = await resp.json()
        game = await Game.from_json(data)
        print(game.to_json())

    @commands.command()
    async def getgoals(self, ctx):
        """Loop to check what teams are playing and see if a goal was scored"""
        to_remove = []
        games_playing = True
        # print(link)
        with open(str(cog_data_path(self)) + "/testgame.json", "r") as infile:
            data = json.loads(infile.read())
        # print(data)
        game_data = await Game.from_json(data)
        await self.check_game_state(game_data)              
        if (game_data.home_score + game_data.away_score) != 0:
            await self.check_team_goals(game_data)

    async def save_game_state(self, data, is_final=False):
        home = await self.get_team(data.home_team)
        away = await self.get_team(data.away_team)
        team_list = await self.config.teams()
        team_list.remove(home)
        team_list.remove(away)
        if not is_final:
            home["game_state"] = data.game_state
            away["game_state"] = data.game_state
            home["period"] = data.period
            away["period"] = data.period
        else:
            home["game_state"] = "Null"
            away["game_state"] = "Null"
            home["period"] = 0
            away["period"] = 0
        home["game_start"] = data.game_start
        away["game_start"] = data.game_start
        team_list.append(home)
        team_list.append(away)
        print("test")
        await self.config.teams.set(team_list)

    async def check_game_state(self, data):
        post_state = ["all", data.home_team, data.away_team]
        # print("gamecheck")
        home = await self.get_team(data.home_team)
        away = await self.get_team(data.away_team)
        team_list = await self.config.teams()
        # Home team checking
        # print(data.game_state)
        if data.game_state == "Preview":
            """Checks if the the game state has changes from Final to Preview
               Could be unnecessary since after Game Final it will check for next game
            """
            if home["game_state"] != data.game_state:
                
                if not await self.config.created_gdc():
                    await self.post_automatic_standings()
                    await self.check_new_gdc()
                    await self.config.created_gdc.set(True)
                await self.post_game_state(data)
                await self.save_game_state(data)
                # Create channel and look for game day thread

        if data.game_state == "Live":
            """Checks what the period is and posts the game is starting in the appropriate channel"""
            if home["period"] != data.period:
                msg = "**{} Period starting {} at {}**"
                print(msg.format(data.period_ord, data.away_team, data.home_team))
                await self.post_game_state(data)
                await self.save_game_state(data)

            if (data.home_score + data.away_score) != 0:
                # Check if there's goals only if there are goals
                await self.check_team_goals(data)

        if data.game_state == "Final":
            """Final game state checks"""
            if (data.home_score + data.away_score) != 0:
                """ Check for goal before posting game final, happens with OT games"""
                await self.check_team_goals(data)
            if home["game_state"] != data.game_state and home["game_state"] != "Null":
                # Post game final data and check for next game
                msg = "Game Final {} @ {}"
                print(msg.format(data.home_team, data.away_team))
                await self.post_game_state(data)
                await self.save_game_state(data)


        
    async def get_team_channels(self, team):
        for teams in await self.config.teams():
            if teams["team_name"] == team:
                return teams["channel"]
        return []

    async def get_team(self, team):
        for teams in await self.config.teams():
            # print(team)
            if team == teams["team_name"]:
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

    async def get_next_game(self, team):
        """Gets all NHL games this season or selected team"""
        games_list = []
        page_num = 0
        today = datetime.now()
        url = "{base}/api/v1/schedule?startDate={year}-9-1&endDate={year2}-9-1"\
              .format(base=self.url, year=YEAR_START, year2=YEAR_FINISH)
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
            game = games_list[page_num]
            async with self.session.get("https://statsapi.web.nhl.com" + game["link"]) as resp:
                game_data = await resp.json()
            game_data = await Game.from_json(game_data)
            return game_data
        else:
            return None

    async def check_gdc(self, guild, data):
        for channel in guild.channels:
            if data.home_abr.lower() in channel.name and data.away_abr.lower() in channel.name:
                return channel
        return None


    async def check_team_goals(self, data):
        home_team_data = await self.get_team(data.home_team)
        away_team_data = await self.get_team(data.away_team)
        all_data = await self.get_team("all")
        team_list = await self.config.teams()
        post_state = ["all", data.home_team, data.away_team]
        
        home_goal_ids = [str(goal_id["result"]["eventCode"]) for goal_id in data.home_goals]
        away_goal_ids = [str(goal_id["result"]["eventCode"]) for goal_id in data.away_goals]

        home_goal_list = list(home_team_data["goal_id"])
        away_goal_list = list(away_team_data["goal_id"])
        # all_goal_list = list(all_data["goal_id"])

        for goal in data.goals:
            goal_id = str(goal["result"]["eventCode"])
            team = goal["team"]["name"]
            team_data = await self.get_team(team)
            # print(team_data)
            if goal_id not in team_data["goal_id"]:
                # attempts to post the goal if there is a new goal
                msg_list = await self.post_team_goal(goal, data)
                team_list.remove(team_data)
                team_data["goal_id"][goal_id] = {"goal":goal,"messages":msg_list}
                team_list.append(team_data)
                await self.config.teams.set(team_list)
                continue
            if goal_id in team_data["goal_id"]:
                # attempts to edit the goal if the scorers have changed
                old_goal = team_data["goal_id"][goal_id]["goal"]
                if goal["result"]["description"] != old_goal["result"]["description"]:
                    old_msgs = team_data["goal_id"][goal_id]["messages"]
                    team_list.remove(team_data)
                    team_data["goal_id"][goal_id]["goal"] = goal
                    team_list.append(team_data)
                    await self.config.teams.set(team_list)
                    await self.edit_team_goal(goal, data, old_msgs)
        for goal in list(home_team_data["goal_id"]):
            # attempts to delete the goal if it was called back
            await self.remove_goal_post(goal, data.home_team, data)
        for goal in list(away_team_data["goal_id"]):
            await self.remove_goal_post(goal, data.away_team, data)
    
    async def remove_goal_post(self, goal, team, data):
        # print(goal)
        # goal_id = str(goal["result"]["eventCode"])
        team_list = await self.config.teams()
        team_data = await self.get_team(team)
        if goal not in [goal["result"]["eventCode"] for goal in data.goals]:
            try:
                old_msgs = team_data["goal_id"][goal]["messages"].items()
            except Exception as e:
                print(e)
                return
            for channel_id, message_id in old_msgs:
                channel = self.bot.get_channel(id=int(channel_id))
                try:
                    message = await channel.get_message(message_id)
                    if message is not None:
                        await message.delete()
                    
                except Exception as e:
                    print("something wrong with {} {}: {}".format(team, goal, e))
                    pass
            try:
                team_list.remove(team_data)
                del team_data["goal_id"][goal]
                team_list.append(team_data)
                await self.config.teams.set(team_list)
            except Exception as e:
                print(e)
                return
        return
                    

    async def post_team_goal(self, goal, game_data):
        """Creates embed and sends message if a team has scored a goal"""
        scorer = self.headshots.format(goal["players"][0]["player"]["id"])
        post_state = ["all", game_data.home_team, game_data.away_team]
        event = goal["result"]["event"]
        em = await goal_post_embed(goal, game_data)
        msg_list = {}
        if "oilers" in goal["team"]["name"].lower() and "missed" not in event.lower():
            try:
                hue = Oilers(self.bot)
                await hue.oilersgoal2()
            except:
                pass
            # for channels in team_data["channel"]:
        for channels in await self.config.all_channels():
            role = None
            channel = self.bot.get_channel(id=channels)
            if channel is None:
                continue
            if await self.config.channel(channel).team() in post_state:
                try:
                    guild = channel.guild
                    game_day_channels = await self.config.guild(guild).gdc()
                    # Don't want to ping people in the game day channels
                    if not channel.permissions_for(guild.me).embed_links:
                        continue
                    for roles in guild.roles:
                        if roles.name == goal["team"]["name"] + " GOAL":
                            role = roles
                    if game_day_channels is not None:
                        # We don't want to ping people in the game day channels twice
                        if channel.id in game_day_channels:
                            role = None
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

    async def post_game_state(self, data):
        post_state = ["all", data.home_team, data.away_team]
        # print("test")
            
        for channels in await self.config.all_channels():
            channel = self.bot.get_channel(id=channels)
            if channel is None:
                continue

            state = await self.config.channel(channel).team()
            if state in post_state:
                em = await game_state_embed(data, state)
                guild = channel.guild
                game_day_channels = await self.config.guild(guild).gdc()
                # print(game_day_channels)
                if data.game_state == "Live":
                    msg = "**{} Period starting {} at {}**"
                    home_role, away_role = await self.get_team_role(guild, data.home_team, data.away_team)
                    if game_day_channels is not None:
                        # We don't want to ping people in the game day channels twice
                        if channel.id in game_day_channels:
                            home_role, away_role = data.home_team, data.away_team                        
                    try:
                        await channel.send(msg.format(data.period_ord, away_role, home_role), embed=em)
                    except Exception as e:
                        print("Problem posting in channel <#{}> : {}".format(channels, e))
                
                else:
                    if data.game_state == "Preview":
                        if game_day_channels is not None:
                            # Don't post the preview message twice in the channel
                            if channel.id in game_day_channels:
                                continue
                    try:
                        await channel.send(embed=em)
                    except Exception as e:
                        print("Problem posting in channel <#{}> : {}".format(channels, e))


    async def edit_team_goal(self, goal, game_data, og_msg):
        scorer = self.headshots.format(goal["players"][0]["player"]["id"])
        post_state = ["all", game_data.home_team, game_data.away_team]
        event = goal["result"]["event"]
        em = await goal_post_embed(goal, game_data)
        for channel_id, message_id in og_msg.items():
            try:
                role = None
                channel = self.bot.get_channel(id=int(channel_id))
                if channel is None:
                    continue
                message = await channel.get_message(message_id)
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

    @commands.group()
    async def hockeytest(self, ctx):
        """Various Hockey related commands"""
        pass

    @hockeytest.command(hidden=True)
    @checks.is_owner()
    async def reset(self, ctx):
        all_teams = await self.config.teams()
        for team in all_teams:
            all_teams.remove(team)
            team["goal_id"] = {}
            team["game_state"] = "Null"
            team["game_start"] = ""
            team["period"] = 0
            all_teams.append(team)

        await self.config.teams.set(all_teams)
        await ctx.send("Done.")

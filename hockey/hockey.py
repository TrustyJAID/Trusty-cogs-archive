import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
try:
    from .oilers import Oilers
except ImportError:
    pass

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
class Hockey:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.settings = dataIO.load_json("data/hockey/settings.json")
        self.url = "https://statsapi.web.nhl.com"
        self.teams = dataIO.load_json("data/hockey/teams.json")
        self.headshots = "https://nhl.bamcontent.com/images/headshots/current/168x168/{}.jpg"
        self.loop = bot.loop.create_task(self.get_team_goals())

    def __unload(self):
        self.session.close()
        self.loop.cancel()

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def testgoallights(self, ctx):
        hue = Oilers(self.bot)
        await hue.oilersgoal2()

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def add_team_data(self, ctx):
        for team in self.settings:
            self.settings[team]["game_state"] = "Null"
            self.settings[team]["game_start"] = "2018-01-21T23:00:00Z"
            self.settings[team]["period"] = 1
        dataIO.save_json("data/hockey/settings.json", self.settings)

    async def team_playing(self, games):
        """Check if team is playing and returns game link and team name"""
        is_playing = False
        # links = {}
        links = []
        for game in games:
            if game["teams"]["away"]["team"]["name"] in self.settings and game["status"]["abstractGameState"] != "Final":
                is_playing = True
                if game["link"] not in links:
                    links.append(game["link"])
                # links[game["teams"]["away"]["team"]["name"]] = game["link"]
            if game["teams"]["home"]["team"]["name"] in self.settings and game["status"]["abstractGameState"] != "Final":
                is_playing =True
                if game["link"] not in links:
                    links.append(game["link"])
                # links[game["teams"]["home"]["team"]["name"]] = game["link"]
        return is_playing, links

    async def get_team_goals(self):
        """Loop to check what teams are playing and see if a goal was scored"""
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Hockey"):
            async with self.session.get(self.url + "/api/v1/schedule") as resp:
                data = await resp.json()
            is_playing, games = await self.team_playing(data["dates"][0]["games"])
            num_goals = 0
            # print(games)
            to_remove = []
            while is_playing and games != []:
                for link in games:
                    # print(link)
                    async with self.session.get(self.url + link) as resp:
                        data = await resp.json()
                    # print(data)
                    await self.check_game_state(data)
                    game_state = data["gameData"]["status"]["abstractGameState"]
                    game_start = data["gameData"]["datetime"]["dateTime"]
                    event = data["liveData"]["plays"]["allPlays"]
                    home_team = data["gameData"]["teams"]["home"]["name"]
                    home_shots = data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
                    home_score = data["liveData"]["linescore"]["teams"]["home"]["goals"]
                    away_team = data["gameData"]["teams"]["away"]["name"]
                    away_shots = data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
                    away_score = data["liveData"]["linescore"]["teams"]["away"]["goals"]
                    goals = [goal for goal in event if goal["result"]["eventTypeId"] == "GOAL" or (goal["result"]["eventTypeId"] == "MISSED_SHOT" and goal["about"]["ordinalNum"] == "SO")]
                    home_goals = [goal for goal in goals if home_team in goal["team"]["name"]]
                    away_goals = [goal for goal in goals if away_team in goal["team"]["name"]]
                    home_msg, away_msg = await self.get_shootout_display(goals, home_team, away_team)
                    score_msg = {"Home":home_team, "Home Score":home_score, "Home Shots":home_shots,
                                 "Away": away_team, "Away Score":away_score, "Away Shots":away_shots,
                                 "shootout":{"home_msg": home_msg, "away_msg":away_msg}}
                    print("{} @ {}".format(home_team, away_team))
                    
                    if len(goals) != 0:
                        await self.check_team_goals(goals, home_team, score_msg, False)
                        await self.check_team_goals(goals, away_team, score_msg, False)
                        await self.check_team_goals(home_goals, home_team, score_msg, True)
                        await self.check_team_goals(away_goals, away_team, score_msg, True)


                    if game_state == "Final":
                        self.settings[home_team]["goal_id"] = {}
                        self.settings[away_team]["goal_id"] = {}
                        to_remove.append(link)

                for link in to_remove:
                    del games[games.index(link)]
                if games == []:
                    is_playing = False
                    break
                dataIO.save_json("data/hockey/settings.json", self.settings)
                await asyncio.sleep(60)
            print(is_playing)
            for team in self.settings:
                self.settings[team]["goal_id"] = {}
            dataIO.save_json("data/hockey/settings.json", self.settings)
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
        em = discord.Embed(timestamp=timestamp)       
        

        # Home team checking

        if game_state == "Preview":
            """Checks if the the game state has changes from Final to Preview
               Could be unnecessary since after Game Final it will check for next game
            """
            if self.settings[home_team]["game_state"] != game_state:
                self.settings[home_team]["game_state"] = game_state
                self.settings[home_team]["game_start"] = game_start
                self.settings[away_team]["game_state"] = game_state
                self.settings[away_team]["game_start"] = game_start
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
                    for channels in self.settings[state]["channel"]:
                        channel = self.bot.get_channel(id=channels)
                        await self.bot.send_message(channel, embed=em)
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
            if self.settings[home_team]["game_state"] != game_state:
                self.settings[home_team]["game_state"] = game_state
                msg = "**Game starting {} at {}**"
                print(msg.format(home_team, away_team))
                for state in post_state:
                    team = state if state != "all" else home_team
                    alt_team = [state for state in post_state if state != "all" and state != team][0]
                    em.colour = int(self.teams[team]["home"].replace("#", ""), 16)
                    logo = self.teams[team]["logo"]
                    alt_logo = self.teams[alt_team]["logo"]
                    em.set_author(name=title, url=team_url, icon_url=logo)
                    em.set_thumbnail(url=logo)
                    em.set_footer(text="Game start ", icon_url=alt_logo)
                    for channels in self.settings[state]["channel"]:
                        channel = self.bot.get_channel(id=channels)
                        server = channel.server
                        home_role, away_role = await self.get_team_role(server, home_team, away_team)
                        await self.bot.send_message(channel, msg.format(home_role, away_role), embed=em)

            if self.settings[home_team]["period"] != period:
                self.settings[home_team]["period"] = period
                self.settings[away_team]["period"] = period
                self.settings[home_team]["game_state"] = game_state
                msg = "**{} Period starting {} at {}**"
                print(msg.format(period_ord, home_team, away_team))
                for state in post_state:
                    team = state if state != "all" else home_team
                    alt_team = [state for state in post_state if state != "all" and state != team][0]
                    em.colour = int(self.teams[team]["home"].replace("#", ""), 16)
                    logo = self.teams[team]["logo"]
                    alt_logo = self.teams[alt_team]["logo"]
                    em.set_author(name=title, url=team_url, icon_url=logo)
                    em.set_thumbnail(url=logo)
                    em.set_footer(text="Game start ", icon_url=alt_logo)
                    for channels in self.settings[state]["channel"]:
                        channel = self.bot.get_channel(id=channels)
                        server = channel.server
                        # print(home_role)
                        home_role, away_role = await self.get_team_role(server, home_team, away_team)
                        await self.bot.send_message(channel, msg.format(period_ord, home_role, away_role), embed=em)
            # Say game starting in all channels


        if game_state == "Final":
            """Final game state checks"""

            if self.settings[home_team]["game_state"] != game_state and self.settings[home_team]["game_state"] != "Null":
                self.settings[home_team]["game_state"] = "Null"
                self.settings[away_team]["game_state"] = "Null"
                self.settings[home_team]["period"] = 1
                self.settings[away_team]["period"] = 1
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
                    for channels in self.settings[state]["channel"]:
                        channel = self.bot.get_channel(id=channels)
                        server = channel.server
                        await self.bot.send_message(channel, embed=em)

        

        
    async def get_team_role(self, server, home_team, away_team):
        home_role = None
        away_role = None
        for role in server.roles:
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
        goal_ids = [str(goal_id["result"]["eventCode"]) for goal_id in goals]
        goal_list = list(self.settings[team]["goal_id"])
        all_goal_list = list(self.settings["all"]["goal_id"])
        # print(goals)
        for goal in goals:
            goal_id = str(goal["result"]["eventCode"])
            if not is_all:
                if goal_id not in goal_list:
                    # Posts goal information and saves data for verification later
                    msg_list = await self.post_team_goal(goal, team, score_msg)
                    self.settings[team]["goal_id"][goal_id] = {"goal":goal,"messages":msg_list}
                if goal_id in goal_list:
                    # Checks if the goal data has changed and edits all previous posts with new data
                    old_goal = self.settings[team]["goal_id"][goal_id]["goal"]
                    if goal != old_goal:
                        print("attempting to edit")
                        old_msgs = self.settings[team]["goal_id"][goal_id]["messages"]
                        self.settings[team]["goal_id"][goal_id]["goal"] = goal
                        await self.post_team_goal(goal, team, score_msg, old_msgs)
            if is_all:
                # print("all")
                if goal_id not in all_goal_list:
                    msg_list = await self.post_team_goal(goal, "all", score_msg)
                    self.settings["all"]["goal_id"][goal_id] = {"goal":goal, "messages":msg_list}
                if goal_id in all_goal_list:
                    old_goal = self.settings["all"]["goal_id"][goal_id]["goal"]
                    if goal != old_goal:
                        print("attempting to edit")
                        old_msgs = self.settings["all"]["goal_id"][goal_id]["messages"]
                        self.settings["all"]["goal_id"][goal_id]["goal"] = goal
                        await self.post_team_goal(goal, "all", score_msg, old_msgs)
        if not is_all:
            # to_remove = [goal for goal in goal_list if goal not in goal_ids]
            for old_goal in goal_list:
                # print(old_goal)
                if old_goal not in goal_ids:
                    print(old_goal)
                    try:
                        old_msgs = self.settings[team]["goal_id"][old_goal]["messages"].items()
                    except Exception as e:
                        print(e)
                        continue
                    for channel_id, message_id in old_msgs:
                        channel = self.bot.get_channel(id=channel_id)
                        try:
                            message = await self.bot.get_message(channel, message_id)
                            await self.bot.delete_message(message)
                            
                        except Exception as e:
                            print("something wrong with {} {}: {}".format(team, old_goal, e))
                            pass
                        try:
                            del self.settings[team]["goal_id"][old_goal]
                        except Exception as e:
                            print(e)
                            pass
                        print("done")
                    try:
                        all_old_msgs = self.settings["all"]["goal_id"][old_goal]["messages"].items()
                    except Exception as e:
                        print(e)
                        continue
                    
                    for channel_id, message_id in all_old_msgs:
                        try:
                            channel = self.bot.get_channel(id=channel_id)
                            message = await self.bot.get_message(channel, message_id)
                            await self.bot.delete_message(message)
                        except Exception as e:
                            print("something wrong with all {}: {}".format(old_goal, e))
                            pass
                        try:
                            del self.settings["all"]["goal_id"][old_goal]
                        except Exception as e:
                            print(e)
                            pass
                    print("should reach here")

    async def post_team_goal(self, goal, team, score_msg, og_msg=None):
        """Creates embed and sends message if a team has scored a goal"""
        
        scorer = self.headshots.format(goal["players"][0]["player"]["id"])
        scoring_team = self.teams[goal["team"]["name"]]
        period = goal["about"]["ordinalNum"]
        home = goal["about"]["goals"]["home"]
        away = goal["about"]["goals"]["away"]
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
            em = discord.Embed(description=strength + " " + event + " by " + goal["result"]["description"],
                               colour=int(self.teams[goal["team"]["name"]]["home"].replace("#", ""), 16))
            em.set_author(name="🚨 " + goal["team"]["name"] + " " + strength + " " + event + " 🚨", 
                          url=self.teams[goal["team"]["name"]]["team_url"],
                          icon_url=self.teams[goal["team"]["name"]]["logo"])
            home_str = "Goals: **{}** \nShots: **{}**".format(home, score_msg["Home Shots"])
            away_str = "Goals: **{}** \nShots: **{}**".format(away, score_msg["Away Shots"])
            em.add_field(name=score_msg["Home"], value=home_str, inline=True)
            em.add_field(name=score_msg["Away"], value=away_str, inline=True)
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
            for channels in self.settings[team]["channel"]:
                role = None
                channel = self.bot.get_channel(id=channels)
                server = channel.server
                for roles in server.roles:
                    if roles.name == goal["team"]["name"] + " GOAL":
                        role = roles
                try:
                    if role is None or "missed" in event.lower():
                        msg = await self.bot.send_message(channel, embed=em)
                        msg_list[channel.id] = msg.id
                    else:  
                        msg = await self.bot.send_message(channel, role.mention, embed=em)
                        msg_list[channel.id] = msg.id
                except:
                    print("Could not post goal in {}".format(channels))
                    pass
            # print(msg_list)
            return msg_list
        else:
            for channel_id, message_id in og_msg.items():
                role = None
                channel = self.bot.get_channel(id=channel_id)
                # print("channel {} ID {}".format(channel, message_id))
                message = await self.bot.get_message(channel, message_id)
                # print("I can get the message")
                server = message.server
                for roles in server.roles:
                    if roles.name == goal["team"]["name"] + " GOAL":
                        role = roles
                if role is None or "missed" in event.lower():
                    await self.bot.edit_message(message, embed=em)
                else:  
                    await self.bot.edit_message(message, role.mention, embed=em)
            return

    @commands.group(pass_context=True, name="hockey", aliases=["nhl"])
    async def hockey_commands(self, ctx):
        """Various Hockey related commands"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @hockey_commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def hockeytwitter(self, ctx):
        server = self.bot.get_server(id="381567805495181344")
        for team in self.teams:
            team = team.replace(".", "")
            team = team.replace(" ", "-")
            if team.startswith("Montr"):
                team = "montreal-canadiens"
            await self.bot.create_channel(server, name=team.lower() + "-twitter")

    @hockey_commands.command(pass_context=True, hidden=True, name="reset")
    @checks.is_owner()
    async def reset_hockey(self, ctx):
        for team in self.settings:
            self.settings[team]["goal_id"] = {}
        dataIO.save_json("data/hockey/settings.json", self.settings)
        await self.bot.say("Cleared saved hockey data.")


    @hockey_commands.command(pass_context=True, name="add", aliases=["add_goals"])
    @checks.admin_or_permissions(manage_channels=True)
    async def add_goals(self, ctx, team, channel:discord.Channel=None):
        """Adds a hockey team goal updates to a channel"""
        if team.lower() == "all":
            team = "all"
        else:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await self.bot.say("{} is not an available team!".format(team))
                return
        if channel is None:
            channel = ctx.message.channel
        if team not in self.settings:
            self.settings[team] = {"channel":[channel.id], "goal_id": {}}
        if channel.id in self.settings[team]["channel"]:
            await self.bot.send_message(ctx.message.channel, "I am already posting {} goals in {}!".format(team, channel.mention))
            return
        self.settings[team]["channel"].append(channel.id)
        dataIO.save_json("data/hockey/settings.json", self.settings)
        await self.bot.say("{} goals will be posted in {}".format(team, channel.mention))


    @hockey_commands.command(pass_context=True, name="del", aliases=["remove", "rem"])
    @checks.admin_or_permissions(manage_channels=True)
    async def remove_goals(self, ctx, team, channel:discord.Channel=None):
        """Removes a teams goal updates from a channel"""
        if team.lower() == "all":
            team = "all"
        else:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await self.bot.say("{} is not an available team!".format(team))
                return
        if channel is None:
            channel = ctx.message.channel
        if team not in self.settings:
            await self.bot.send_message(ctx.message.channel, "I am not posting {} goals in {}".format(team, channel.mention))
            return
        if channel.id in self.settings[team]["channel"]:
            self.settings[team]["channel"].remove(channel.id)
            dataIO.save_json("data/hockey/settings.json", self.settings)
            await self.bot.say("{} goals will stop being posted in {}".format(team, channel.mention))

    @hockey_commands.command(pass_context=True, name="role")
    async def team_role(self, ctx, *, team):
        """Set your role to a team role"""
        server = ctx.message.server
        if server.id != "381567805495181344":
            await self.bot.send_message(ctx.message.channel, "Sorry that only works on TrustyJAID's Oilers Server!")
            return
        try:
            role = [role for role in server.roles if (team.lower() in role.name.lower() and "GOAL" not in role.name)][0]
            await self.bot.add_roles(ctx.message.author, role)
            await self.bot.send_message(ctx.message.channel, "Role applied.")
        except:
            await self.bot.send_message(ctx.message.channel, "{} is not an available role!".format(team))

    @hockey_commands.command(pass_context=True, name="goals")
    async def team_goals(self, ctx, *, team=None):
        """Subscribe to goal notifications"""
        server = ctx.message.server
        member = ctx.message.author
        if server.id != "381567805495181344":
            await self.bot.send_message(ctx.message.channel, "Sorry that only works on TrustyJAID's Oilers Server!")
            return
        if team is None:
            team = [role.name for role in member.roles if role.name in self.teams]
            for t in team:
                role = [role for role in server.roles if role.name == t + " GOAL"]
                for roles in role:
                    await self.bot.add_roles(ctx.message.author, roles)
                await self.bot.send_message(ctx.message.channel, "Role applied.")
        else:
            try:
                role = [role for role in server.roles if (team.lower() in role.name.lower() and role.name.endswith("GOAL"))][0]
                await self.bot.add_roles(ctx.message.author, role)
                await self.bot.send_message(ctx.message.channel, "Role applied.")
            except:
                await self.bot.send_message(ctx.message.channel, "{} is not an available role!".format(team))

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
            home_msg = "{}\nGoals: **{}** \nShots: **{}**".format(h_emoji, home_score, home_shots)
            away_msg = "{}\nGoals: **{}** \nShots: **{}**".format(a_emoji, away_score, away_shots)
            em.add_field(name=home_team, value=home_msg)
            em.add_field(name=away_team, value=away_msg)
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
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == len(post_list) - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            try:
                await self.bot.remove_reaction(message, "➡", ctx.message.author)
            except:
                pass
            return await self.game_menu(ctx, post_list, team_set=team_set,
                                        message=message,
                                        page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            try:
                await self.bot.remove_reaction(message, "⬅", ctx.message.author)
            except:
                pass
            return await self.game_menu(ctx, post_list, team_set=team_set,
                                        message=message,
                                        page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

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
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == len(post_list) - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            try:
                await self.bot.remove_reaction(message, "➡", ctx.message.author)
            except:
                pass
            return await self.roster_menu(ctx, post_list,
                                        message=message,
                                        page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            try:
                await self.bot.remove_reaction(message, "⬅", ctx.message.author)
            except:
                pass
            return await self.roster_menu(ctx, post_list,
                                        message=message,
                                        page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

    @hockey_commands.command(pass_context=True)
    async def emojis(self, ctx):
        emoji = ""
        for team in self.teams:
            await self.bot.say("<:" + self.teams[team]["emoji"] + "> ")
        # await self.bot.say(emoji)

    async def standings_menu(self, ctx, post_list: list,
                         display_type,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        # Change between standing pages
        em = discord.Embed()
        standing_list = post_list[page]
        
        if display_type == "division":
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
                msg = "GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**".format(pl=pl,emoji=emoji, wins=wins, losses=losses, ot=ot, pts=pts, gp=gp)
                timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
                em.add_field(name=pl + ". " + emoji + " " + team_name, value=msg, inline=True)
                em.timestamp = timestamp
                em.set_footer(text="Stats last Updated")
            if conference == "Eastern":
                em.colour = int("c41230", 16)
                em.set_author(name=division + " Division", url="https://www.nhl.com/standings")#, icon_url="https://upload.wikimedia.org/wikipedia/en/thumb/1/16/NHL_Eastern_Conference.svg/1280px-NHL_Eastern_Conference.svg.png")
            if conference == "Western":
                em.colour = int("003e7e", 16)
                em.set_author(name=division + " Division", url="https://www.nhl.com/standings")#, icon_url="https://upload.wikimedia.org/wikipedia/en/thumb/6/65/NHL_Western_Conference.svg/1280px-NHL_Western_Conference.svg.png")
        if display_type == "conference":
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
        if display_type == "teams":
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


        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == len(post_list) - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            try:
                await self.bot.remove_reaction(message, "➡", ctx.message.author)
            except:
                pass
            return await self.standings_menu(ctx, post_list,
                                        display_type=display_type,
                                        message=message,
                                        page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            try:
                await self.bot.remove_reaction(message, "⬅", ctx.message.author)
            except:
                pass
            return await self.standings_menu(ctx, post_list,
                                        display_type=display_type,
                                        message=message,
                                        page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

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

    def get_season(self):
        now = datetime.now()
        if (now.month, now.day) < (7, 1):
            return (now.year - 1, now.year)
        if (now.month, now.day) >= (7, 1):
            return (now.year, now.year + 1)

    @hockey_commands.command(pass_context=True, aliases=["score"])
    async def games(self, ctx, *, team=None):
        """Gets all NHL games this season or selected team"""
        games_list = []
        page_num = 0
        today = datetime.today()
        year = self.get_season()[0]
        year2 = self.get_season()[1]
        url = "{base}/api/v1/schedule?startDate={year}-9-1&endDate={year2}-9-1"\
              .format(base=self.url, year=year, year2=year2)
        
        if team is not None:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await self.bot.send_message(ctx.message.channel, "{} Does not appear to be an NHL team!".format(team))
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
            await self.bot.send_message(ctx.message.channel, "{} have no recent or upcoming games!".format(team))

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
                rosters[team] = data["roster"]
            
            for team in rosters:
                for player in rosters[team]:
                    if search.lower() in player["person"]["fullName"].lower():
                        players.append(player)
        
        if players != []:
            await self.roster_menu(ctx, players)
        else:
            await self.bot.send_message(ctx.message.channel, "{} is not an NHL team or Player!".format(search))

def check_folder():
    if not os.path.exists("data/hockey"):
        print("Creating data/tweets folder")
        os.makedirs("data/hockey")

def check_file():
    data = {}
    f = "data/hockey/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Hockey(bot))
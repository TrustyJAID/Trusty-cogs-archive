import discord
import aiohttp
import asyncio
import json
from datetime import datetime
from io import BytesIO
from redbot.core import commands, checks, Config
from .teams import teams
from .teamentry import TeamEntry
from .menu import hockey_menu
from .embeds import *
from .helper import *
from .errors import *
from .game import Game
from .pickems import Pickems
from.standings import Standings


try:
    from .oilers import Oilers
except ImportError:
    pass

__version__ = "2.2.0"
__author__ = "TrustyJAID"

class Hockey(commands.Cog):

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
                         "create_channels":False, "category":None, "gdc_team":None, "gdc":[], "delete_gdc":True,
                         "rules":"", "team_rules":"", "pickems": [], "leaderboard":[]}
        default_channel = {"team":[], "to_delete":False}

        self.config = Config.get_conf(self, 13457745779)
        self.config.register_global(**default_global, force_registration=True)
        self.url = "https://statsapi.web.nhl.com"
        self.teams = teams
        self.headshots = "https://nhl.bamcontent.com/images/headshots/current/168x168/{}.jpg"
        self.loop = bot.loop.create_task(self.get_team_goals())

    ##############################################################################
    # Here is all the logic for gathering game data and updating information

    async def get_day_games(self):
        """
            Gets all current games for the day as a list of game objects
        """
        async with self.session.get(self.url + "/api/v1/schedule") as resp:
            data = await resp.json()
        game_list = []
        for link in data["dates"][0]["games"]:
            try:
                async with self.session.get(self.url + link["link"]) as resp:
                    data = await resp.json()
                game_list.append(await Game.from_json(data))
            except Exception as e:
                print("error here {}".format(e))
                continue
        return game_list

    @commands.command() 
    @checks.is_owner()
    async def getgoals(self, ctx):  
        """Loop to check what teams are playing and see if a goal was scored""" 
        to_remove = []  
        games_playing = True    
        # print(link)   
        with open("/mnt/e/github/Trusty-cogs/hockeytest/testgame.json", "r") as infile: 
            data = json.loads(infile.read())    
        # print(data)   
        game_data = await Game.from_json(data)  
        await self.check_game_state(game_data)                  
        if (game_data.home_score + game_data.away_score) != 0:  
            await self.check_team_goals(game_data)

    async def refactor_data(self):
        chan_list = await self.config.all_channels()
        for channel_id in chan_list:
            channel = self.bot.get_channel(id=channel_id)
            if channel is None:
                continue
            teams = await self.config.channel(channel).team()
            if type(teams) is not list:
                await self.config.channel(channel).team.set([teams])

    async def get_team_goals(self):
        """
            This loop grabs the current games for the day then passes off to other functions as necessary
        """
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Hockey"):
            await self.refactor_data()
            async with self.session.get(self.url + "/api/v1/schedule") as resp:
                data = await resp.json()
            if data["dates"] != []:
                games = [game["link"] for game in data["dates"][0]["games"] if game["status"]["abstractGameState"] != "Final"]
            else:
                games = []
            games_playing = False
            while games != []:
                to_remove = []
                games_playing = True
                for link in games:
                    try:
                        async with self.session.get(self.url + link) as resp:
                            data = await resp.json()
                    except Exception as e:
                        print(e)
                        continue
                    game_data = await Game.from_json(data)
                    await self.check_game_state(game_data)

                    print("{} @ {}".format(game_data.away_team, game_data.home_team))

                    if game_data.game_state == "Final":
                        all_teams = await self.config.teams()
                        home = await self.get_team(game_data.home_team)
                        away = await self.get_team(game_data.away_team)
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
                await asyncio.sleep(60)
            print("Games Done Playing")
            if games_playing:
                await self.config.created_gdc.set(False)
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

    async def save_game_state(self, data, time_to_game_start:str="0"):
        home = await self.get_team(data.home_team)
        away = await self.get_team(data.away_team)
        team_list = await self.config.teams()
        team_list.remove(home)
        team_list.remove(away)
        if data.game_state != "Final":
            if data.game_state == "Preview" and time_to_game_start != "0":
                home["game_state"] = data.game_state+time_to_game_start
                away["game_state"] = data.game_state+time_to_game_start
            else:
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
        await self.config.teams.set(team_list)

    async def post_time_to_game_start(self, data, time_left):
        """
            Post when there is 60, 30, and 10 minutes until the game starts in all channels
        """
        post_state = ["all", data.home_team, data.away_team]
            
        for channels in await self.config.all_channels():
            channel = self.bot.get_channel(id=channels)
            if channel is None:
                continue

            should_post = await self.check_to_post(channel, post_state)
            team_to_post = await self.config.channel(channel).team()
            if should_post and "all" not in team_to_post:
                guild = channel.guild
                msg = "{} minutes until {} {} @ {} {} starts".format(time_left, data.away_emoji, data.away_team,
                       data.home_emoji, data.home_team)
                try:
                    await channel.send(msg)
                except Exception as e:
                    print("Problem posting in channel <#{}> : {}".format(channels, e))

    async def check_game_state(self, data):
        post_state = ["all", data.home_team, data.away_team]
        home = await self.get_team(data.home_team)
        away = await self.get_team(data.away_team)
        team_list = await self.config.teams()
        # Home team checking

        if data.game_state == "Preview":
            """Checks if the the game state has changes from Final to Preview
               Could be unnecessary since after Game Final it will check for next game
            """
            time_now = datetime.utcnow()
            game_time = datetime.strptime(data.game_start, "%Y-%m-%dT%H:%M:%SZ")
            game_start = (game_time - time_now).total_seconds()/60
            if "Preview" not in home["game_state"]:
                
                if not await self.config.created_gdc():
                    try:
                        await self.post_automatic_standings()
                    except Exception as e:
                        print(e)
                    await self.check_new_gdc()
                    await self.config.created_gdc.set(True)
                await self.post_game_state(data)
                await self.save_game_state(data)
            if game_start < 60 and game_start > 30 and home["game_state"] != "Preview60":
                # Post 60 minutes until game start
                await self.post_time_to_game_start(data, "60")
                await self.save_game_state(data, "60")
            if game_start < 30 and game_start >10 and home["game_state"] != "Preview30":
                # Post 30 minutes until game start
                await self.post_time_to_game_start(data, "30")
                await self.save_game_state(data, "30")
            if game_start < 10 and game_start > 0 and home["game_state"] != "Preview10":
                # Post 10 minutes until game start
                await self.post_time_to_game_start(data, "10")
                await self.save_game_state(data, "10")

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

    async def get_next_game(self, team, date=None):
        """
            Gets all NHL games this season or selected team
        """
        games_list = []
        page_num = 0
        if date is None:
            today = datetime.now()
        else:
            today = date
        url = "{base}/api/v1/schedule?startDate={year}-9-1&endDate={year2}-9-1"\
              .format(base=self.url, year=get_season()[0], year2=get_season()[1])
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


    async def check_team_goals(self, data):
        """
            Checks to see if a goal needs to be posted
        """
        home_team_data = await self.get_team(data.home_team)
        away_team_data = await self.get_team(data.away_team)
        all_data = await self.get_team("all")
        team_list = await self.config.teams()
        post_state = ["all", data.home_team, data.away_team]
        
        home_goal_ids = [str(goal_id["result"]["eventCode"]) for goal_id in data.home_goals]
        away_goal_ids = [str(goal_id["result"]["eventCode"]) for goal_id in data.away_goals]

        home_goal_list = list(home_team_data["goal_id"])
        away_goal_list = list(away_team_data["goal_id"])

        for goal in data.goals:
            goal_id = str(goal["result"]["eventCode"])
            team = goal["team"]["name"]
            team_data = await self.get_team(team)
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
        """
            Attempt to delete a goal if it was pulled back
        """
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
                    print("Cannot find message {} {}: {}".format(team, goal, e))
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

    async def check_to_post(self, channel, post_state):
        channel_teams = await self.config.channel(channel).team()
        should_post = False
        for team in channel_teams:
            if team in post_state:
                should_post = True
        return should_post

    async def post_team_goal(self, goal, game_data):
        """
            Creates embed and sends message if a team has scored a goal
        """
        scorer = self.headshots.format(goal["players"][0]["player"]["id"])
        post_state = ["all", game_data.home_team, game_data.away_team]
        event = goal["result"]["event"]
        msg_list = {}
        if "oilers" in goal["team"]["name"].lower() and "missed" not in event.lower():
            try:
                hue = Oilers(self.bot)
                await hue.oilersgoal2()
            except:
                pass
        for channels in await self.config.all_channels():
            role = None
            channel = self.bot.get_channel(id=channels)
            if channel is None:
                continue
            should_post = await self.check_to_post(channel, post_state)
            if should_post:
                try:
                    guild = channel.guild
                    game_day_channels = await self.config.guild(guild).gdc()
                    # Don't want to ping people in the game day channels
                    if not channel.permissions_for(guild.me).embed_links:
                        em = await goal_post_text(goal, game_data)
                        msg = await channel.send(em)
                        msg_list[str(channel.id)] = msg.id
                        continue
                    for roles in guild.roles:
                        if roles.name == goal["team"]["name"] + " GOAL":
                            role = roles
                    if game_day_channels is not None:
                        # We don't want to ping people in the game day channels twice
                        if channel.id in game_day_channels:
                            role = None
                    if role is None or "missed" in event.lower():
                        em = await goal_post_embed(goal, game_data)
                        msg = await channel.send(embed=em)
                        msg_list[str(channel.id)] = msg.id
                    else:
                        em = await goal_post_embed(goal, game_data)
                        msg = await channel.send(role.mention, embed=em)
                        msg_list[str(channel.id)] = msg.id
                except Exception as e:
                    print("Could not post goal in {}: {}".format(channels, e))
                    pass
        return msg_list

    async def edit_team_goal(self, goal, game_data, og_msg):
        """
            When a goal scorer has changed we want to edit the original post
        """
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
                if not channel.permissions_for(channel.guild.me).embed_links:
                    continue
                message = await channel.get_message(message_id)
                guild = message.guild
                game_day_channels = await self.config.guild(guild).gdc()
                for roles in guild.roles:
                    if roles.name == goal["team"]["name"] + " GOAL":
                        role = roles
                if game_day_channels is not None:
                        # We don't want to ping people in the game day channels twice
                        if channel.id in game_day_channels:
                            role = None
                if role is None or "missed" in event.lower():
                    await message.edit(embed=em)
                else:  
                    await message.edit(content=role.mention, embed=em)
            except:
                print("Could not edit goal in {}".format(channel_id))
        return

    async def check_new_gdc(self):
        print("Checking GDC")
        game_list = await self.get_day_games()
        for guilds in await self.config.all_guilds():
            guild = self.bot.get_guild(guilds)
            if guild is None:
                continue
            if not await self.config.guild(guild).create_channels():
                continue
            team = await self.config.guild(guild).gdc_team()
            if team != "all":
                next_game = await self.get_next_game(team)
                # print(next_game)
                chn_name = await get_chn_name(next_game)
                try:
                    cur_channels = await self.config.guild(guild).gdc()
                    cur_channel = self.bot.get_channel(cur_channels[0])
                except Exception as e:
                    print(e)
                    cur_channel = None
                if cur_channel is None:
                    await self.create_gdc(guild)
                elif cur_channel.name != chn_name.lower():
                    await self.delete_gdc(guild)
                    await self.create_gdc(guild)
                
            else:
                await self.delete_gdc(guild)
                for game in game_list:
                    await self.create_gdc(guild, game)

    async def create_gdc(self, guild, game_data=None):
        """
            Creates a game day channel for the given game object
            if no game object is passed it looks for the set team for the guild
            returns None if not setup
        """
        print("making Game Day channels")
        category = self.bot.get_channel(await self.config.guild(guild).category())
        if category is None:
            # Return none if there's no category to create the channel
            return
        if game_data is None:
            team = await self.config.guild(guild).gdc_team()
            
            next_game = await self.get_next_game(team)
        else:
            team = game_data.home_team
            next_game = game_data
        if next_game is None:
            return
        chn_name = await get_chn_name(next_game)
        new_chn = await guild.create_text_channel(chn_name, category=category)
        cur_channels = await self.config.guild(guild).gdc()
        if cur_channels is None:
            cur_channels = []
        cur_channels.append(new_chn.id)
        await self.config.guild(guild).gdc.set(cur_channels)
        await self.config.guild(guild).create_channels.set(True)
        await self.config.channel(new_chn).team.set([team])
        delete_gdc = await self.config.guild(guild).delete_gdc()
        await self.config.channel(new_chn).to_delete.set(delete_gdc)

        # Gets the timezone to use for game day channel topic
        timestamp = datetime.strptime(next_game.game_start, "%Y-%m-%dT%H:%M:%SZ")
        guild_team = await self.config.guild(guild).gdc_team()
        channel_team = guild_team if guild_team != "all" else next_game.home_team
        timezone = self.teams[channel_team]["timezone"]
        time_string = utc_to_local(timestamp, timezone).strftime("%A %B %d, %Y at %I:%M %p %Z")

        game_msg = "{} {} @ {} {} {}".format(next_game.away_team, next_game.away_emoji,\
                                                   next_game.home_team, next_game.home_emoji,\
                                                   time_string)
        await new_chn.edit(topic=game_msg)
        if new_chn.permissions_for(guild.me).embed_links:
            em = await game_state_embed(next_game)
            preview_msg = await new_chn.send(embed=em)
        else:
            preview_msg = await new_chn.send(await game_state_text(next_game))

        # Create new pickems object for the game
        pickems = await self.config.guild(guild).pickems()
        if pickems is None:
            pickems = []
        new_pickem = Pickems(preview_msg.id, new_chn.id, next_game.game_start,
                             next_game.home_team, next_game.away_team, [])
        pickems.append(new_pickem.to_json())
        await self.config.guild(guild).pickems.set(pickems)
        


        if new_chn.permissions_for(guild.me).manage_messages:
            await preview_msg.pin()
        if new_chn.permissions_for(guild.me).add_reactions:
            try:
                await preview_msg.add_reaction(next_game.home_emoji[2:-1])
                await preview_msg.add_reaction(next_game.away_emoji[2:-1])
            except Exception as e:
                print(e)

    async def set_pickem_winner(self, pickems):
        try:
            # First try the home team games list
            game = await self.get_next_game(pickems.home_team, pickems.game_start)
        except:
            try:
                # Then try the away team game list
                game = await self.get_next_game(pickems.away_team, pickems.game_start)
            except:
                raise NotAValidTeamError()
        if game.home_score > game.away_score:
            pickems.winner = pickems.home_team
        if game.away_score > game.home_score:
            pickems.winner = pickems.away_team
        return pickems

    async def tally_leaderboard(self, guild, channel_id):
        """
            This should be where the pickems is removed and tallies are added
            to the leaderboard
        """
        pickem_list = [Pickems.from_json(p) for p in await self.config.guild(guild).pickems()]
        pickems = None
        for pickem in pickem_list:
            if str(channel_id) == str(pickem.channel):
                pickems = pickem
                pickem_list.remove(pickems)
        if pickems is None:
            return
        if pickems.winner is None:
            # Tries to get the winner if it wasn't already set
            try:
                pickems = await self.set_pickem_winner(pickems)
            except NotAValidTeamError:
                pass
        if pickems.winner is not None:
            leaderboard = await self.config.guild(guild).leaderboard()
            if leaderboard is None:
                leaderboard = {}
            for user, choice in pickems.votes:
                if choice == pickems.winner:
                    if str(user) not in leaderboard:
                        leaderboard[str(user)] = 1
                    else:
                        leaderboard[str(user)] += 1
            await self.config.guild(guild).leaderboard.set(leaderboard)
        await self.config.guild(guild).pickems.set(pickem_list)

    async def delete_gdc(self, guild):
        """
            Deletes all game day channels in a given guild
        """
        channels = await self.config.guild(guild).gdc()
        
        for channel in channels:
            chn = self.bot.get_channel(channel)
            if chn is None:
                try:
                    await self.config._clear_scope(Config.CHANNEL, str(chn))
                except:
                    pass
                continue
            await self.tally_leaderboard(guild, chn.id)
            if not await self.config.channel(chn).to_delete():
                continue
            try:
                await self.config.channel(chn).clear()
                await chn.delete()
            except Exception as e:
                print(e)
        await self.config.guild(guild).gdc.set([])

    async def post_game_state(self, data):
        """
            When a game state has changed this is called to create the embed
            and post in all channels
        """
        post_state = ["all", data.home_team, data.away_team]
            
        for channels in await self.config.all_channels():
            channel = self.bot.get_channel(id=channels)
            if channel is None:
                continue

            should_post = await self.check_to_post(channel, post_state)
            if should_post:
                guild = channel.guild
                game_day_channels = await self.config.guild(guild).gdc()
                if data.game_state == "Live":
                    msg = "**{} Period starting {} at {}**"
                    home_role, away_role = await get_team_role(guild, data.home_team, data.away_team)
                    if game_day_channels is not None:
                        # We don't want to ping people in the game day channels twice
                        if channel.id in game_day_channels:
                            home_role, away_role = data.home_team, data.away_team
                    try:
                        if not channel.permissions_for(guild.me).embed_links:
                            em = await game_state_text(data)
                            await channel.send(msg.format(data.period_ord, away_role, home_role)+"\n{}".format(em))
                        else:
                            em = await game_state_embed(data)
                            await channel.send(msg.format(data.period_ord, away_role, home_role), embed=em)
                    except Exception as e:
                            print("Problem posting in channel <#{}> : {}".format(channels, e)) 
                
                else:
                    if data.game_state == "Preview":
                        print(data.game_state)
                        if game_day_channels is not None:
                            # Don't post the preview message twice in the channel
                            if channel.id in game_day_channels:
                                continue
                    try:
                        if not channel.permissions_for(guild.me).embed_links:
                            await channel.send(await game_state_text(data))
                        else:
                            await channel.send(embed=await game_state_embed(data))
                    except Exception as e:
                        print("Problem posting in channel <#{}> : {}".format(channels, e))


    async def post_automatic_standings(self):
        """
            Automatically update a standings embed with the latest stats
            run when new games for the day is updated
        """
        print("Updating Standings.")
        all_guilds = await self.config.all_guilds()
        for guilds in all_guilds:
            try:
                guild = self.bot.get_guild(guilds)
                print(guild.name)
            except:
                continue
            if await self.config.guild(guild).post_standings():

                search = await self.config.guild(guild).standings_type()
                if search is None:
                    continue
                standings_channel = await self.config.guild(guild).standings_channel()
                if standings_channel is None:
                    continue
                channel = self.bot.get_channel(standings_channel)
                if channel is None:
                    continue
                standings_msg = await self.config.guild(guild).standings_msg()
                if standings_msg is None:
                    continue
                message = await channel.get_message(standings_msg)

                standings, page = await get_team_standings(search)
                if search != "all":
                    em = await build_standing_embed(await get_team_standings(search))
                else:
                    em = await all_standing_embed(await get_team_standings(search))
                if message is not None:
                    await message.edit(embed=em)

    async def get_team_channels(self, team):
        for teams in await self.config.teams():
            if teams["team_name"] == team:
                return teams["channel"]
        return []

    async def get_team(self, team):
        return_team = None
        team_list = await self.config.teams()
        for teams in team_list:
            if team == teams["team_name"]:
                return_team = team
                return teams
        if return_team is None:
            # Add unknown teams to the config to track stats
            return_team = TeamEntry("Null", team, 0, [], {}, [], "")
            team_list.append(return_team.to_json())
            await self.config.teams.set(team_list)
            return await self.get_team(team)

    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(id=payload.channel_id)
        try:
            guild = channel.guild
        except:
            return
        pickems_list = await self.config.guild(guild).pickems()
        
        if pickem_list is None:
            return
        pickems = [Pickems.from_json(p) for p in pickems_list]
        if len(pickems) == 0:
            return
        try:
            msg = await channel.get_message(id=payload.message_id)
        except:
            return        
        user = guild.get_member(payload.user_id)
        print(payload.user_id)
        if user.bot:
            return
        is_pickems_vote = False
        for pickem in pickems:
            if str(pickem.message) == str(msg.id):
                try:
                    #print(payload.emoji)
                    pickem.add_vote(user.id, payload.emoji)
                except UserHasVotedError:
                    print("User has already voted! Changing vote")
                    try:
                        emoji = pickem.home_emoji if str(payload.emoji.id) in pickem.away_emoji else pickem.away_emoji
                        await msg.remove_reaction(emoji, user)
                    except Exception as e:
                        print(e)
                except VotingHasEndedError:
                    try:
                        await msg.remove_reaction(payload.emoji, user)
                    except:
                        pass
                    print("Voting has ended")
        pickems_list = [p.to_json() for p in pickems]
        await self.config.guild(guild).pickems.set(pickems_list)
                





    ##############################################################################
    # Here are all the command functions to set certain attributes and settings

    @commands.group(name="hockey", aliases=["nhl"])
    async def hockey_commands(self, ctx):
        """Various Hockey related commands also aliased to `nhl`"""
        pass

    @hockey_commands.command(hidden=True)
    async def rempickem(self, ctx):
        await self.config.guild(ctx.guild).pickems.set([])
        await ctx.send("Done.")

    @commands.group()
    @checks.admin_or_permissions(manage_channels=True)
    async def gdc(self, ctx):
        """Game Day Channel setup for the server"""
        if ctx.invoked_subcommand is None:
            guild = ctx.message.guild
            create_channels = await self.config.guild(guild).create_channels()
            if create_channels is None:
                return
            team = await self.config.guild(guild).gdc_team()
            if team is None:
                team = "None"
            channels = await self.config.guild(guild).gdc()
            category = self.bot.get_channel(await self.config.guild(guild).category())
            delete_gdc = await self.config.guild(guild).delete_gdc()
            if category is not None:
                category = category.name
            if channels is not None:
                created_channels = ""
                for channel in channels:
                    chn = self.bot.get_channel(channel)
                    if chn is not None:
                        created_channels += chn.mention
                    else:
                        created_channels += "<#{}>\n".format(channel)
                if len(channels) == 0:
                    created_channels = "None"
            else:
                created_channels = "None"
            if not ctx.channel.permissions_for(guild.me).embed_links:
                msg = """GDC settings for {}\nCreate Game Day Channels:**{}**\nDelete Game Day Channels: **{}**\nTeam: **{}**\nCurrent Channels: {}
                """.format(guild.name, create_channels, delete_gdc, team, created_channels)
            if ctx.channel.permissions_for(guild.me).embed_links:
                em = discord.Embed(title="GDC settings for {}".format(guild.name))
                em.add_field(name="Create Game Day Channels", value=str(create_channels), inline=False)
                em.add_field(name="Delete Game Day Channels", value=str(delete_gdc), inline=False)
                em.add_field(name="Team", value=str(team), inline=False)
                em.add_field(name="Current Channels", value=created_channels, inline=False)
                await ctx.send(embed=em)
            else:
                await ctx.send(msg)

    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def lights(self, ctx):
        hue = Oilers(self.bot)
        await hue.oilersgoal2()

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


    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def add_team_data(self, ctx):
        all_teams = await self.config.teams()
        print(all_teams)
        for team in teams:
            if team not in [t["team_name"] for t in all_teams]:
                team_entry = TeamEntry("Null", team, 0, [], {}, [], "")
                all_teams.append(team_entry.to_json())
        if "all" not in all_teams:
            team_entry = TeamEntry("Null", "all", 0, [], {}, [], "")
            all_teams.append(team_entry.to_json())
        await self.config.teams.set(all_teams)

    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def testhockey(self, ctx):
        for channels in await self.config.all_channels():
            channel = self.bot.get_channel(channels)
            if channel is None:
                await self.config._clear_scope(Config.CHANNEL, str(channels))
                print(channels)
                continue
            chn = await self.config.channel(channel).team()
            print(chn)

    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def cleargdc(self, ctx):
        guild = ctx.message.guild
        good_channels = []
        for channels in await self.config.guild(guild).gdc():
            channel = self.bot.get_channel(channels)
            if channel is None:
                await self.config._clear_scope(Config.CHANNEL, str(channels))
                print(channels)
                continue
            else:
                good_channels.append(channel.id)
        await self.config.guild(guild).gdc.set(good_channels)

    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def clear_broken_channels(self, ctx):
        for channels in await self.config.all_channels():
            channel = self.bot.get_channel(channels)
            if channel is None:
                await self.config._clear_scope(Config.CHANNEL, str(channels))
                print(channels)
                continue
            # if await self.config.channel(channel).to_delete():
                # await self.config._clear_scope(Config.CHANNEL, str(channels))
        await ctx.send("done")

    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def remove_broken_guild(self, ctx):
        all_guilds = await self.config.all_guilds()
        for guilds in await self.config.all_guilds():
            guild = self.bot.get_guild(guilds)
            if guild is None:
                await self.config._clear_scope(Config.GUILD, str(guilds))
            else:
                if not await self.config.guild(guild).create_channels():
                    await self.config.guild(guild).gdc.set([])

        await ctx.send("Done.")

    @hockey_commands.command(hidden=True)
    @checks.is_owner()
    async def cogstats(self, ctx):
        all_channels = await self.config.all_channels()
        all_guilds = await self.config.all_guilds()
        guild_list = {}
        for channels in all_channels.keys():
            channel = self.bot.get_channel(channels)
            if channel is None:
                print(channels)
                continue
            if channel.guild.name not in guild_list:
                guild_list[channel.guild.name] = 1
            else:
                guild_list[channel.guild.name] += 1
        msg = "Servers:{}\nNumber of Channels: {}\nNumber of Servers: {}".format(
               guild_list, len(all_channels), len(all_guilds))
        print(guild_list)
        print(len(all_channels))
        print(len(all_guilds))


        await ctx.send("Done.")


    @gdc.command(name="delete")
    async def gdc_delete(self, ctx, guild_id:discord.Guild=None):
        """
            Delete all current game day channels for the server
        """
        if guild_id is None:
            guild_id = ctx.message.guild

        if await self.config.guild(guild_id).create_channels():
            await self.delete_gdc(guild_id)
        await ctx.send("Done.")

    @gdc.command(name="create")
    async def gdc_create(self, ctx, guild_id:discord.Guild=None):
        """
            Creates the next gdc for the server
        """
        if guild_id is None:
            guild_id = ctx.message.guild

        if await self.config.guild(guild_id).create_channels():
            await self.create_gdc(guild_id)
        await ctx.send("Done.")

    @gdc.command(name="toggle")
    async def gdc_toggle(self, ctx):
        """
            Toggles the game day channel creation on this server
        """
        guild = ctx.message.guild
        cur_setting = await self.config.guild(guild).create_channels()

        msg = "Okay, game day channels {} be created on this server."
        verb = "won't" if cur_setting else "will"
        await self.config.guild(guild).create_channels.set(not cur_setting)
        await ctx.send(msg.format(verb))

    @gdc.command(name="category")
    async def gdc_category(self, ctx, category:discord.CategoryChannel):
        """
            Change the category for channel creation. Channel is case sensitive.
        """
        guild = ctx.message.guild

        cur_setting = await self.config.guild(guild).category()

        msg = "Okay, game day channels be created in the {} category."
        await self.config.guild(guild).category.set(category.id)
        await ctx.send(msg.format(category.name))

    @gdc.command(name="autodelete")
    async def gdc_autodelete(self, ctx):
        """
            Toggle's auto deletion of game day channels.
        """
        guild = ctx.message.guild

        cur_setting = await self.config.guild(guild).delete_gdc()

        msg = "Okay, game day channels {} be deleted on this server.\nNote, this may not happen until the next set of games."
        verb = "won't" if cur_setting else "will"
        await self.config.guild(guild).delete_gdc.set(not cur_setting)
        await ctx.send(msg.format(verb))


    @gdc.command(hidden=True, name="test")
    @checks.is_owner()
    async def test_gdc(self, ctx):
        await self.check_new_gdc()


    @gdc.command(name="setup")
    async def gdc_setup(self, ctx, team, category:discord.CategoryChannel=None, delete_gdc:bool=True):
        """
            Setup game day channels for a single team or all teams
            Use quotes to specify the full team name and category if required
        """
        guild = ctx.message.guild
        if category is None:
            category = guild.get_channel(ctx.message.channel.category_id)
        if not category.permissions_for(guild.me).manage_channels:
            await ctx.send("I don't have permission to create or delete channels!")
            return
        team_list = await check_valid_team(team)
        if team_list == [] and team.lower() != "all":
            await ctx.send("{} is not a valid team!".format(team))
            return
        if len(team_list) > 1:
            team = await self.pick_team(ctx, team_list)
        else:
            team = team_list[0]

        await self.config.guild(guild).category.set(category.id)
        await self.config.guild(guild).gdc_team.set(team)
        await self.config.guild(guild).delete_gdc.set(delete_gdc)
        if team.lower() != "all":
            await self.create_gdc(guild)
        else:
            game_list = await self.get_day_games()
            for game in game_list:
                await self.create_gdc(guild, game)
        await ctx.send("Game Day Channels for {} setup in the {} category".format(team, category.name))


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
            em = await division_standing_embed(division_data, index)
        elif standings_type.lower() in conference:
            if standings_type.lower() == "eastern":
                em = await conference_standing_embed(conference_data, 0)
            else:
                em = await conference_standing_embed(conference_data, 1)
        elif standings_type == "all":
            em = await all_standing_embed(division_data, 0)
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

    @hockey_commands.command(name="add", aliases=["add_goals"])
    @checks.admin_or_permissions(manage_channels=True)
    async def add_goals(self, ctx, team, channel:discord.TextChannel=None):
        """Adds a hockey team goal updates to a channel do 'all' for all teams"""
        all_team_data = await self.config.teams()
        guild = ctx.message.guild
        team_name = await check_valid_team(team)
        if team_name == []:
            await ctx.send("{} is not an available team!".format(team))
            return
        if len(team_name) > 1:
                team_name = await pick_team(ctx, team_name)
        else:
            team_name = team_name[0]
        # team_data = await self.get_team(team)
        if channel is None:
            channel = ctx.message.channel
        if not channel.permissions_for(guild.me).embed_links:
            await ctx.send("I need embed_links enabled to post goal messages!")
            return
        await self.config.channel(channel).team.set(team_name)
        await ctx.send("{} goals will be posted in {}".format(team_name, channel.mention))


    @hockey_commands.command(name="del", aliases=["remove", "rem"])
    @checks.admin_or_permissions(manage_channels=True)
    async def remove_goals(self, ctx, channel:discord.TextChannel=None):
        """Removes a teams goal updates from a channel"""
        if channel is None:
            channel = ctx.message.channel
    
        await self.config.channel(channel).clear()
        await ctx.send("goals will stop being posted in {}".format(channel.mention))

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

    @hockey_commands.command(name="goals")
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

    @hockey_commands.command()
    async def standings(self, ctx, *, search=None):
        """Displays current standings for each division"""
        if search is None:
            standings, page = await get_team_standings("division")
            await hockey_menu(ctx, "standings", standings)
            return
        search_r = await check_valid_team(search, True)
        if search_r == []:
            await ctx.message.channel.send( "{} Does not appear to be a valid standing type!".format(search))
            return
        if len(search_r) > 1:
            search_r = await pick_team(ctx, search)
        else:
            search_r = search_r[0]

        standings, page = await get_team_standings(search_r.lower())
        if search != "all":
            await hockey_menu(ctx, "standings", standings, None, page)
        else:
            await hockey_menu(ctx, "all", standings, None, page) 


    @hockey_commands.command(aliases=["score"])
    async def games(self, ctx, *, team=None):
        """Gets all NHL games this season or selected team"""
        games_list = []
        page_num = 0
        today = datetime.now()
        url = "{base}/api/v1/schedule?startDate={year}-9-1&endDate={year2}-9-1"\
              .format(base=self.url, year=get_season()[0], year2=get_season()[1])
        
        if team is not None:
            team_search = await check_valid_team(team)
            if team_search == []:
                await ctx.message.channel.send( "{} Does not appear to be an NHL team!".format(team))
                return
            if len(team_search) > 1:
                team = await pick_team(ctx, team_search)
            else:
                team = team_search[0]
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

    @hockey_commands.command(aliases=["player"])
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
                try:
                    rosters[team] = data["roster"]
                except KeyError:
                    pass
            
            for team in rosters:
                for player in rosters[team]:
                    if search.lower() in player["person"]["fullName"].lower():
                        players.append(player)
        
        if players != []:
            await hockey_menu(ctx, "roster", players)
        else:
            await ctx.message.channel.send( "{} is not an NHL team or Player!".format(search))

    @hockey_commands.command(hidden=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def rules(self, ctx):
        if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            return
        rules = await self.config.guild(ctx.guild).rules()
        team = await self.config.guild(ctx.guild).team_rules()
        if rules == "":
            return
        em = await make_rules_embed(ctx.guild, team, rules)
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()
        await ctx.send(embed=em)

    @hockey_commands.command(hidden=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def setrules(self, ctx, team, *, rules):
        """Set the main rules page for the nhl rules command"""
        if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            await ctx.send("I need embed_links for this to work.")
            return
        team_search = await check_valid_team(team)
        if team_search == []:
            await ctx.message.channel.send( "{} Does not appear to be an NHL team!".format(team))
            return
        if len(team_search) > 1:
            team = await pick_team(ctx, team_search)
        else:
            team = team_search[0]
        await self.config.guild(ctx.guild).rules.set(rules)
        await self.config.guild(ctx.guild).team_rules.set(team)
        em = await make_rules_embed(ctx.guild, team, rules)
        await ctx.send("Done, here's how it will look.", embed=em)

    @hockey_commands.command(aliases=["link", "invite"])
    async def otherdiscords(self, ctx, team):
        """Gets the Specified teams discord server link"""
        if team not in ["all", "page"]:
            team_search = await check_valid_team(team)
            if team_search == []:
                await ctx.message.channel.send( "{} Does not appear to be an NHL team!".format(team))
                return
            if len(team_search) > 1:
                team = await pick_team(ctx, team_search)
            else:
                team = team_search[0]
            await ctx.send(teams[team]["invite"])
        else:
            if not ctx.channel.permissions_for(ctx.message.author).manage_messages:
                # Don't need everyone spamming this command
                return
            atlantic = [team for team in teams if teams[team]["division"] == "Atlantic"]
            metropolitan = [team for team in teams if teams[team]["division"] == "Metropolitan"]
            central = [team for team in teams if teams[team]["division"] == "Central"]
            pacific = [team for team in teams if teams[team]["division"] == "Pacific"]
            team_list = {"Atlantic":atlantic, "Metropolitan":metropolitan, "Central":central, "Pacific":pacific}
            msg1 = "__**Hockey Discord Master List**__\n```fix\n- Do not join other discords to troll.\n- Respect their rules & their members (Yes even the leafs & habs unfortunately).\n- We don't control the servers below. If you get banned we can not get you unbanned.\n- Don't be an asshole because then we all look like assholes. They won't see it as one asshole fan they will see it as a toxic fanbase.\n- Salt levels may vary. Your team is the best here but don't go on another discord and preach it to an angry mob after we just won.\n- Not following the above rules will result in appropriate punishments ranging from a warning to a ban. ```\n\nhttps://discord.gg/reddithockey"
            eastern_conference = "https://i.imgur.com/CtXvcCs.png"
            western_conference = "https://i.imgur.com/UFYJTDF.png"
            async with self.session.get(eastern_conference) as resp:
                data = await resp.read()
            logo = BytesIO()
            logo.write(data)
            logo.seek(0)
            image = discord.File(logo, filename="eastern_logo.png")
            await ctx.send(msg1, file=image)
            for division in team_list:
                if division == "Central":
                    async with self.session.get(western_conference) as resp:
                        data = await resp.read()
                    logo = BytesIO()
                    logo.write(data)
                    logo.seek(0)
                    image = discord.File(logo, filename="western_logo.png")
                    await ctx.send(file=image)
                div_emoji = "<:" + teams["Team {}".format(division)]["emoji"] + ">"
                msg = "{0} __**{1} DIVISION**__ {0}".format(div_emoji, division.upper())
                await ctx.send(msg)
                for team in team_list[division]:
                    team_emoji = "<:" + teams[team]["emoji"] + ">"
                    team_link = teams[team]["invite"]
                    msg = "{0} {1} {0}".format(team_emoji, team_link)
                    await ctx.send(msg)

    def __unload(self):
        self.bot.loop.create_task(self.session.close())
        self.loop.cancel()

    __del__ = __unload

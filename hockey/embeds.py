import discord
import aiohttp
from datetime import datetime
from .teams import teams
from .game import Game
from .helper import *
        

async def game_state_embed(data):
    post_state = ["all", data.home_team, data.away_team]
    timestamp = datetime.strptime(data.game_start, "%Y-%m-%dT%H:%M:%SZ")
    title = "{away} @ {home} {state}".format(away=data.away_team, home=data.home_team, state=data.game_state)
    em = discord.Embed(timestamp=timestamp)
    home_field = "{} {} {}".format(data.home_emoji, data.home_team, data.home_emoji)
    away_field = "{} {} {}".format(data.away_emoji, data.away_team, data.away_emoji)
    if data.game_state != "Preview":
        home_str = "Goals: **{}** \nShots: **{}**".format(data.home_score, data.home_shots)
        away_str = "Goals: **{}** \nShots: **{}**".format(data.away_score, data.away_shots)
    else:
        home_str, away_str = await get_stats_msg(data)
    em.add_field(name=home_field, value=home_str, inline=True)
    em.add_field(name=away_field, value=away_str, inline=True)
    colour = int(teams[data.home_team]["home"].replace("#", ""), 16)  if data.home_team in teams else None
    if colour is not None:
        em.colour = colour
    home_url = teams[data.home_team]["team_url"]  if data.home_team in teams else "https://nhl.com"
    em.set_author(name=title, url=home_url, icon_url=data.home_logo)
    em.set_thumbnail(url=data.home_logo)
    em.set_footer(text="Game start ", icon_url=data.away_logo)
    return em

async def game_state_text(data):
    post_state = ["all", data.home_team, data.away_team]
    timestamp = datetime.strptime(data.game_start, "%Y-%m-%dT%H:%M:%SZ")
    time_string = utc_to_local(timestamp).strftime("%I:%M %p %Z")
    em = "{a_emoji}{away} @ {h_emoji}{home} {state}\n({time})".format(a_emoji=data.away_emoji, away=data.away_team, 
             h_emoji= data.home_emoji, home=data.home_team, state=data.game_state, time=time_string)
    if data.game_state != "Preview":
        em = "**__Current Score__**\n{} {}: {}\n{} {}: {}".format(data.home_emoji, data.home_team, data.home_score,
               data.away_emoji, data.away_team, data.away_score)
    return em

async def make_rules_embed(guild, team, rules):
    warning = "***Any violation of the [Discord TOS](https://discordapp.com/terms) or [Community Guidelines](https://discordapp.com/guidelines) will result in immediate banning and possibly reported to discord.***"
    em = discord.Embed(colour=int(teams[team]["home"].replace("#", ""), 16))
    em.description = rules
    em.title = "__RULES__"
    em.add_field(name="__**WARNING**__", value=warning)
    em.set_thumbnail(url=guild.icon_url)
    em.set_author(name=guild.name, icon_url=guild.icon_url)
    return em

async def get_stats_msg(data):
    
    msg = "GP:**{gp}** W:**{wins}** L:**{losses}\n**OT:**{ot}** PTS:**{pts}** S:**{streak}**\n"
    streak_types = {"wins":"W", "losses":"L", "ot":"OT"}
    home_str = "GP:**0** W:**0** L:**0\n**OT:**0** PTS:**0** S:**0**\n"
    away_str = "GP:**0** W:**0** L:**0\n**OT:**0** PTS:**0** S:**0**\n"
    try:
        stats, home_i = await get_team_standings(data.home_team)
        for team in stats:
            if team.name == data.away_team:
                streak = "{} {}".format(team.streak, streak_types[team.streak_type].upper())
                away_str = msg.format(wins=team.wins, losses=team.losses,\
                             ot=team.ot, pts=team.pts, gp=team.gp, streak=streak)
            if team.name == data.home_team:
                streak = "{} {}".format(team.streak, streak_types[team.streak_type].upper())
                home_str = msg.format(wins=team.wins, losses=team.losses,\
                             ot=team.ot, pts=team.pts, gp=team.gp, streak=streak)
    except:
        pass
    return home_str, away_str

async def get_shootout_display(goals):
    msg = ""
    score = "☑"
    miss = "❌"
    for goal in goals:
        if goal["result"]["eventTypeId"] in ["SHOT", "MISSED_SHOT"] and goal["about"]["ordinalNum"] == "SO":
            msg += miss
        if goal["about"]["ordinalNum"] == "SO":
            msg += score
    return msg

async def goal_post_embed(goal, game_data):
    h_emoji = game_data.home_emoji
    a_emoji = game_data.away_emoji
    period_time_left = goal["about"]["periodTimeRemaining"]
    event = goal["result"]["event"]
    shootout = False
    if game_data.period_ord == "SO":
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
    description = goal["result"]["description"]
    colour = int(teams[goal["team"]["name"]]["home"].replace("#", ""), 16)  if goal["team"]["name"] in teams else None
    title = "🚨 {} {} {} 🚨".format(goal["team"]["name"], strength, event)
    url = teams[goal["team"]["name"]]["team_url"] if goal["team"]["name"] in teams else "https://nhl.com"
    logo = teams[goal["team"]["name"]]["logo"] if goal["team"]["name"] in teams else "https://nhl.com"
    if not shootout:
        
        em = discord.Embed(description=description)
        if colour is not None:
            em.colour = colour
        em.set_author(name=title, url=url, icon_url=logo)
        home_str = "Goals: **{}** \nShots: **{}**".format(game_data.home_score, game_data.home_shots)
        away_str = "Goals: **{}** \nShots: **{}**".format(game_data.away_score, game_data.away_shots)
        home_field = "{} {} {}".format(game_data.home_emoji, game_data.home_team, game_data.home_emoji)
        away_field = "{} {} {}".format(game_data.away_emoji, game_data.away_team, game_data.away_emoji)
        em.add_field(name=home_field, value=home_str, inline=True)
        em.add_field(name=away_field, value=away_str, inline=True)
        em.set_footer(text="{} left in the {} period".format(period_time_left, game_data.period_ord), icon_url=logo)
        em.timestamp = datetime.strptime(goal["about"]["dateTime"], "%Y-%m-%dT%H:%M:%SZ")
    else:
        if "missed" in event.lower():
            em = discord.Embed(description=description, colour=colour)
            em.set_author(name=title.replace("🚨", ""), url=url, icon_url=logo)
        else:
            em = discord.Embed(description=description, colour=colour)
            em.set_author(name=title, url=url, icon_url=logo)
        home_msg = await get_shootout_display(game_data.home_goals)
        away_msg = await get_shootout_display(game_data.away_goals)
        em.add_field(name=game_data.home_team, value=home_msg)
        em.add_field(name=game_data.away_team, value=away_msg)
        em.set_footer(text="{} left in the {} period".format(period_time_left, game_data.period_ord), icon_url=logo)
        em.timestamp = datetime.strptime(goal["about"]["dateTime"], "%Y-%m-%dT%H:%M:%SZ")
    return em

async def goal_post_text(goal, game_data):
    h_emoji = game_data.home_emoji
    a_emoji = game_data.away_emoji
    period_time_left = goal["about"]["periodTimeRemaining"]
    event = goal["result"]["event"]
    shootout = False
    if game_data.period_ord == "SO":
        shootout = True
    if not shootout:        
        em = "{} {}: {}\n{} {}: {}\n ({} left in the {} period)".format(h_emoji, game_data.home_team, game_data.home_score,
               a_emoji, game_data.away_team, game_data.away_score, period_time_left, game_data.period_ord)
    else:
        home_msg = await get_shootout_display(game_data.home_goals)
        away_msg = await get_shootout_display(game_data.away_goals)
        em = "{} {}: {}\n{} {}: {}\n ({} left in the {} period)".format(h_emoji, game_data.home_team, home_msg,
               a_emoji, game_data.away_team, away_msg, period_time_left, game_data.period_ord)
    return em

async def build_standing_embed(post_list, page=0):
    _teams = post_list[page]
    em = discord.Embed()
    if type(_teams) is not list:
        em.set_author(name="# {} {}".format(_teams.league_rank, _teams.name), url="https://www.nhl.com/standings", icon_url=teams[_teams.name]["logo"])
        em.colour = int(teams[_teams.name]["home"].replace("#", ""), 16)
        em.set_thumbnail(url=teams[_teams.name]["logo"])
        em.add_field(name="Division", value="# " + _teams.division_rank)
        em.add_field(name="Conference", value="# " + _teams.conference_rank)
        em.add_field(name="Wins", value=_teams.wins)
        em.add_field(name="Losses", value=_teams.losses)
        em.add_field(name="OT", value=_teams.ot)
        em.add_field(name="Points", value=_teams.pts)
        em.add_field(name="Games Played", value=_teams.gp)
        em.add_field(name="Goals Scored", value=_teams.goals)
        em.add_field(name="Goals Against", value=_teams.gaa)
        em.add_field(name="Current Streak", value="{} {}".format(_teams.streak, _teams.streak_type))
        timestamp = datetime.strptime(_teams.last_updated, "%Y-%m-%dT%H:%M:%SZ")
        em.timestamp = timestamp
        em.set_footer(text="Stats last Updated", icon_url=teams[_teams.name]["logo"])
        return em

    msg = ""
    timestamp = datetime.strptime(_teams[0].last_updated, "%Y-%m-%dT%H:%M:%SZ")
    em.timestamp = timestamp

    if len(_teams) <= 8:
        for team in _teams:
            msg += "{rank}. <:{emoji}> GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**\n"\
                    .format(rank=team.division_rank, wins=team.wins, losses=team.losses, ot=team.ot,\
                    pts=team.pts, gp=team.gp, emoji=teams[team.name]["emoji"])
        em.description = msg
        division = _teams[0].division
        division_logo = teams["Team {}".format(division)]["logo"]
        em.colour = int(teams["Team {}".format(division)]["home"].replace("#", ""), 16)
        em.set_author(name=division + " Division", url="https://www.nhl.com/standings", icon_url=division_logo)
        em.set_footer(text="Stats last Updated", icon_url=division_logo)
        em.set_thumbnail(url=division_logo)
        return em
    if len(_teams) > 8 and len(_teams) <= 15:
        new_teams = sorted(_teams, key=lambda k: int(k.conference_rank))
        for team in new_teams:
            msg += "{rank}. <:{emoji}> GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**\n"\
                    .format(rank=team.conference_rank, wins=team.wins, losses=team.losses, ot=team.ot,\
                    pts=team.pts, gp=team.gp, emoji=teams[team.name]["emoji"])
        em.description = msg
        conference = _teams[0].conference
        em.colour = int("c41230", 16) if conference == "Eastern" else int("003e7e", 16)
        logo = {"Eastern":"https://upload.wikimedia.org/wikipedia/en/thumb/1/16/NHL_Eastern_Conference.svg/1280px-NHL_Eastern_Conference.svg.png",
                "Western":"https://upload.wikimedia.org/wikipedia/en/thumb/6/65/NHL_Western_Conference.svg/1280px-NHL_Western_Conference.svg.png"}
        em.set_author(name=conference + " Conference", url="https://www.nhl.com/standings", icon_url=logo[conference])
        em.set_thumbnail(url=logo[conference])
        em.set_footer(text="Stats last Updated", icon_url=logo[conference])
        return em


async def all_standing_embed(post_standings, page=0):
    em = discord.Embed()
    new_dict = {}
    for team in post_standings:
        if team.division not in new_dict:
            new_dict[team.division] = ""
        new_dict[team.division] += "{rank}. <:{emoji}> GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**\n"\
                .format(rank=team.division_rank, wins=team.wins, losses=team.losses, ot=team.ot,\
                pts=team.pts, gp=team.gp, emoji=teams[team.name]["emoji"])
    for div in new_dict:
        em.add_field(name="{} Division".format(div), value=new_dict[div])
    em.set_author(name="NHL Standings", url="https://www.nhl.com/standings/2017/wildcard", icon_url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
    em.set_thumbnail(url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
    em.timestamp = datetime.strptime(post_standings[0].last_updated, "%Y-%m-%dT%H:%M:%SZ")
    em.set_footer(text="Stats Last Updated", icon_url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
    return em

async def roster_embed(post_list, page):
    player_list = post_list[page]
    headshots = "https://nhl.bamcontent.com/images/headshots/current/168x168/{}.jpg"
    url = "https://statsapi.web.nhl.com" + player_list["person"]["link"] + "?expand=person.stats&stats=yearByYear"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            player_data = await resp.json()
    player = player_data["people"][0]
    year_stats = [league for league in player["stats"][0]["splits"] if league["league"]["name"] == "National Hockey League"][-1]
    name = player["fullName"]
    number = player["primaryNumber"]
    position = player["primaryPosition"]["name"]
    headshot = headshots.format(player["id"])
    team = player["currentTeam"]["name"]
    em = discord.Embed(colour=int(teams[team]["home"].replace("#", ""), 16))
    em.set_author(name="{} #{}".format(name, number), url=teams[team]["team_url"], icon_url=teams[team]["logo"])
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
    return em

async def make_game_obj(url):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://statsapi.web.nhl.com" + url) as resp:
            game_data = await resp.json()
    data = await Game.from_json(game_data)
    return data


async def game_embed(post_list, page):
    game = post_list[page]
    
    if type(game) is dict:
        data = await make_game_obj(game["link"])
        print("https://statsapi.web.nhl.com" + game["link"])
    else:
        data = game
    team_url = teams[data.home_team]["team_url"] if data.home_team in teams else "https://nhl.com"
    timestamp = datetime.strptime(data.game_start, "%Y-%m-%dT%H:%M:%SZ")
    title = "{away} @ {home} {state}".format(away=data.away_team, home=data.home_team, state=data.game_state)
    colour = int(teams[data.home_team]["home"].replace("#", ""), 16) if data.home_team in teams else None

    em = discord.Embed(timestamp=timestamp)
    if colour is not None:
        em.colour = colour
    em.set_author(name=title, url=team_url, icon_url=data.home_logo)
    em.set_thumbnail(url=data.home_logo)
    em.set_footer(text="Game start ", icon_url=data.away_logo)
    if data.game_state == "Preview":
        home_str, away_str = await get_stats_msg(data)
        em.add_field(name="{} {} {}".format(data.home_emoji, data.home_team, data.home_emoji), value=home_str)
        em.add_field(name="{} {} {}".format(data.away_emoji, data.away_team, data.away_emoji), value=away_str)
    if data.game_state != "Preview":
        home_msg = "Goals: **{}** \nShots: **{}**".format(data.home_score, data.home_shots)
        away_msg = "Goals: **{}** \nShots: **{}**".format(data.away_score, data.away_shots)
        em.add_field(name="{} {} {}".format(data.home_emoji, data.home_team, data.home_emoji), value=home_msg)
        em.add_field(name="{} {} {}".format(data.away_emoji, data.away_team, data.away_emoji), value=away_msg)
        if data.goals != []:
            goal_msg = ""
            first_goals = [goal for goal in data.goals if goal["about"]["ordinalNum"] == "1st"]
            second_goals = [goal for goal in data.goals if goal["about"]["ordinalNum"] == "2nd"]
            third_goals = [goal for goal in data.goals if goal["about"]["ordinalNum"] == "3rd"]
            ot_goals = [goal for goal in data.goals if goal["about"]["ordinalNum"] == "OT"]
            so_goals = [goal for goal in data.goals if goal["about"]["ordinalNum"] == "SO"]
            list_goals = {"1st":first_goals, "2nd":second_goals, "3rd":third_goals, "OT":ot_goals, "SO":so_goals}
            for goals in list_goals:
                ordinal = goals
                goal_msg = ""
                for goal in list_goals[ordinal]:
                    team = goal["team"]["name"]
                    emoji = teams[team]["emoji"]
                    goal_msg += "<:{}>{} Goal By {}\n\n".format(emoji, team, goal["result"]["description"])
                if goal_msg != "":
                    em.add_field(name="{} Period Goals".format(ordinal), value=goal_msg)
        if data.game_state == "Live":
            try:
                em.description = data.plays[-1]["result"]["description"]
            except:
                pass
            period = data.period_ord
            if data.period_time_left[0].isdigit():
                msg = "{} Left in the {} period".format(data.period_time_left, period)
            else:
                msg = "{} of the {} period".format(data.period_time_left, period)
            em.add_field(name="Period", value=msg)
    return em

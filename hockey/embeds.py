import asyncio
import discord
import aiohttp
from datetime import datetime
from redbot.core.context import RedContext
from .teams import teams
        

async def division_standing_embed(post_list, page=0):
    em = discord.Embed()
    standing_list = post_list[page]
    conference = standing_list["conference"]["name"]
    division = standing_list["division"]["name"]
    for team in standing_list["teamRecords"]:
        team_name = team["team"]["name"]
        emoji = "<:" + teams[team_name]["emoji"] + ">"
        wins = team["leagueRecord"]["wins"]
        losses = team["leagueRecord"]["losses"]
        ot = team["leagueRecord"]["ot"]
        gp = team["gamesPlayed"]
        pts = team["points"]
        pl = team["divisionRank"]
        division_logo = teams["Team {}".format(division)]["logo"]
        msg = "GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**"\
              .format(pl=pl,emoji=emoji, wins=wins, losses=losses, ot=ot, pts=pts, gp=gp)
        timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
        em.add_field(name="{pl}. {emoji} __{team_name}__ {emoji}"\
                          .format(pl=pl,emoji=emoji,team_name=team_name), value=msg, inline=False)
        em.timestamp = timestamp
        em.set_footer(text="Stats last Updated", icon_url=division_logo)
        em.set_thumbnail(url=division_logo)
        em.colour = int(teams["Team {}".format(division)]["home"].replace("#", ""), 16)
        em.set_author(name=division + " Division", url="https://www.nhl.com/standings", icon_url=division_logo)
    return em

async def game_state_embed(data, state):
    post_state = ["all", data.home_team, data.away_team]
    timestamp = datetime.strptime(data.game_start, "%Y-%m-%dT%H:%M:%SZ")
    title = "{away} @ {home} {state}".format(away=data.away_team, home=data.home_team, state=data.game_state)
    colour = int(teams[data.home_team]["home"].replace("#", ""), 16)
    em = discord.Embed(timestamp=timestamp)
    home_field = "{} {} {}".format(data.home_emoji, data.home_team, data.home_emoji)
    away_field = "{} {} {}".format(data.away_emoji, data.away_team, data.away_emoji)
    if data.game_state != "Preview":
        home_str = "Goals: **{}** \nShots: **{}**".format(data.home_score, data.home_shots)
        away_str = "Goals: **{}** \nShots: **{}**".format(data.away_score, data.away_shots)
    else:
        home_str = "Home"
        away_str = "Away"
    em.add_field(name=home_field, value=home_str, inline=True)
    em.add_field(name=away_field, value=away_str, inline=True)
    team = state if state != "all" else data.home_team
    alt_team = [state for state in post_state if state != "all" and state != team][0]
    em.colour = int(teams[team]["home"].replace("#", ""), 16)
    logo = teams[team]["logo"]
    alt_logo = teams[alt_team]["logo"]
    team_url = teams[team]["team_url"]
    em.set_author(name=title, url=team_url, icon_url=logo)
    em.set_thumbnail(url=logo)
    em.set_footer(text="Game start ", icon_url=alt_logo)
    return em


async def get_shootout_display(goals):
    msg = ""
    score = "☑"
    miss = "❌"
    for goal in goals:
        if goal["result"]["eventTypeId"] in ["SHOT", "MISSED_SHOT"] and goal["about"]["ordinalNum"] == "SO":
            msg += miss
        else:
            msg += score
    return msg

async def goal_post_embed(goal, game_data):
    scoring_team = teams[goal["team"]["name"]]
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
    colour = int(teams[goal["team"]["name"]]["home"].replace("#", ""), 16)
    title = "🚨 {} {} {} 🚨".format(goal["team"]["name"], strength, event)
    url = teams[goal["team"]["name"]]["team_url"]
    logo = teams[goal["team"]["name"]]["logo"]
    if not shootout:
        
        em = discord.Embed(description=description, colour=colour)
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

async def conference_standing_embed(post_list, page=0):
    em = discord.Embed()
    standing_list = post_list[page]
    conference = "Eastern" if page == 0 else "Western"
    new_list = sorted(standing_list, key=lambda k: int(k["conferenceRank"]))
    for team in new_list:
        team_name = team["team"]["name"]
        emoji = "<:" + teams[team_name]["emoji"] + ">"
        wins = team["leagueRecord"]["wins"]
        losses = team["leagueRecord"]["losses"]
        ot = team["leagueRecord"]["ot"]
        gp = team["gamesPlayed"]
        pts = team["points"]
        pl = team["conferenceRank"]
        msg = "GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**"\
              .format(pl=pl,emoji=emoji, wins=wins, losses=losses, ot=ot, pts=pts, gp=gp)
        timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
        em.add_field(name="{pl}. {emoji} __{team_name}__ {emoji}".format(pl=pl,emoji=emoji,team_name=team_name), value=msg, inline=False)
        em.timestamp = timestamp
        em.set_footer(text="Stats last Updated")
    if conference == "Eastern":
        em.colour = int("c41230", 16)
        logo = "https://upload.wikimedia.org/wikipedia/en/thumb/1/16/NHL_Eastern_Conference.svg/1280px-NHL_Eastern_Conference.svg.png"
        em.set_author(name=conference + " Conference", url="https://www.nhl.com/standings", icon_url=logo)
        em.set_thumbnail(url=logo)
    if conference == "Western":
        em.colour = int("003e7e", 16)
        logo = "https://upload.wikimedia.org/wikipedia/en/thumb/6/65/NHL_Western_Conference.svg/1280px-NHL_Western_Conference.svg.png"
        em.set_author(name=conference + " Conference", url="https://www.nhl.com/standings", icon_url=logo)
        em.set_thumbnail(url=logo)
    return em

async def team_standing_embed(post_list, page=0):
    em = discord.Embed()
    standing_list = post_list[page]
    team = standing_list
    team_name = team["team"]["name"]
    league_rank = team["leagueRank"]
    division_rank = team["divisionRank"]
    conference_rank = team["conferenceRank"]
    emoji = "<:" + teams[team_name]["emoji"] + ">"
    wins = team["leagueRecord"]["wins"]
    losses = team["leagueRecord"]["losses"]
    ot = team["leagueRecord"]["ot"]
    gp = team["gamesPlayed"]
    pts = team["points"]
    streak = "{} {}".format(team["streak"]["streakNumber"], team["streak"]["streakType"])
    goals = team["goalsScored"]
    goals_against = team["goalsAgainst"]
    timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
    em.set_author(name="# {} {}".format(league_rank, team_name), url="https://www.nhl.com/standings", icon_url=teams[team_name]["logo"])
    em.colour = int(teams[team_name]["home"].replace("#", ""), 16)
    em.set_thumbnail(url=teams[team_name]["logo"])
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
    em.set_footer(text="Stats last Updated", icon_url=teams[team_name]["logo"])
    return em

async def all_standing_embed(post_standings, page=0):
    em = discord.Embed()
    em.set_author(name="NHL Standings", url="https://www.nhl.com/standings/2017/wildcard", icon_url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
    em.set_thumbnail(url="https://cdn.bleacherreport.net/images/team_logos/328x328/nhl.png")
    # standing_list = post_list[page]
    for division in post_standings:
        msg = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"  
        division_name = division["division"]["name"]
        for team in division["teamRecords"]:
            team_name = team["team"]["name"]
            emoji = "<:" + teams[team_name]["emoji"] + ">"
            wins = team["leagueRecord"]["wins"]
            losses = team["leagueRecord"]["losses"]
            ot = team["leagueRecord"]["ot"]
            gp = team["gamesPlayed"]
            pts = team["points"]
            pl = team["divisionRank"]
            # division_logo = teams["Team {}".format(division)]["logo"]
            msg += "{rank}. <:{team}> GP: **{gp}** W: **{wins}** L: **{losses}** OT: **{ot}** PTS: **{pts}**\n".format(pl=pl,emoji=emoji, wins=wins, losses=losses, ot=ot, pts=pts, gp=gp, rank=pl, team=teams[team_name]["emoji"])
            timestamp = datetime.strptime(team["lastUpdated"], "%Y-%m-%dT%H:%M:%SZ")
        msg += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        em.add_field(name=division_name, value=msg, inline=True)
        # em.add_field(name="▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    em.timestamp = timestamp
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

async def game_embed(post_list, page):
    game = post_list[page]
    print("https://statsapi.web.nhl.com" + game["link"])
    async with aiohttp.ClientSession() as session:
        async with session.get("https://statsapi.web.nhl.com" + game["link"]) as resp:
            game_data = await resp.json()
    home_team = game_data["liveData"]["linescore"]["teams"]["home"]["team"]["name"]
    home_shots = game_data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
    home_score = game_data["liveData"]["linescore"]["teams"]["home"]["goals"]
    away_team = game_data["liveData"]["linescore"]["teams"]["away"]["team"]["name"]
    away_shots = game_data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
    away_score = game_data["liveData"]["linescore"]["teams"]["away"]["goals"]
    home_logo = teams[home_team]["logo"]
    away_logo = teams[away_team]["logo"]
    team_url = teams[home_team]["team_url"]
    game_time = game["gameDate"]
    timestamp = datetime.strptime(game_time, "%Y-%m-%dT%H:%M:%SZ")
    game_state = game_data["gameData"]["status"]["abstractGameState"]
    h_emoji = "<:{}>".format(teams[home_team]["emoji"])
    a_emoji = "<:{}>".format(teams[away_team]["emoji"])
    title = "{away} @ {home} {state}".format(away=away_team, home=home_team, state=game_state)
    colour = int(teams[home_team]["home"].replace("#", ""), 16)
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
    return em

from redbot.core import commands
from .teams import teams
import asyncio
from datetime import datetime, timezone
import pytz
import aiohttp
from .standings import Standings

def get_season():
    now = datetime.now()
    if (now.month, now.day) < (7, 1):
        return (now.year - 1, now.year)
    if (now.month, now.day) >= (7, 1):
        return (now.year, now.year + 1)
        
async def get_team_role(guild, home_team, away_team):
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

async def get_team_standings(style):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://statsapi.web.nhl.com/api/v1/standings") as resp:
            data = await resp.json()
    conference = ["eastern", "western", "conference"]
    division = ["metropolitan", "atlantic", "pacific", "central", "division"]
    if style.lower() in conference:
        e = [await Standings.from_json(team, record["division"]["name"], record["conference"]["name"])\
                   for record in data["records"] for team in record["teamRecords"] \
                   if record["conference"]["name"] =="Eastern"]
        w = [await Standings.from_json(team, record["division"]["name"], record["conference"]["name"])\
                   for record in data["records"] for team in record["teamRecords"] \
                   if record["conference"]["name"] =="Western"]

        index = 0
        for div in [e, w]:
            print(div[0].conference)
            if div[0].conference.lower() == style and style != "conference":
                index = [e, w].index(div)
        return [e, w], index
    if style.lower() in division:
        new_list = []
        for record in data["records"]:
            new_list.append([await Standings.from_json(team, record["division"]["name"],\
            record["conference"]["name"]) for team in record["teamRecords"]])
        index = 0
        for div in new_list:
            if div[0].division.lower() == style and style != "division":
                index = new_list.index(div)
        return new_list, index
    else:
        all_teams =  [await Standings.from_json(team, record["division"]["name"], record["conference"]["name"])\
                      for record in data["records"] for team in record["teamRecords"]]
        index = 0
        for team in all_teams:
            if team.name.lower() == style:
                index = all_teams.index(team)
        return all_teams, index

async def pick_team(ctx, team_list):
    """
        helper to determine the team when two teams share a name when requested
        TODO: impliment everywhere teams are a choice
    """
    def msg_check(m):
        return m.author == ctx.message.author
    msg = "There's multiple teams with that name, pick one of these:\n"
    for i, team_name in enumerate(team_list):
        msg += "{}: {}\n".format(i, team_name)
    await ctx.send(msg)
    while msg is not None:
        try:
            msg = await ctx.bot.wait_for("message", check=msg_check, timeout=15)
        except asyncio.TimeoutError:
            await ctx.send("I guess not.")
            return None
        if msg.content.isdigit():
            msg = int(msg.content)
            try:
                return team_list[msg]
            except (IndexError, ValueError, AttributeError):
                pass
        else:
            return_team = None
            for team in team_list:
                if msg.content.lower() in team.lower():
                    return_team = team
            return return_team

async def check_valid_team(team_name, standings=False):
    """
        Checks if this is a valid team name or all teams
        useful for game day channel creation should impliment elsewhere
    """
    is_team = []
    conference = ["eastern", "western", "conference"]
    division = ["metropolitan", "atlantic", "pacific", "central", "division"]
    if team_name.lower() == "all":
        return ["all"]
    if team_name in conference and standings:
        return [team_name]
    if team_name.lower() in division and standings:
        return [team_name]
    for team in teams:
        if team_name.lower() in team.lower():
            is_team.append(team)
    return is_team

def utc_to_local(utc_dt):
    eastern = pytz.timezone('US/Eastern')
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=eastern)

async def get_chn_name(game):
    """
        Creates game day channel name
    """
    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    timestamp = utc_to_local(datetime.strptime(game.game_start, "%Y-%m-%dT%H:%M:%SZ"))
    chn_name = "{}-vs-{}-{}-{}-{}".format(game.home_abr, game.away_abr,\
                                          timestamp.year, timestamp.month, timestamp.day)
    return chn_name.lower()
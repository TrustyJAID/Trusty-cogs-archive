from discord.ext import commands
from .teams import teams
import asyncio
from datetime import datetime, timezone

        
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

async def check_valid_team(team_name):
    """
        Checks if this is a valid team name or all teams
        useful for game day channel creation should impliment elsewhere
    """
    is_team = []
    if team_name.lower() == "all":
        return ["all"]
    for team in teams:
        if team_name.lower() in team.lower():
            is_team.append(team)
    return is_team

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
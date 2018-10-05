import asyncio
import discord
import aiohttp
from redbot.core.commands import Context
from .embeds import *

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
async def hockey_menu(ctx:Context, display_type:str, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
    """menu control logic for this taken from
       https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
    if ctx.channel.permissions_for(ctx.guild.me).embed_links:
        if display_type == "standings":
            em = await build_standing_embed(post_list, page)
        if display_type == "division":
            em = await division_standing_embed(post_list, page)
        if display_type == "conference":
            em = await conference_standing_embed_test(post_list, page)
        if display_type == "teams":
            em = await team_standing_embed(post_list, page)
        if display_type == "all":
            em = await all_standing_embed(post_list, page)
        if display_type == "roster":
            em = await roster_embed(post_list, page)
        if display_type == "game":
            em = await game_embed(post_list, page)
        if display_type == "seasonal":
            leaderboard = {"type": "Seasonal", "lists": post_list}
            print(leaderboard)
            em = await make_leaderboard_embed(ctx.guild, leaderboard, page)
        if display_type == "weekly":
            leaderboard = {"type": "Weekly", "lists": post_list}
            em = await make_leaderboard_embed(ctx.guild, leaderboard, page)
    else:
        await ctx.send("I need embed_links permission to use this command.")
        return
    
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
        react, user = await ctx.bot.wait_for("reaction_add", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await message.remove_reaction("⬅", ctx.guild.me)
        await message.remove_reaction("❌", ctx.guild.me)
        await message.remove_reaction("➡", ctx.guild.me)
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
            return await hockey_menu(ctx, display_type, post_list, message=message,
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
            return await hockey_menu(ctx, display_type, post_list, message=message,
                                         page=next_page, timeout=timeout)
        else:
            return await message.delete()
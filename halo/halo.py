import discord
import aiohttp
from discord.ext import commands
from .utils.chat_formatting import pagify
from .utils.dataIO import dataIO
from .utils import checks
import os
from random import choice as randchoice

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}

class Halo():

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.settings = dataIO.load_json("data/halo/settings.json")
        self.api_token = self.settings["api_token"]

    async def request_url(self, url, params=None):
        async with self.session.get(url, params=params, headers=self.api_token) as resp:
            return await resp.json()

    @commands.group(pass_context=True, name='halo5')
    @checks.admin_or_permissions(manage_server=True)
    async def _halo5(self, ctx):
        """Get information from Halo 5"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @commands.group(pass_context=True, name='halowars')
    @checks.admin_or_permissions(manage_server=True)
    async def _halowars(self, ctx):
        """Get information from Halo Wars 2"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    def random_colour(self):
        return int(''.join([randchoice('0123456789ABCDEF')for x in range(6)]), 16)

    async def halo5_playlist_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        s = post_list[page]
        created_at = ctx.message.timestamp
        desc = "Created at: {}".format(created_at)
        em = discord.Embed(title=s["name"],
                           description=s["description"],
                           colour=discord.Colour(value=self.random_colour()),
                           timestamp=created_at)
        em.add_field(name="Gamemode", value=s["gameMode"])
        em.add_field(name="Ranked", value=str(s["isRanked"]))
        if s["imageUrl"] is not None:
            em.set_image(url=s["imageUrl"])
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
            return await self.halo5_playlist_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            return await self.halo5_playlist_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

    @_halo5.command(pass_context=True, name="playlist")
    async def halo5_playlist(self, ctx, active=True):
        """Gathers data about active Halo 5 playlists"""
        data = await self.request_url("https://www.haloapi.com/metadata/h5/metadata/playlists")
        list_active = []
        for playlist in data:
            if playlist["isActive"]:
                list_active.append(playlist)
        await self.halo5_playlist_menu(ctx, list_active)

    async def halowars_playlist_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        s = post_list[page]
        created_at = ctx.message.timestamp
        desc = "Created at: {}".format(created_at)
        em = discord.Embed(title=s["View"]["Title"],
                           # description=s["description"],
                           colour=discord.Colour(value=self.random_colour()),
                           timestamp=created_at)
        # em.add_field(name="Gamemode", value=s["gameMode"])
        # em.add_field(name="Ranked", value=str(s["isRanked"]))
        # if s["HW2Playlist"][] is not None:
        em.set_image(url=s["View"]["HW2Playlist"]["Image"]["View"]["Media"]["MediaUrl"])
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
            return await self.halowars_playlist_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            return await self.halowars_playlist_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

    async def get_halo5_rank_data(self, designation_id, tier_id):
        rank_data = await self.request_url("https://www.haloapi.com/metadata/h5/metadata/csr-designations")
        designation = [x for x in rank_data if x["id"] == str(designation_id)]
        image_url = [x["iconImageUrl"] for x in designation[0]["tiers"] if x["id"] == str(tier_id)]
        return designation[0]["name"], image_url

    @_halo5.command(pass_context=True, name="rank")
    async def Halo5_rank(self, ctx, *, gamertag):
        colours = {"Unranked": "7f7f7f", "Bronze": "c27c0e", "Silver": "cccccc", "Gold": "xf1c40f", 
                   "Platinum": "e5e5e5", "Diamond": "ffffff", "Onyx": "000000", "Champion": "71368a"}
        player_data = await self.request_url("https://www.haloapi.com/stats/h5/servicerecords/arena?", {"players":gamertag})
        tier = player_data["Results"][0]["Result"]["ArenaStats"]["HighestCsrAttained"]["Tier"]
        designation = player_data["Results"][0]["Result"]["ArenaStats"]["HighestCsrAttained"]["DesignationId"]
        designation_name, image_url = await self.get_halo5_rank_data(designation, tier)
        embed = discord.Embed(title=gamertag,
                              description=designation_name,
                              colour=discord.Colour(value=int(colours[designation_name], 16)),
                              timestamp=ctx.message.timestamp)
        embed.add_field(name="Designation", value=str(designation), inline=True)
        embed.add_field(name="Tier", value=str(tier), inline=True)
        embed.set_thumbnail(url=image_url[0])
        await self.bot.send_message(ctx.message.channel, embed=embed)
        


    @_halowars.command(pass_context=True, name="playlist")
    async def halowars_playlist(self, ctx, active=True):
        """Gathers data about active Halo 5 playlists"""
        data = await self.request_url("https://www.haloapi.com/metadata/hw2/playlists")
        list_active = []
        for playlist in data["ContentItems"]:
            # print(playlist)
            if not playlist["View"]["HW2Playlist"]["Hide"]:
                list_active.append(playlist)
        await self.halowars_playlist_menu(ctx, list_active)

    @commands.group(pass_context=True, name='haloset')
    @checks.admin_or_permissions(manage_server=True)
    async def _haloset(self, ctx):
        """Command for setting required access information for the API.
        To get this info, visit https://developer.haloapi.com and create a new application."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_haloset.command(pass_context=True)
    async def tokens(self, ctx, subscription_key, language="en"):
        """Set the tokens and language for requests from the API"""
        self.settings["api_token"]["Ocp-Apim-Subscription-Key"] = subscription_key
        self.settings["api_token"]["Accept-Language"] = language
        dataIO.save_json("data/halo/settings.json", self.settings)
        await self.bot.send_message(ctx.message.channel, "Halo API credentials set!")

def check_folder():
    if not os.path.exists("data/halo"):
        print("Creating data/halo folder")
        os.makedirs("data/halo")


def check_file():
    data = {"api_token":{"Ocp-Apim-Subscription-Key": "",
                "Accept-Language": "en"}}
    f = "data/halo/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Halo(bot))

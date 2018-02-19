import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
from redbot.core import checks
from redbot.core import Config
from random import choice as randchoice

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
class Anime:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = "https://anilist.co/api/"
        self.config = Config.get_conf(self, 15863754656)
        default_global = {"airing":{}, "api":{'client_id': '', 'client_secret': '', "access_token":""}}
        default_guild = {"enabled":False, "channel":None}
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        # self.airing = dataIO.load_json("data/anilist/airing.json")
        self.loop = bot.loop.create_task(self.check_airing_start())


    def __unload(self):
        self.session.close()
        self.loop.cancel()

    @commands.group()
    async def anime(self, ctx):
        """Various anime related commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    async def check_airing_start(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Anilist"):
            await self.check_last_posted()
            time_now = datetime.utcnow()
            for anime in self.airing:
                # print(anime["title_english"])
                if "episodes" not in anime:
                    continue
                if anime["adult"]:
                    continue
                for episode, time in anime["episodes"].items():
                    time_start = datetime.utcfromtimestamp(time)
                    # print(time_start.timestamp())
                    if time_start < time_now:
                        await self.post_anime_announcement(anime, episode, time_start)
            self.settings["last_check"] = time_now.timestamp()
            await self.remove_posted_shows()
            dataIO.save_json("data/anilist/settings.json", self.settings)
            await asyncio.sleep(60)
            # print("Checking anime")

    @anime.command(pass_context=True)
    async def airing(self, ctx):
        animes=""
        for anime in self.airing:
            animes += "{},".format(anime["title_english"])
        await self.bot.say(animes[:-2])

    async def remove_posted_shows(self):
        time_now = datetime.utcnow()
        to_delete = {}
        for anime in self.airing:
            if "episodes" not in anime:
                continue
            for episode, time in anime["episodes"].items():
                time_start = datetime.utcfromtimestamp(time)
                if time_start < time_now:
                    print("it gets here")
                    try:
                        to_delete[anime["id"]] = episode
                    except Exception as e:
                        print(e)
        for show_id, episode in to_delete.items():
            anime = [show for show in self.airing if show["id"] == show_id][0]
            del self.airing[self.airing.index(anime)]["episodes"][episode]
        dataIO.save_json("data/anilist/airing.json", self.airing)

    async def check_last_posted(self):
        last_time = datetime.utcfromtimestamp(self.settings["last_check"])
        time_now = datetime.utcnow()
        if last_time.day != last_time.day:
            await self.get_currently_airing()
        return

    async def post_anime_announcement(self, anime, episode, time_start):
        title = "{} | {}".format(anime["title_english"], anime["title_japanese"])
        url = "https://anilist.co/anime/{}/".format(anime["id"])
        # print(url)
        em = discord.Embed(colour=discord.Colour(value=self.random_colour()))
        desc = "Episode {} of {} starting!".format(episode, anime["title_english"])
        em.description = desc
        em.set_image(url=anime["image_url_lge"])
        em.set_author(name=title, url=url, icon_url=anime["image_url_sml"])
        em.set_footer(text="Start Date ")
        em.timestamp = time_start
        for server in list(self.settings):
            if server == "api" or server == "last_check" or server == "token":
                continue
            # print(server)
            channel_list = self.settings[server]["channel"]
            # print(channel_list)
            for channels in channel_list:
                channel = self.bot.get_channel(id=channels)
                await self.bot.send_message(channel, embed=em)
        return


    async def check_auth(self):
        time_now = datetime.utcnow()
        params = self.settings["api"]
        params["grant_type"] = "client_credentials"
        if "token" not in self.settings:
            async with self.session.post(self.url + "auth/access_token", params=params) as resp:
                data = await resp.json()
            print(data)
            self.settings["token"] = data
        if time_now > datetime.utcfromtimestamp(self.settings["token"]["expires"]):
            async with self.session.post(self.url + "auth/access_token", params=params) as resp:
                data = await resp.json()
            print("new token saved")
            self.settings["token"] = data
        dataIO.save_json("data/anilist/settings.json", self.settings)
        header = {"access_token": self.settings["token"]["access_token"]}
        return header

    def random_colour(self):
        return int(''.join([randchoice('0123456789ABCDEF')for x in range(6)]), 16)

    async def search_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        s = post_list[page]
        title = "{} | {}".format(s["title_english"], s["title_japanese"])
        url = "https://anilist.co/anime/{}/".format(s["id"])
        created_at = s["start_date"]
        created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S+09:00") # "2006-07-03T00:00:00+09:00"
        
        em = discord.Embed( colour=discord.Colour(value=self.random_colour()))
        if s["description"] is not None:
            desc = s["description"].replace("<br>", "\n")
            desc = desc.replace("<em>", "*")
            desc = desc.replace("</em>", "*")
            em.description = desc
        em.set_thumbnail(url=s["image_url_lge"])
        em.set_author(name=title, url=url, icon_url=s["image_url_sml"])
        em.set_footer(text="Start Date ")
        em.timestamp = created_at
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
            return await self.search_menu(ctx, post_list, message=message,
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
            return await self.search_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)



    @anime.command(pass_context=True)
    async def search(self, ctx, *, search):
        header = await self.check_auth()
        async with self.session.get(self.url + "anime/search/{}".format(search), params=header) as resp:
            print(str(resp.url))
            data = await resp.json()
        dataIO.save_json("data/anilist/sample.json", data)
        if "error" not in data:
            await self.search_menu(ctx, data)
        else:
            await self.bot.say("{} was not found or credentials were not set!".format(search))

    @commands.command(pass_context=True)
    async def forceairing(self, ctx):
        await self.get_currently_airing()
        await self.bot.say("Done.")

    async def get_currently_airing(self):
        header1 = await self.check_auth()
        header2 = header1
        header2["status"] = "Currently Airing"
        header2["full_page"] = "true"
        time_now = datetime.utcnow()
        anime_list = []
        async with self.session.get(self.url + "browse/anime", params=header2) as resp:
            # print(str(resp.url))
            data = await resp.json()
        for anime in data:
            if not anime["adult"]:
                print(anime["title_english"])
                episode_data = {}
                async with self.session.get(self.url + "anime/{}/airing".format(anime["id"]), params=header1) as resp:
                    ani_data = await resp.json()
                try:
                    for ep, time in ani_data.items():
                        if datetime.utcfromtimestamp(time) > time_now:
                            episode_data[ep] = time
                except Exception as e:
                    print("failed")
                    pass
            if episode_data != {}:
                data[data.index(anime)]["episodes"] = episode_data
            self.airing = data
        dataIO.save_json("data/anilist/airing.json", self.airing)

    @anime.command(hidden=True, pass_context=True)
    async def test(self, ctx, *, search=None):
        header1 = await self.check_auth()
        header2 = header1
        header2["status"] = "currently airing"
        header2["full_page"] = True
        time_now = datetime.utcnow()
        anime_list = []
        async with self.session.get(self.url + "browse/anime", params=header2) as resp:
            print(str(resp.url))
            data = await resp.json()
        for anime in data:
            if not anime["adult"]:
                episode_data = {}
                async with self.session.get(self.url + "anime/{}/airing".format(anime["id"]), params=header1) as resp:
                    ani_data = await resp.json()
                    # print(anime["title_english"])
                # anime_list.append(ani_data)
                # print(ani_data)
            # if episode_data != {}:
            data[data.index(anime)]["episodes"] = ani_data
        dataIO.save_json("data/anilist/sample.json", data)

    @commands.group(pass_context=True, name="animeset")
    @checks.admin_or_permissions(manage_channels=True)
    async def animeset(self, ctx):
        """Setup a channel for anime airing announcements"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    

    @animeset.command(pass_context=True, name="channel")
    async def add_channel(self, ctx, channel:discord.Channel=None):
        """Set the channel for anime announcements"""
        if channel is None:
            channel = ctx.message.channel
        server = channel.server
        if server.id not in self.settings:
            self.settings[server.id] = {"channel":[channel.id]}
        else:
            if channel.id in self.settings[server.id]["channel"]:
                await self.bot.say("I am already posting anime announcement updates in {}".format(channel.mention))
                return
            else:
                self.settings[server.id]["channel"].append(channel.id)
        dataIO.save_json("data/anilist/settings.json", self.settings)
        await self.bot.say("I will post anime episode announcements in {}".format(channel.mention))

    @animeset.command(pass_context=True, name="delete")
    async def del_channel(self, ctx, channel:discord.Channel=None):
        """Set the channel for anime announcements"""
        if channel is None:
            channel = ctx.message.channel
        server = channel.server
        if server.id not in self.settings:
            self.settings[server.id] = {"channel":[channel.id]}
        else:
            if channel.id not in self.settings[server.id]["channel"]:
                await self.bot.say("I am not posting anime announcement updates in {}".format(channel.mention))
                return
            else:
                self.settings[server.id]["channel"].remove(channel.id)
        dataIO.save_json("data/anilist/settings.json", self.settings)
        await self.bot.say("I will stop posting anime episode announcements in {}".format(channel.mention))


        

    @commands.group(pass_context=True, name='aniset')
    @checks.is_owner()
    async def _aniset(self, ctx):
        """Command for setting required access information for the API.
        To get this info, visit https://apps.twitter.com and create a new application.
        Once the application is created, click Keys and Access Tokens then find the
        button that says Create my access token and click that. Once that is done,
        use the subcommands of this command to set the access details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_aniset.command(name='creds')
    @checks.is_owner()
    async def set_creds(self, client_id:str, client_secret:str):
        """Sets the access credentials. See [p]help tweetset for instructions on getting these"""
        self.settings["api"]["client_id"] = client_id
        self.settings["api"]["client_secret"] = client_secret
        dataIO.save_json("data/anilist/settings.json", self.settings)
        await self.bot.say('Set the access credentials!')


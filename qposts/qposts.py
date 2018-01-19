import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from bs4 import BeautifulSoup

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
class QPosts:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.settings = dataIO.load_json("data/qposts/settings.json")
        self.qposts = dataIO.load_json("data/qposts/qposts.json")
        self.url = "https://8ch.net"
        self.boards = ["greatawakening", "qresearch"]
        self.loop = bot.loop.create_task(self.get_q_posts())

    def __unload(self):
        self.session.close()
        self.loop.cancel()

    @commands.command()
    async def dlq(self):
        for board in self.boards:
            async with self.session.get("{}/{}/catalog.json".format(self.url, board)) as resp:
                data = await resp.json()
            Q_posts = []
            for page in data:
                for thread in page["threads"]:
                    print(thread["no"])
                    async with self.session.get("{}/{}/res/{}.json".format(self.url, board,thread["no"])) as resp:
                        posts = await resp.json()
                    for post in posts["posts"]:
                        if "trip" in post:
                            if post["trip"] in ["!UW.yye1fxo", "!ITPb.qbhqo"]:
                                Q_posts.append(post)
            self.qposts[board] = Q_posts
        dataIO.save_json("data/qposts/qposts.json", self.qposts)

    @commands.command(pass_context=True, name="qrole")
    async def qrole(self, ctx):
        """Set your role to a team role"""
        server = ctx.message.server
        if server.id not in ["400317912616927234", "390196447657852929", "321105104931389440"]:
            return
        try:
            role = [role for role in server.roles if role.name == "QPOSTS"][0]
            await self.bot.add_roles(ctx.message.author, role)
            await self.bot.send_message(ctx.message.channel, "Role applied.")
        except:
            return

    async def get_q_posts(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("QPosts"):
            for board in self.boards:
                try:
                    async with self.session.get("{}/{}/catalog.json".format(self.url, board)) as resp:
                        data = await resp.json()
                except:
                    print("error grabbing board catalog {}".format(board))
                    continue
                Q_posts = []
                if board not in self.qposts:
                    self.qposts[board] = []
                for page in data:
                    for thread in page["threads"]:
                        # print(thread["no"])
                        try:
                            async with self.session.get("{}/{}/res/{}.json".format(self.url, board,thread["no"])) as resp:
                                posts = await resp.json()
                        except:
                            print("error grabbing thread {} in board {}".format(thread["no"], board))
                            continue
                        for post in posts["posts"]:
                            if "trip" in post:
                                if post["trip"] in ["!UW.yye1fxo"]:
                                    Q_posts.append(post)
                old_posts = [post_no["no"] for post_no in self.qposts[board]]

                for post in Q_posts:
                    if post["no"] not in old_posts:
                        self.qposts[board].append(post)
                        dataIO.save_json("data/qposts/qposts.json", self.qposts)
                        await self.postq(post, "/{}/".format(board))
                    for old_post in self.qposts[board]:
                        if old_post["no"] == post["no"] and old_post["com"] != post["com"]:
                            if "edit" not in self.qposts:
                                self.qposts["edit"] = {}
                            if board not in self.qposts["edit"]:
                                self.qposts["edit"][board] = []
                            self.qposts["edit"][board].append(old_post)
                            self.qposts[board].remove(old_post)
                            self.qposts[board].append(post)
                            dataIO.save_json("data/qposts/qposts.json", self.qposts)
                            await self.postq(post, "/{}/ {}".format(board, "EDIT"))
            print("checking Q...")
            asyncio.sleep(60)

    async def get_quoted_post(self, qpost):
        html = qpost["com"]
        soup = BeautifulSoup(html, "html.parser")
        reference_post = []
        for a in soup.find_all("a", href=True):
            print(a)
            url, post_id = a["href"].split("#")[0].replace("html", "json"), int(a["href"].split("#")[1])
            async with self.session.get(self.url + url) as resp:
                data = await resp.json()
            for post in data["posts"]:
                if post["no"] == post_id:
                    reference_post.append(post)
        return reference_post
            
    # @commands.command(pass_context=True)
    async def postq(self, qpost, board):
        # qpost = [post for post in self.qposts["thestorm"] if post["no"] == 11689][0]
        # print(qpost)
        # print("trying to post")
        em = discord.Embed(colour=discord.Colour.red())
        name = qpost["name"] if "name" in qpost else "Anonymous"
        url = "{}/{}/res/{}.html#{}".format(self.url, board, qpost["resto"], qpost["no"])
        em.set_author(name=name + qpost["trip"], url=url)
        em.timestamp = datetime.utcfromtimestamp(qpost["time"])
        html = qpost["com"]
        soup = BeautifulSoup(html, "html.parser")
        
        text = ""
        for p in soup.find_all("p"):
            if p.string is None:
                text += "."
            else:
                text += p.string + "\n"
        em.description = "```{}```".format(text[:1800])
        reference = await self.get_quoted_post(qpost)
        if reference != []:
            for post in reference:
                print(post)
                ref_html = post["com"]
                soup_ref = BeautifulSoup(ref_html, "html.parser")
                ref_text = ""
                for p in soup_ref.find_all("p"):
                    if p.string is None:
                        ref_text += "."
                    else:
                        ref_text += p.string + "\n"
                em.add_field(name=str(post["no"]), value="```{}```".format(ref_text))
        em.set_footer(text=board)
        if "tim" in qpost:
            file_id = qpost["tim"]
            file_ext = qpost["ext"]
            img_url = "https://media.8ch.net/file_store/{}{}".format(file_id, file_ext)
            if file_ext in [".png", ".jpg"]:
                em.set_image(url=img_url)
            await self.save_q_files(qpost)
        for channel_id in self.settings:
            channel = self.bot.get_channel(id=channel_id)
            server = channel.server
            try:
                role = [role for role in server.roles if role.name == "QPOSTS"][0]
                await self.bot.send_message(channel, "{} <{}>".format(role.mention, url), embed=em)
            except:
                await self.bot.send_message(channel, "<{}>".format(url), embed=em)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def fixq(self, ctx):
        async for message in self.bot.logs_from(ctx.message.channel, limit=1000):
            if message.embeds != []:
                embed = message.embeds[0]
                author = embed["author"]["name"]
                board = embed["footer"]["text"]
                url = embed["author"]["url"].replace("/thestorm/", board)
                embed["author"]["url"] = url
                text = embed["description"]
                # timestamp = embed["timestamp"] "2018-01-13T22:39:31+00:00"
                # print(board)
                post_id = int(url.split("#")[-1])
                timestamp = [post["time"] for post in self.qposts[board.replace("/", "")] if post["no"] == post_id][0]
                qpost = [post for post in self.qposts[board.replace("/", "")] if post["no"] == post_id][0]
                # print(timestamp)
                timestamp = datetime.utcfromtimestamp(timestamp)
                # print(timestamp)
                em = discord.Embed(colour=discord.Colour.red(),
                                   description="{}".format(text),
                                   timestamp=timestamp)
                em.set_author(name=author, url=url)
                em.set_footer(text="{}".format(board))
                if "tim" in qpost:
                    file_id = qpost["tim"]
                    file_ext = qpost["ext"]
                    img_url = "https://media.8ch.net/file_store/{}{}".format(file_id, file_ext)
                    if file_ext in [".png", ".jpg"]:
                        em.set_image(url=img_url)
                await self.bot.edit_message(message, embed=em)
        # print(embed["author"])

    async def q_menu(self, ctx, post_list: list, board,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""

        qpost = post_list[page]
        em = discord.Embed(colour=discord.Colour.red())
        name = qpost["name"] if "name" in qpost else "Anonymous"
        url = "{}/{}/res/{}.html#{}".format(self.url, board, qpost["resto"], qpost["no"])
        em.set_author(name=name + qpost["trip"], url=url)
        em.timestamp = datetime.utcfromtimestamp(qpost["time"])
        html = qpost["com"]
        soup = BeautifulSoup(html, "html.parser")
        text = ""
        for p in soup.find_all("p"):
            if p.string is None:
                text += "."
            else:
                text += p.string + "\n"
        em.description = "```{}```".format(text[:1800])
        reference = await self.get_quoted_post(qpost)
        if reference != []:
            for post in reference:
                print(post)
                ref_html = post["com"]
                soup_ref = BeautifulSoup(ref_html, "html.parser")
                ref_text = ""
                for p in soup_ref.find_all("p"):
                    if p.string is None:
                        ref_text += "."
                    else:
                        ref_text += p.string + "\n"
                em.add_field(name=str(post["no"]), value=ref_text)
        em.set_footer(text="/{}/".format(board))
        if "tim" in qpost:
            file_id = qpost["tim"]
            file_ext = qpost["ext"]
            img_url = "https://media.8ch.net/file_store/{}{}".format(file_id, file_ext)
            if file_ext in [".png", ".jpg"]:
                em.set_image(url=img_url)
        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, "<{}>".format(url), embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, "<{}>".format(url), embed=em)
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
            return await self.q_menu(ctx, post_list, board=board,
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
            return await self.q_menu(ctx, post_list, board=board,
                                        message=message,
                                        page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

    @commands.command(pass_context=True, aliases=["postq"])
    async def qpost(self, ctx, board="greatawakening"):
        if board not in self.qposts:
            await self.bot.send_message(ctx.message.channel, "{} is not an available board!")
            return
        qposts = list(reversed(self.qposts[board]))
        await self.q_menu(ctx, qposts, board)

    async def save_q_files(self, post):
        file_id = post["tim"]
        file_ext = post["ext"]
        url = "https://media.8ch.net/file_store/{}{}".format(file_id, file_ext)
        async with self.session.get(url) as resp:
            image = await resp.read()
        with open("data/qposts/files/{}{}".format(file_id, file_ext), "wb") as out:
            out.write(image)
        if "extra_files" in post:
            for file in post["extra_files"]:
                file_id = file["tim"]
                file_ext = file["ext"]
                url = "https://media.8ch.net/file_store/{}{}".format(file_id, file_ext)
                async with self.session.get(url) as resp:
                    image = await resp.read()
                with open("data/qposts/files/{}{}".format(file_id, file_ext), "wb") as out:
                    out.write(image)

    @commands.command(pass_context=True)
    async def qchannel(self, ctx, channel:discord.Channel=None):
        if channel is None:
            channel = ctx.message.channel
        server = ctx.message.server
        if self.settings == {}:
            self.settings = []
        self.settings.append(channel.id)
        dataIO.save_json("data/qposts/settings.json", self.settings)
        await self.bot.say("{} set for qposts!".format(channel.mention))


def check_folder():
    if not os.path.exists("data/qposts"):
        print("Creating data/qposts folder")
        os.makedirs("data/qposts")
    if not os.path.exists("data/qposts/files"):
        print("Creating data/qposts/files folder")
        os.makedirs("data/qposts/files")

def check_file():
    data = {}
    settings = []
    f = "data/qposts/settings.json"
    q = "data/qposts/qposts.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, settings)
    if not dataIO.is_valid_json(q):
        print("Creating default settings.json...")
        dataIO.save_json(q, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(QPosts(bot))

import discord
import asyncio
import aiohttp
from discord.ext import commands
from redbot.core import checks, Config
from datetime import datetime
import logging


class Unity4J:

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 458467658435)
        default_global = {"last_sent":0}
        self.config.register_global(**default_global)
        self.loop = bot.loop.create_task(self.message_need_a_role())

    async def get_role(self, guild, role_id):
        need_a_role = None
        for role in guild.roles:
            if role.id == role_id:
                need_a_role = role
        return need_a_role


    async def message_need_a_role(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Unity4J"):
            last_checked = datetime.utcfromtimestamp(await self.config.last_sent())
            now = datetime.utcnow()
            if last_checked.day != now.day:
                guild = self.bot.get_guild(469771424274317312)
                role = await self.get_role(guild, 470518033840865290)# get the need_a_role role object
                for member in role.members:
                    try:
                        await member.send("Hey there. You have no role assigned yet and we want to help you settle into your #Unity4J team as soon as possible. Please go to #role, read through the role descriptions and answer the questions, and to <#469816208464805896> or <#470402195477626910> if you need any help. Thank you!")
                    except Exception as e:
                        print(e)
                await self.config.last_checked.set(now.timestamp())
            await asyncio.sleep(600)


    async def on_member_update(self, before, after):
        guild = before.guild
        if guild.id != 469771424274317312:
            return
        before_role_id = [role.id for role in before.roles]
        after_role_id = [role.id for role in after.roles]
        if 470458449839259649 in after_role_id and 470458449839259649 not in before_role_id:
            try:
                await after.send("Congratulations {}, you have earned the 'Helpful' role for being kind and helpful to your fellow members of the movement! Thank you for being such a wonderful human being and helping to save Julian!".format(after.mention))
            except Exception as e:
                print(e)
        if 470898257774641153 in after_role_id and 470898257774641153 not in before_role_id:
            try:
                await after.send("Congratulations {}, you have earned the 'Contributing' role for contributing to work being utilised by the movement! Thank you for your efforts to help save Julian!".format(after.mention))
            except Exception as e:
                print(e)
        
    async def on_message(self, message):
        if message.channel.id == 469783041145962496 or message.channel.id == 469771424773701649:
            if "donate" in message.content.lower() and not message.author.bot:
                await message.channel.send("Would you like to donate to support Julian? Please do so at https://iamwikileaks.org/donate and https://justice4assange.com. Thank you so much for supporting him!")
                return
        


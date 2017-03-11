from random import choice as randchoice
from datetime import datetime as dt
from discord.ext import commands
import discord
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from .utils import checks
try:
    import tweepy as tw
    twInstalled = True
except:
    twInstalled = False
import os
import asyncio


class AutoTweets():
    """Cog for displaying info from Twitter's API"""
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/autotweet/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        settings = self.settings["api"]
        if 'consumer_key' in list(settings.keys()):
            self.consumer_key = settings['consumer_key']
        if 'consumer_secret' in list(settings.keys()):
            self.consumer_secret = settings['consumer_secret']
        if 'access_token' in list(settings.keys()):
            self.access_token = settings['access_token']
        if 'access_secret' in list(settings.keys()):
            self.access_secret = settings['access_secret']

    def authenticate(self):
        """Authenticate with Twitter's API"""
        auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        return tw.API(auth)

    @commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def addautotweet(self, ctx, account, channel=None):
        if account in self.settings["accounts"]:
            accountlist = self.settings["accounts"][account]
        else:
            self.settings["accounts"][account] = []
            accountlist = self.settings["accounts"][account]
        channelname = self.bot.get_channel(channel)

        if channel is None:
            channel = ctx.message.channel.id
        if "<#" in channel:
            channel = channel.strip("<#>")

        if channel in accountlist:
            await self.bot.say("I am already posting in <#{}>".format(channel))
            return
        accountlist.append(channel)
        await self.bot.say("{0} Added to <#{1}>!".format(account, channel))
        dataIO.save_json(self.settings_file, self.settings)


    @commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def delautotweet(self, ctx, account, channel=None):
        try:
            accountlist = self.settings["accounts"][account]
        except KeyError:
            await self.bot.say("{} is not in my list of accounts!"
                               .format(account))
            return

        channelname = self.bot.get_channel(channel)
        if channel is None:
            channel = ctx.message.channel.id
        if "<#" in channel:
            channel = channel.strip("<#>")

        if channel in accountlist:
            if len(accountlist) < 2:
                self.settings["accounts"].pop(account, None)
            else:
                accountlist.remove(channel)
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("{0} removed from <#{1}>!"
                               .format(account, channel))
        else:
            await self.bot.say("{0} doesn't seem to be posting in <#{1}>!"
                               .format(account, channel))

    async def gettweet(self, username: str):
        """Gets the specified number of tweets for the specified username"""
        api = self.authenticate()
        msg = ""
        lasttweet = self.settings["lasttweet"]
        try:
            for status in tw.Cursor(api.user_timeline, id=username).items(1):
                msg = status
        except tw.TweepError as e:
            await self.bot.say("Whoops! Something went wrong here. \
                The error code is " + str(e))
            return
        try:
            if lasttweet[username] == str(msg.id):
                return
        except KeyError:
            pass

        lasttweet[username] = str(msg.id)
        lasttweet = dataIO.save_json(self.settings_file, self.settings)
        post_url = "https://twitter.com/{}/status/{}".format(msg.user.screen_name, msg.id)
        created_at = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        desc = "{}".format(created_at)
        em = discord.Embed(title="Tweet by {}".format(msg.user.name),
                           colour=discord.Colour.gold(),
                           url=post_url)
        em.add_field(name=desc, value=msg.text)
        for channel in self.settings["accounts"][username]:
            await self.bot.send_message(self.bot.get_channel(channel), embed=em)

    async def post_tweets(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            for key in self.settings["accounts"].keys():
                try:
                    await self.gettweet(key)
                except:
                    await self.bot.say("Something must be wrong with that username!")
            await asyncio.sleep(60)

    @commands.group(pass_context=True, name='autotweetset')
    @checks.admin_or_permissions(manage_server=True)
    async def _autotweetset(self, ctx):
        """Command for setting required access information for the API"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_autotweetset.command(pass_context=True, name='consumerkey')
    @checks.is_owner()
    async def set_consumer_key(self, ctx, cons_key):
        """Sets the consumer key"""
        message = ""
        if cons_key is not None:
            settings = self.settings["api"]
            settings["consumer_key"] = cons_key
            settings = dataIO.save_json(self.settings_file, self.settings)
            message = "Consumer key saved!"
        else:
            message = "No consumer key provided!"
        await self.bot.say('```{}```'.format(message))

    @_autotweetset.command(pass_context=True, name='consumersecret')
    @checks.is_owner()
    async def set_consumer_secret(self, ctx, cons_secret):
        """Sets the consumer secret"""
        message = ""
        if cons_secret is not None:
            settings = self.settings["api"]
            settings["consumer_secret"] = cons_secret
            settings = dataIO.save_json(self.settings_file, self.settings)
            message = "Consumer secret saved!"
        else:
            message = "No consumer secret provided!"
        await self.bot.say('```{}```'.format(message))

    @_autotweetset.command(pass_context=True, name='accesstoken')
    @checks.is_owner()
    async def set_access_token(self, ctx, token):
        """Sets the access token"""
        message = ""
        if token is not None:
            settings = self.settings["api"]
            settings["access_token"] = token
            settings = dataIO.save_json(self.settings_file, self.settings)
            message = "Access token saved!"
        else:
            message = "No access token provided!"
        await self.bot.say('```{}```'.format(message))

    @_autotweetset.command(pass_context=True, name='accesssecret')
    @checks.is_owner()
    async def set_access_secret(self, ctx, secret):
        """Sets the access secret"""
        message = ""
        if secret is not None:
            settings = self.settings["api"]
            settings["access_secret"] = secret
            settings = dataIO.save_json(self.settings_file, self.settings)
            message = "Access secret saved!"
        else:
            message = "No access secret provided!"
        await self.bot.say('```{}```'.format(message))


def check_folder():
    if not os.path.exists("data/autotweet"):
        print("Creating data/aotuotweet folder")
        os.makedirs("data/autotweet")


def check_file():
    data = {"api": {'consumer_key': '', 'consumer_secret': '',
            'access_token': '', 'access_secret': ''}, "lasttweet": {}, "accounts": {}}
    f = "data/autotweet/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    if twInstalled:
        n = AutoTweets(bot)
        bot.loop.create_task(n.post_tweets())
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to do 'pip3 install tweepy'")

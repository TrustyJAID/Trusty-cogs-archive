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
import time


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
    
    @commands.group(pass_context=True, name='autotweet')
    @checks.admin_or_permissions(manage_channels=True)
    async def _autotweet(self, ctx):
        """Command for setting accounts and channels for posting"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
    
    @_autotweet.command(pass_context=True, name="replies")
    async def _replies(self, ctx, account, replies):
        account = account.lower()
        if account not in self.settings["accounts"]:
            await self.bot.say("{} is not posting anywhere!".format(account))
            return
        if replies.lower() == "true":
            self.settings["accounts"][account]["replies"] = True
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("I will post replies for {} now!".format(account))
        if replies.lower() == "false":
            self.settings["accounts"][account]["replies"] = False
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("I will stop posting replies for {} now!".format(account))

    @_autotweet.command(pass_context=True, name="add")
    async def _add(self, ctx, account, channel:discord.Channel=None):
        """Adds a twitter account to the specified channel"""
        account = account.lower()
        if account in self.settings["accounts"]:
            try:
                accountlist = self.settings["accounts"][account]["channel"]
            except TypeError:
                self.settings["accounts"][account] = {"channel" : [], "lasttweet": "", "replies": False}
                accountlist = self.settings["accounts"][account]
        else:
            self.settings["accounts"][account] = {"channel" : [], "lasttweet": "", "replies": False}
            accountlist = self.settings["accounts"][account]["channel"]
            api = self.authenticate()
            lasttweet = self.settings["accounts"][account]["lasttweet"]
            for status in tw.Cursor(api.user_timeline, id=account).items(1):
                lasttweet = status.id
            dataIO.save_json(self.settings_file, self.settings)

        if channel is None:
            channel = ctx.message.channel

        if channel.id in accountlist:
            await self.bot.say("I am already posting in {}".format(channel.mention))
            return
        accountlist.append(channel.id)
        await self.bot.say("{0} Added to {1}!".format(account, channel.mention))
        dataIO.save_json(self.settings_file, self.settings)


    @_autotweet.command(pass_context=True, name="del", aliases=["delete", "rem", "remove"])
    async def _del(self, ctx, account, channel:discord.Channel=None):
        """Removes a twitter account to the specified channel"""
        account = account.lower()
        try:
            accountlist = self.settings["accounts"][account]["channel"]
        except KeyError:
            await self.bot.say("{} is not in my list of accounts!".format(account))
            return

        if channel is None:
            channel = ctx.message.channel

        if channel.id in accountlist:
            if len(accountlist) < 2:
                del self.settings["accounts"][account]
            else:
                accountlist.remove(channel.id)
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("{0} removed from {1}!"
                               .format(account, channel.mention))
        else:
            await self.bot.say("{0} doesn't seem to be posting in {1}!"
                               .format(account, channel.mention))

    async def get_tweet(self, api, username: str):
        """Posts the tweets to the channel"""
        lasttweet = self.settings["accounts"][username]["lasttweet"]
        if lasttweet is "":
            for status in tw.Cursor(api.user_timeline, id=username).items(1):
                self.settings["accounts"][username]["lasttweet"] = status.id
            lasttweet = dataIO.save_json(self.settings_file, self.settings)
        try:
            for status in tw.Cursor(api.user_timeline, id=username, 
                                    since_id=self.settings["accounts"][username]["lasttweet"]).items(1):
                if hasattr(status, "in_reply_to_screen_name") and not self.settings["accounts"][username]["replies"]:
                    return
                post_url = "https://twitter.com/{}/status/{}".format(status.user.screen_name, status.id)
                created_at = status.created_at.strftime("%Y-%m-%d %H:%M:%S")
                desc = "{}".format(created_at)
                colour =''.join([randchoice('0123456789ABCDEF')for x in range(6)])
                colour = int(colour, 16)
                em = discord.Embed(description=status.text,
                                colour=discord.Colour(value=colour),
                                url=post_url,
                                timestamp=status.created_at)
                try:                                
                    em.set_author(name=status.user.name, icon_url=status.user.profile_image_url)
                except:
                    print(status.user.name + " could not get profile image!")
                if hasattr(status, "extended_entities"):
                    em.set_image(url=status.extended_entities["media"][0]["media_url"])
                for channel in list(self.settings["accounts"][username]["channel"]):
                    await self.bot.send_message(self.bot.get_channel(channel), embed=em)
                    await asyncio.sleep(1)
                self.settings["accounts"][username]["lasttweet"] = status.id
            dataIO.save_json(self.settings_file, self.settings)
        except tw.TweepError as e:
            print("Whoops! Something went wrong here. \
                The error code is " + str(e) + username)
            return

    async def post_tweets(self):
        while self is self.bot.get_cog("AutoTweets"):
            api = self.authenticate()
            for key in list(self.settings["accounts"]):
                await self.get_tweet(api, key)
                await asyncio.sleep(1)
            await asyncio.sleep(120)

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
            'access_token': '', 'access_secret': ''}, "accounts": {}}
    f = "data/autotweet/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    if twInstalled:
        n = AutoTweets(bot)
        loop = asyncio.get_event_loop()
        loop.create_task(n.post_tweets())
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to do 'pip3 install tweepy'")

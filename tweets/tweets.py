from random import choice as randchoice
from datetime import datetime as dt
from discord.ext import commands
import discord
import asyncio
from .utils.dataIO import dataIO
from .utils import checks
try:
    import tweepy as tw
    twInstalled = True
except:
    twInstalled = False
import os


numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}


class TweetListener(tw.StreamListener):
    
    def __init__(self, api, bot):
        self.bot = bot
        self.api = api
    
    def on_status(self, status):
        # print(status.text)
        self.bot.dispatch("tweet_status", status)
        if self.bot.is_closed:
            return False
        else:
            return True

    def on_error(self, status_code):
        if status_code == 420:
            return False


class Tweets():
    """Cog for displaying info from Twitter's API"""
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/tweets/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        if 'consumer_key' in list(self.settings["api"].keys()):
            self.consumer_key = self.settings["api"]['consumer_key']
        if 'consumer_secret' in list(self.settings["api"].keys()):
            self.consumer_secret = self.settings["api"]['consumer_secret']
        if 'access_token' in list(self.settings["api"].keys()):
            self.access_token = self.settings["api"]['access_token']
        if 'access_secret' in list(self.settings["api"].keys()):
            self.access_secret = self.settings["api"]['access_secret']
        auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5, retry_errors=5)
        tweet_list = list(self.settings["accounts"])
        stream_start = TweetListener(api, self.bot)
        mystream = tw.Stream(auth, stream_start)
    
        mystream.filter(follow=tweet_list, async=True)

    async def authenticate(self):
        """Authenticate with Twitter's API"""
        auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        return tw.API(auth)

    async def tweet_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        s = post_list[page]
        colour =\
            ''.join([randchoice('0123456789ABCDEF')
                     for x in range(6)])
        colour = int(colour, 16)
        created_at = s.created_at
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
        post_url =\
            "https://twitter.com/{}/status/{}".format(s.user.screen_name, s.id)
        desc = "Created at: {}".format(created_at)
        em = discord.Embed(description=s.text,
                           colour=discord.Colour(value=colour),
                           url=post_url,
                           timestamp=s.created_at)
        try:                                
            em.set_author(name=s.user.name, icon_url=s.user.profile_image_url)
        except:
            print(s.user.name + " could not get profile image!")
        # em.add_field(name="Text", value=s.text)
        em.set_footer(text="Retweet count: " + str(s.retweet_count))
        if hasattr(s, "extended_entities"):
            em.set_image(url=s.extended_entities["media"][0]["media_url"] + ":thumb")
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
            return await self.tweet_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            return await self.tweet_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

    @commands.group(pass_context=True, no_pm=True, name='tweets')
    async def _tweets(self, ctx):
        """Gets various information from Twitter's API"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_tweets.command(pass_context=True, no_pm=True, name='getuser')
    async def get_user(self, ctx, username: str):
        """Get info about the specified user"""
        message = ""
        if username is not None:
            api = await self.authenticate()
            user = api.get_user(username)

            colour =\
                ''.join([randchoice('0123456789ABCDEF')
                     for x in range(6)])
            colour = int(colour, 16)
            url = "https://twitter.com/" + user.screen_name
            emb = discord.Embed(title=user.name,
                                colour=discord.Colour(value=colour),
                                url=url,
                                description=user.description)
            emb.set_thumbnail(url=user.profile_image_url)
            emb.add_field(name="Followers", value=user.followers_count)
            emb.add_field(name="Friends", value=user.friends_count)
            if user.verified:
                emb.add_field(name="Verified", value="Yes")
            else:
                emb.add_field(name="Verified", value="No")
            footer = "Created at " + user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            emb.set_footer(text=footer)
            await self.bot.send_message(ctx.message.channel, embed=emb)
        else:
            message = "Uh oh, an error occurred somewhere!"
            await self.bot.say(message)

    @_tweets.command(pass_context=True, no_pm=True, name='gettweets')
    async def get_tweets(self, ctx, username: str, count: int):
        """Gets the specified number of tweets for the specified username"""
        cnt = count
        if count > 25:
            cnt = 25
        if username not in self.settings["accounts"]:
            replies_on = False
        else:
            replies_on = self.settings["accounts"][username]["replies"]

        if username is not None:
            if cnt < 1:
                await self.bot.say("I can't do that, silly! Please specify a \
                    number greater than or equal to 1")
                return
            msg_list = []
            api = await self.authenticate()
            try:
                for status in\
                        tw.Cursor(api.user_timeline, id=username).items(cnt):
                    if status.in_reply_to_screen_name is not None and not replies_on:
                        continue
                    msg_list.append(status)
            except tw.TweepError as e:
                await self.bot.say("Whoops! Something went wrong here. \
                    The error code is " + str(e))
                return
            if len(msg_list) > 0:
                await self.tweet_menu(ctx, msg_list, page=0, timeout=30)
            else:
                await self.bot.say("No tweets available to display!")
        else:
            await self.bot.say("No username specified!")
            return
    
    async def on_tweet_status(self, status):
        """Posts the tweets to the channel"""
        # await self.bot.send_message(self.bot.get_channel("321105104931389440"), status.text)
        username = status.user.screen_name
        user_id = str(status.user.id)
        if user_id not in self.settings["accounts"]:
            return
        lasttweet = self.settings["accounts"][user_id]["lasttweet"]
        if lasttweet is "":
            for status in tw.Cursor(api.user_timeline, id=username).items(1):
                self.settings["accounts"][user_id]["lasttweet"] = status.id
            lasttweet = dataIO.save_json(self.settings_file, self.settings)
        try:
            if status.in_reply_to_screen_name is not None and not self.settings["accounts"][user_id]["replies"]:
                return
            post_url = "https://twitter.com/{}/status/{}".format(status.user.screen_name, status.id)
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
            for channel in list(self.settings["accounts"][user_id]["channel"]):
                await self.bot.send_message(self.bot.get_channel(channel), embed=em)
                # await asyncio.sleep(1)
            self.settings["accounts"][user_id]["lasttweet"] = status.id
            dataIO.save_json(self.settings_file, self.settings)
        except tw.TweepError as e:
            print("Whoops! Something went wrong here. \
                The error code is " + str(e) + username)
            return
    
    @commands.group(pass_context=True, name='autotweet')
    @checks.admin_or_permissions(manage_channels=True)
    async def _autotweet(self, ctx):
        """Command for setting accounts and channels for posting"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
    
    @_autotweet.command(pass_context=True, name="replies")
    async def _replies(self, ctx, account, replies):
        account = account.lower()
        for user_id in list(self.settings["accounts"]):
            if account == self.settings["accounts"][user_id]["username"].lower():
                channel_list = self.settings["accounts"][user_id]["channel"]
                user = user_id
        if channel_list is None:
            await self.bot.say("{} is not in my list of accounts!".format(account))
            return
        if replies.lower() in ["true", "on"]:
            self.settings["accounts"][user]["replies"] = True
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("I will post replies for {} now!".format(account))
        if replies.lower() in ["false", "off"]:
            self.settings["accounts"][user]["replies"] = False
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("I will stop posting replies for {} now!".format(account))

    @_autotweet.command(pass_context=True, name="add")
    async def _add(self, ctx, account, channel:discord.Channel=None):
        """Adds a twitter account to the specified channel"""
        api = await self.authenticate()
        try:
            for status in tw.Cursor(api.user_timeline, id=account).items(1):
                user_id = str(status.user.id)
                screen_name = status.user.screen_name
                last_id = status.id
                self.settings["accounts"][user_id] = {"channel" : [], 
                                                      "lasttweet": last_id, 
                                                      "replies": False,
                                                      "username": screen_name}
        except tw.TweepError as e:
            print("Whoops! Something went wrong here. \
                    The error code is " + str(e) + account)
            await self.bot.say("That account does not exist! Try again")
            return
        channel_list = self.settings["accounts"][user_id]["channel"]
        if channel is None:
            channel = ctx.message.channel

        if channel.id in channel_list:
            await self.bot.say("I am already posting in {}".format(channel.mention))
            return
        channel_list.append(channel.id)
        await self.bot.say("{0} Added to {1}!".format(account, channel.mention))
        dataIO.save_json(self.settings_file, self.settings)


    @_autotweet.command(pass_context=True, name="del", aliases=["delete", "rem", "remove"])
    async def _del(self, ctx, account, channel:discord.Channel=None):
        """Removes a twitter account to the specified channel"""
        account = account.lower()
        for user_id in list(self.settings["accounts"]):
            if account == self.settings["accounts"][user_id]["username"].lower():
                channel_list = self.settings["accounts"][user_id]["channel"]
                user = user_id
        if channel_list is None:
            await self.bot.say("{} is not in my list of accounts!".format(account))
            return

        if channel is None:
            channel = ctx.message.channel

        if channel.id in channel_list:
            if len(channel_list) < 2:
                del self.settings["accounts"][user]
            else:
                channel_list.remove(channel.id)
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("{0} removed from {1}!"
                               .format(account, channel.mention))
        else:
            await self.bot.say("{0} doesn't seem to be posting in {1}!"
                               .format(account, channel.mention))


    @commands.group(pass_context=True, name='tweetset')
    @checks.admin_or_permissions(manage_server=True)
    async def _tweetset(self, ctx):
        """Command for setting required access information for the API.
        To get this info, visit https://apps.twitter.com and create a new application.
        Once the application is created, click Keys and Access Tokens then find the
        button that says Create my access token and click that. Once that is done,
        use the subcommands of this command to set the access details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_tweetset.command(name='creds')
    @checks.is_owner()
    async def set_creds(self, consumer_key: str, consumer_secret: str, access_token: str, access_secret: str):
        """Sets the access credentials. See [p]help tweetset for instructions on getting these"""
        if consumer_key is not None:
            self.settings["api"]["consumer_key"] = consumer_key
        else:
            await self.bot.say("No consumer key provided!")
            return
        if consumer_secret is not None:
            self.settings["api"]["consumer_secret"] = consumer_secret
        else:
            await self.bot.say("No consumer secret provided!")
            return
        if access_token is not None:
            self.settings["api"]["access_token"] = access_token
        else:
            await self.bot.say("No access token provided!")
            return
        if access_secret is not None:
            self.settings["api"]["access_secret"] = access_secret
        else:
            await self.bot.say("No access secret provided!")
            return
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.say('Set the access credentials!')

def check_folder():
    if not os.path.exists("data/tweets"):
        print("Creating data/tweets folder")
        os.makedirs("data/tweets")


def check_file():
    data = {"api":{'consumer_key': '', 'consumer_secret': '',
            'access_token': '', 'access_secret': ''}, 'accounts': {}}
    f = "data/tweets/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    if not twInstalled:
        bot.pip_install("tweepy")
        import tweepy as tw
    n = Tweets(bot)
    bot.add_cog(n)

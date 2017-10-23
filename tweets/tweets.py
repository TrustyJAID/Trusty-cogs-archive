from typing import Generator, Tuple, Iterable
from random import choice as randchoice
from datetime import datetime as dt
from discord.ext import commands
import discord
import asyncio
from redbot.core import Config
from redbot.core import checks
from .tweet_entry import TweetEntry
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
        if self.bot.is_closed():
            return False
        else:
            return True

    def on_error(self, status_code):
        print("A tweet stream error has occured! " + str(status_code))
        if status_code in [420, 504, 503, 502, 500, 400, 401, 403, 404]:
            return False

    def on_disconnect(self, notice):
        print("Twitter has sent a disconnect code")
        return False

    def on_warning(self, notice):
        print("Twitter has sent a disconnection warning")
        return True


class Tweets():
    """Cog for displaying info from Twitter's API"""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 133926854)
        default_global = {"api":{'consumer_key': '', 'consumer_secret': '',
            'access_token': '', 'access_secret': ''}, "accounts":[]}
        self.config.register_global(**default_global)
        # auth = tw.OAuthHandler(self.config.consumer_key, self.config.consumer_secret)
        # auth.set_access_token(self.config.access_token, self.config.access_secret)
        # api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5, retry_errors=5)
        # tweet_list = [x for x in self.config.accounts]
        # stream_start = TweetListener(api, self.bot)
        # self.mystream = tw.Stream(auth, stream_start)
        # self.mystream.filter(follow=tweet_list, async=True)
        
    def __unload(self):
        self.mystream.disconnect()
        

    async def authenticate(self):
        """Authenticate with Twitter's API"""
        auth = tw.OAuthHandler(self.config.api.consumer_key, self.config.consumer_secret)
        auth.set_access_token(self.config.access_token, self.config.access_secret)
        return tw.API(auth)

    async def tweet_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        s = post_list[page]
        created_at = s.created_at
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
        post_url =\
            "https://twitter.com/{}/status/{}".format(s.user.screen_name, s.id)
        desc = "Created at: {}".format(created_at)
        em = discord.Embed(description=s.text,
                           colour=discord.Colour(value=self.random_colour()),
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
                await ctx.send(embed=em)
            await message.add_reaction("⬅")
            await message.add_reaction("❌")
            await message.add_reaction("➡")
        else:
            message = await message.edit(embed=em)
        def check(reaction, user):
            return user == ctx.message.author and reaction.emoji in ["➡", "⬅", "❌"]
        react, user = await ctx.wait_for("reaction_add", check=check, timeout=timeout)

        if react is None:
            await ctx.remove_reaction("⬅", ctx.user)
            await ctx.remove_reaction("❌", ctx.user)
            await ctx.remove_reaction("➡", ctx.user)
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
                ctx.delete_message(message)

    @commands.group(pass_context=True, no_pm=True, name='tweets')
    async def _tweets(self, ctx):
        """Gets various information from Twitter's API"""
        if ctx.invoked_subcommand is None:
            await ctx.send_cmd_help(ctx)

    @_tweets.command(pass_context=True, name="send")
    @checks.is_owner()
    async def send_tweet(self, ctx, *, message: str):
        api = await self.authenticate()
        api.update_status(message)
        await ctx.send_message(ctx.message.channel, "Tweet sent!")


    def random_colour(self):
        return int(''.join([randchoice('0123456789ABCDEF')for x in range(6)]), 16)

    @_tweets.command(pass_context=True, no_pm=True, name='getuser')
    async def get_user(self, ctx, username: str):
        """Get info about the specified user"""
        message = ""
        if username is not None:
            api = await self.authenticate()
            user = api.get_user(username)
            url = "https://twitter.com/" + user.screen_name
            emb = discord.Embed(title=user.name,
                                colour=discord.Colour(value=self.random_colour()),
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
            await ctx.send_message(ctx.message.channel, embed=emb)
        else:
            message = "Uh oh, an error occurred somewhere!"
            await ctx.send(message)

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
                await ctx.send("I can't do that, silly! Please specify a \
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
                await ctx.send("Whoops! Something went wrong here. \
                    The error code is " + str(e))
                return
            if len(msg_list) > 0:
                await self.tweet_menu(ctx, msg_list, page=0, timeout=30)
            else:
                await ctx.send("No tweets available to display!")
        else:
            await ctx.send("No username specified!")
            return
    
    async def on_tweet_status(self, status):
        """Posts the tweets to the channel"""
        # await ctx.send_message(ctx.get_channel("321105104931389440"), status.text)
        username = status.user.screen_name
        user_id = str(status.user.id)
        if user_id not in self.config.accounts:
            return
        try:
            if status.in_reply_to_screen_name is not None and not self.settings["accounts"][user_id]["replies"]:
                return
            post_url = "https://twitter.com/{}/status/{}".format(status.user.screen_name, status.id)
            em = discord.Embed(description=status.text,
                            colour=discord.Colour(value=self.random_colour()),
                            url=post_url,
                            timestamp=status.created_at)
            try:                                
                em.set_author(name=status.user.name, icon_url=status.user.profile_image_url)
            except:
                print(status.user.name + " could not get profile image!")
            if hasattr(status, "extended_entities"):
                em.set_image(url=status.extended_entities["media"][0]["media_url"])

            if status.text.startswith("RELEASE:") and username == "wikileaks":
                channel_send = await self.bot.get_channel(365376327278395393)
                await channel_send.send_message(embed=em)
            for channel in list(self.config.accounts.user_id.channel):
                channel_send = await self.bot.get_channel(int(channel))
                await channel_send.send(embed=em)
            # self.settings["accounts"][user_id]["lasttweet"] = status.id
            # dataIO.save_json(self.settings_file, self.settings)
        except tw.TweepError as e:
            print("Whoops! Something went wrong here. \
                The error code is " + str(e) + username)
            return
    
    @commands.group(pass_context=True, name='autotweet')
    @checks.admin_or_permissions(manage_channels=True)
    async def _autotweet(self, ctx):
        """Command for setting accounts and channels for posting"""
        if ctx.invoked_subcommand is None:
            await ctx.send_cmd_help(ctx)

    @_autotweet.command(pass_context=True, name="restart")
    async def restart_stream(self, ctx):
        """Restarts the twitter stream if any issues occur."""
        self.autotweet_restart()
        await ctx.send("Restarting the twitter stream.")

    def autotweet_restart(self):
        """Restarts the stream by disconnecting the old one and starting it again with new data"""
        self.mystream.disconnect()
        auth = tw.OAuthHandler(self.config.consumer_key, self.config.consumer_secret)
        auth.set_access_token(self.config.access_token, self.config.access_secret)
        api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5, retry_errors=5)
        tweet_list = list(self.config.accounts)
        stream_start = TweetListener(api, self.bot)
        self.mystream = tw.Stream(auth, stream_start)
        self.mystream.filter(follow=tweet_list, async=True)
    
    @_autotweet.command(pass_context=True, name="replies")
    async def _replies(self, ctx, account, replies):
        """Enable or disable twitter replies from being posted for an account"""
        account = account.lower()
        for user_id in list(await self.config.accounts()):
            if account == self.config.accounts[user_id].username.lower():
                channel_list = self.settings["accounts"][user_id]["channel"]
                user = user_id
        if channel_list is None:
            await ctx.send("{} is not in my list of accounts!".format(account))
            return
        if replies.lower() in ["true", "on"]:
            self.settings["accounts"][user]["replies"] = True
            dataIO.save_json(self.settings_file, self.settings)
            await ctx.send("I will post replies for {} now!".format(account))
        if replies.lower() in ["false", "off"]:
            self.settings["accounts"][user]["replies"] = False
            dataIO.save_json(self.settings_file, self.settings)
            await ctx.send("I will stop posting replies for {} now!".format(account))

    async def get_followed_accounts(self) -> Generator[TweetEntry, None, None]:
        return (TweetEntry.from_json(d) for d in (await self.config.accounts()))

    async def is_followed_account(self, twitter_id) -> bool:
        followed_accounts = await self.get_followed_accounts()

        for account in followed_accounts:
            if account.id == twitter_id:
                return True, account
        return False, None

    @_autotweet.command(pass_context=True, name="add")
    async def _add(self, ctx, account, channel:discord.TextChannel=None):
        """Adds a twitter account to the specified channel"""
        api = await self.authenticate()
        try:
            for status in tw.Cursor(api.user_timeline, id=account).items(1):
                user_id = status.user.id
                screen_name = status.user.screen_name
                last_id = status.id
        except tw.TweepError as e:
            print("Whoops! Something went wrong here. \
                    The error code is " + str(e) + account)
            await ctx.send("That account does not exist! Try again")
            return
        if channel is None:
            channel = ctx.message.channel
        followed_accounts = await self.config.accounts()

        is_followed, twitter_account = await self.is_followed_account(user_id)
        if is_followed:
            if channel.id in twitter_account.channel:
                await ctx.send("I am already posting {} tweets in {}".format(screen_name, channel.mention))
                return
            else:
                twitter_account.channel.append(channel.id)
                return
        else:
            twitter_account = TweetEntry(user_id, screen_name, [channel.id], last_id)
            followed_accounts.append(twitter_account.to_json())
            await self.config.accounts.set(followed_accounts)
        await ctx.send("{0} Added to {1}!".format(account, channel.mention))
        self.autotweet_restart()

    @_autotweet.command(pass_context=True, name="list")
    async def _list(self, ctx):
        """Lists the autotweet accounts on the server"""
        account_list = ""
        server = ctx.message.server
        server_channels = [x.id for x in server.channels]
        for account in self.config.accounts:
            for channel_id in account.channel:
                if channel_id in server_channels:
                    account_list += account.twitter_name + ", "
        if account_list != "":
            embed = discord.Embed(title="Twitter accounts posting in {}".format(server.name),
                                  colour=discord.Colour(value=self.random_colour()),
                                  description=account_list[:-2],
                                  timestamp=ctx.message.timestamp)
            embed.set_author(name=server.name, icon_url=server.icon_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("I don't seem to have autotweets setup here!")


    @_autotweet.command(pass_context=True, name="del", aliases=["delete", "rem", "remove"])
    async def _del(self, ctx, account, channel:discord.TextChannel=None):
        """Removes a twitter account to the specified channel"""
        account = account.lower()
        api = await self.authenticate()
        if channel is None:
            channel = ctx.message.channel
        try:
            for status in tw.Cursor(api.user_timeline, id=account).items(1):
                user_id = str(status.user.id)      
        except tw.TweepError as e:
            print("Whoops! Something went wrong here. \
                    The error code is " + str(e) + account)
            await ctx.send("That account does not exist! Try again")
            return
        if user_id not in self.settings["accounts"]:
            await ctx.send("{} is not in my list of accounts!".format(account))
            return

        channel_list = self.settings["accounts"][user_id]["channel"]
        if channel.id in channel_list:
            self.settings["accounts"][user_id]["channel"].remove(channel.id)
            dataIO.save_json(self.settings_file, self.settings)
            self.autotweet_restart()
            await ctx.send("{} has been removed from {}".format(account, channel.mention))
            if len(self.settings["accounts"][user_id]["channel"]) < 2:
                del self.settings["accounts"][user_id]
                dataIO.save_json(self.settings_file, self.settings)
                self.autotweet_restart()
        else:
            await ctx.send("{0} doesn't seem to be posting in {1}!"
                               .format(account, channel.mention))


    @commands.group(pass_context=True, name='tweetset')
    @checks.admin_or_permissions(manage_server=True)
    async def _tweetset(self, ctx):
        """Command for setting required access information for the API.
        To get this info, visit https://apps.twitter.com and create a new application.
        Once the application is created, click Keys and Access Tokens then find the
        button that sends Create my access token and click that. Once that is done,
        use the subcommands of this command to set the access details"""
        if ctx.invoked_subcommand is None:
            await ctx.send_cmd_help(ctx)

    @_tweetset.command(name='creds')
    @checks.is_owner()
    async def set_creds(self, consumer_key: str, consumer_secret: str, access_token: str, access_secret: str):
        """Sets the access credentials. See [p]help tweetset for instructions on getting these"""
        if consumer_key is not None:
           self.config.consumer_key = consumer_key
        else:
            await ctx.send("No consumer key provided!")
            return
        if consumer_secret is not None:
            self.config.consumer_secret = consumer_secret
        else:
            ctx.send("No consumer secret provided!")
            return
        if access_token is not None:
            self.config.access_token = access_token
        else:
            ctx.send("No access token provided!")
            return
        if access_secret is not None:
            self.config.access_secret = access_secret
        else:
            await ctx.send("No access secret provided!")
            return
        await ctx.send('Set the access credentials!')

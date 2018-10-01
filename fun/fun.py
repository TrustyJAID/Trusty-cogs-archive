import random
import re
import json
from redbot.core import commands
import discord

'''Module for fun/meme commands commands
   Fun commands from Appu's selfbot
'''


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.regionals = {'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
                          'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
                          'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
                          'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
                          'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
                          'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
                          'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
                          'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
                          'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
                          'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
                          'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
                          'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
                          's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
                          'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
                          'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
                          'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
                          'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
                          '0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣',
                          '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣', '!': '\u2757',
                          '?': '\u2753'}
        self.emoji_reg = re.compile(r'<:.+?:([0-9]{15,21})>')
        self.ball = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']

    emoji_dict = {
    # these arrays are in order of "most desirable". Put emojis that most convincingly correspond to their letter near the front of each array.
        'a': ['🇦', '🅰', '🍙', '🔼', '4⃣'],
        'b': ['🇧', '🅱', '8⃣'],
        'c': ['🇨', '©', '🗜'],
        'd': ['🇩', '↩'],
        'e': ['🇪', '3⃣', '📧', '💶'],
        'f': ['🇫', '🎏'],
        'g': ['🇬', '🗜', '6⃣', '9⃣', '⛽'],
        'h': ['🇭', '♓'],
        'i': ['🇮', 'ℹ', '🚹', '1⃣'],
        'j': ['🇯', '🗾'],
        'k': ['🇰', '🎋'],
        'l': ['🇱', '1⃣', '🇮', '👢', '💷'],
        'm': ['🇲', 'Ⓜ', '📉'],
        'n': ['🇳', '♑', '🎵'],
        'o': ['🇴', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
        'p': ['🇵', '🅿'],
        'q': ['🇶', '♌'],
        'r': ['🇷', '®'],
        's': ['🇸', '💲', '5⃣', '⚡', '💰', '💵'],
        't': ['🇹', '✝', '➕', '🎚', '🌴', '7⃣'],
        'u': ['🇺', '⛎', '🐉'],
        'v': ['🇻', '♈', '☑'],
        'w': ['🇼', '〰', '📈'],
        'x': ['🇽', '❎', '✖', '❌', '⚒'],
        'y': ['🇾', '✌', '💴'],
        'z': ['🇿', '2⃣'],
        '0': ['0⃣', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
        '1': ['1⃣', '🇮'],
        '2': ['2⃣', '🇿'],
        '3': ['3⃣'],
        '4': ['4⃣'],
        '5': ['5⃣', '🇸', '💲', '⚡'],
        '6': ['6⃣'],
        '7': ['7⃣'],
        '8': ['8⃣', '🎱', '🇧', '🅱'],
        '9': ['9⃣'],
        '?': ['❓'],
        '!': ['❗', '❕', '⚠', '❣'],

        # emojis that contain more than one letter can also help us react
        # letters that we are trying to replace go in front, emoji to use second
        #
        # if there is any overlap between characters that could be replaced,
        # e.g. 💯 vs 🔟, both could replace "10",
        # the longest ones & most desirable ones should go at the top
        # else you'll have "100" -> "🔟0" instead of "100" -> "💯".
        'combination': [['cool', '🆒'],
                        ['back', '🔙'],
                        ['soon', '🔜'],
                        ['free', '🆓'],
                        ['end', '🔚'],
                        ['top', '🔝'],
                        ['abc', '🔤'],
                        ['atm', '🏧'],
                        ['new', '🆕'],
                        ['sos', '🆘'],
                        ['100', '💯'],
                        ['loo', '💯'],
                        ['zzz', '💤'],
                        ['...', '💬'],
                        ['ng', '🆖'],
                        ['id', '🆔'],
                        ['vs', '🆚'],
                        ['wc', '🚾'],
                        ['ab', '🆎'],
                        ['cl', '🆑'],
                        ['ok', '🆗'],
                        ['up', '🆙'],
                        ['10', '🔟'],
                        ['11', '⏸'],
                        ['ll', '⏸'],
                        ['ii', '⏸'],
                        ['tm', '™'],
                        ['on', '🔛'],
                        ['oo', '🈁'],
                        ['!?', '⁉'],
                        ['!!', '‼'],
                        ['21', '📅'],
                        ]
    }

    # used in textflip
    text_flip = {}
    char_list = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}"
    alt_char_list = "{|}zʎxʍʌnʇsɹbdouɯlʞɾᴉɥƃɟǝpɔqɐ,‾^[\]Z⅄XMΛ∩┴SɹQԀONW˥ʞſIHפℲƎpƆq∀@¿<=>;:68ㄥ9ϛㄣƐᄅƖ0/˙-'+*(),⅋%$#¡"[::-1]
    for idx, char in enumerate(char_list):
        text_flip[char] = alt_char_list[idx]
        text_flip[alt_char_list[idx]] = char

    # used in [p]react, checks if it's possible to react with the duper string or not
    def has_dupe(duper):
        collect_my_duper = list(filter(lambda x: x != '⃣',
                                       duper))  #   ⃣ appears twice in the number unicode thing, so that must be stripped
        return len(set(collect_my_duper)) != len(collect_my_duper)

    # used in [p]react, replaces e.g. 'ng' with '🆖'
    def replace_combos(react_me):
        for combo in Fun.emoji_dict['combination']:
            if combo[0] in react_me:
                react_me = react_me.replace(combo[0], combo[1], 1)
        return react_me

    # used in [p]react, replaces e.g. 'aaaa' with '🇦🅰🍙🔼'
    def replace_letters(react_me):
        for char in "abcdefghijklmnopqrstuvwxyz0123456789!?":
            char_count = react_me.count(char)
            if char_count > 1:  # there's a duplicate of this letter:
                if len(Fun.emoji_dict[
                           char]) >= char_count:  # if we have enough different ways to say the letter to complete the emoji chain
                    i = 0
                    while i < char_count:  # moving goal post necessitates while loop instead of for
                        if Fun.emoji_dict[char][i] not in react_me:
                            react_me = react_me.replace(char, Fun.emoji_dict[char][i], 1)
                        else:
                            char_count += 1  # skip this one because it's already been used by another replacement (e.g. circle emoji used to replace O already, then want to replace 0)
                        i += 1
            else:
                if char_count == 1:
                    react_me = react_me.replace(char, Fun.emoji_dict[char][0])
        return react_me

    @commands.command(pass_context=True)
    async def vowelreplace(self, ctx, replace, *, msg):
        """Replaces all vowels in a word with a letter"""
        result = ""
        for letter in msg:
            if letter.lower() in "aeiou":
                result += replace
            else:
                result += letter
        
        await ctx.send(result)

    @commands.command(pass_context=True)
    async def textflip(self, ctx, *, msg):
        """Flip given text."""
        result = ""
        for char in msg:
            if char in self.text_flip:
                result += self.text_flip[char]
            else:
                result += char
        await ctx.send(result[::-1])  # slice reverses the string

    @commands.command(pass_context=True)
    async def regional(self, ctx, *, msg):
        """Replace letters with regional indicator emojis"""
        
        msg = list(msg)
        regional_list = [self.regionals[x.lower()] if x.isalnum() or x in ["!", "?"] else x for x in msg]
        regional_output = '\u200b'.join(regional_list)
        await ctx.send(regional_output)

    @commands.command(pass_context=True)
    async def space(self, ctx, *, msg):
        """Add n spaces between each letter. Ex: [p]space 2 thicc"""
        
        if msg.split(' ', 1)[0].isdigit():
            spaces = int(msg.split(' ', 1)[0]) * ' '
            msg = msg.split(' ', 1)[1].strip()
        else:
            spaces = ' '
        spaced_message = spaces.join(list(msg))
        await ctx.send(spaced_message)

    async def find_channel(self, channel_list, text):
        if text.isdigit():
            found_channel = discord.utils.get(channel_list, id=int(text))
        elif text.startswith("<#") and text.endswith(">"):
            found_channel = discord.utils.get(channel_list,
                                              id=text.replace("<", "").replace(">", "").replace("#", ""))
        else:
            found_channel = discord.utils.get(channel_list, name=text)
        return found_channel

    # given String react_me, return a list of emojis that can construct the string with no duplicates (for the purpose of reacting)
    # TODO make it consider reactions already applied to the message
    @commands.command(pass_context=True, aliases=['r'])
    async def react(self, ctx, msg: str, msg_id="last", channel="current", prefer_combine: bool = False):
        """Add letter(s) as reaction to previous message. Ex: [p]react hot"""
        
        msg = msg.lower()

        msg_id = None if not msg_id.isdigit() else int(msg_id)

        limit = 25 if msg_id else 2

        reactions = []
        non_unicode_emoji_list = []
        react_me = ""  # this is the string that will hold all our unicode converted characters from msg

        # replace all custom server emoji <:emoji:123456789> with "<" and add emoji ids to non_unicode_emoji_list
        char_index = 0
        emotes = re.findall(r"<a?:(?:[a-zA-Z0-9]+?):(?:[0-9]+?)>", msg)
        react_me = re.sub(r"<a?:([a-zA-Z0-9]+?):([0-9]+?)>", "", msg)
        
        for emote in emotes:
            reactions.append(discord.utils.get(self.bot.emojis, id=int(emote.split(":")[-1][:-1])))
            non_unicode_emoji_list.append(emote)
            
        
        if Fun.has_dupe(non_unicode_emoji_list):
            return await ctx.send(
                                  "You requested that I react with at least two of the exact same specific emoji. I'll try to find alternatives for alphanumeric text, but if you specify a specific emoji must be used, I can't help.")

        react_me_original = react_me  # we'll go back to this version of react_me if prefer_combine is false but we can't make the reaction happen unless we combine anyway.

        if Fun.has_dupe(react_me):  # there's a duplicate letter somewhere, so let's go ahead try to fix it.
            if prefer_combine:  # we want a smaller reaction string, so we'll try to combine anything we can right away
                react_me = Fun.replace_combos(react_me)
            react_me = Fun.replace_letters(react_me)
            # print(react_me)
            if Fun.has_dupe(react_me):  # check if we were able to solve the dupe
                if not prefer_combine:  # we wanted the most legible reaction string possible, even if it was longer, but unfortunately that's not possible, so we're going to combine first anyway
                    react_me = react_me_original
                    react_me = Fun.replace_combos(react_me)
                    react_me = Fun.replace_letters(react_me)
                    if Fun.has_dupe(react_me):  # this failed too, so there's really nothing we can do anymore.
                        return await ctx.send("Failed to fix all duplicates. Cannot react with this string.")
                else:
                    return await ctx.send("Failed to fix all duplicates. Cannot react with this string.")
                    

            lt_count = 0
            for char in react_me:
                if char not in "0123456789":  # these unicode characters are weird and actually more than one character.
                    if char != '⃣':  # </3
                        reactions.append(char)
                else:
                    reactions.append(self.emoji_dict[char][0])
        else:  # probably doesn't matter, but by treating the case without dupes seperately, we can save some time
            lt_count = 0
            for char in react_me:
                if char in "abcdefghijklmnopqrstuvwxyz0123456789!?":
                    reactions.append(self.emoji_dict[char][0])
                else:
                    reactions.append(char)

        if channel == "current":
            async for message in ctx.message.channel.history(limit=limit):
                if (not msg_id and message.id != ctx.message.id) or (msg_id == message.id):
                    for i in reactions:
                        try:
                            await message.add_reaction(i)
                        # :ok_hand: lit fam :ok_hand:
                        except:
                            pass
        else:
            found_channel = await self.find_channel(ctx.guild.channels, channel)
            if not found_channel:
                found_channel = self.find_channel(self.bot.get_all_channels(), channel)
            if found_channel:
                async for message in found_channel.history(limit=limit):
                    if (not msg_id and message.id != ctx.message.id) or (msg_id == message.id):
                        for i in reactions:
                            try:
                                await message.add_reaction(i)
                            except:
                                pass
            else:
                await ctx.send("Channel not found.")

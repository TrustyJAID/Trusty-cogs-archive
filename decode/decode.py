import discord
from redbot.core import commands
import binascii
import random
import hashlib



class Encoding(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.table = {
    "A": ["00", "01", "10", "11", "00", "00", "00", "01", "01", "01", "10", "10", "10", "11", "11", "11"],
    "G": ["01", "10", "11", "00", "11", "10", "01", "11", "00", "10", "11", "00", "01", "00", "01", "10"],
    "C": ["10", "11", "00", "01", "10", "11", "10", "10", "11", "00", "01", "11", "00", "01", "00", "01"],
    "T": ["11", "00", "01", "10", "01", "01", "11", "00", "10", "11", "00", "01", "11", "10", "10", "00"]
    }
        # A = 00
        # G = 10
        # C = 11
        # T = 01
    def remove_non_ascii(self, data):
        msg = b""
        for char in data:
            if char in range(0, 127):
                msg += bytes(chr(char).encode("utf8"))
        return msg

    def search_words(self, data):
        count = 0
        try:
            for char in data:
                if ord(char) in range(47, 122):
                    count += 1
        except TypeError:
            for char in data:
                if char in range(47, 122):
                    count += 1
        try:
            if(count/len(data)) >= 0.75:
                return True
        except ZeroDivisionError:
            return False
        return False


    @commands.group(name="encode")
    async def _encode(self, ctx: commands.Context):
        """Encode a string."""
        pass

    @commands.group(name="decode")
    async def _decode(self, ctx: commands.Context):
        """Decode a string."""
        pass

    @_encode.command(name="binary")
    async def encode_binary(self, ctx: commands.Context, *, message: str):
        ascii_bin = ' '.join(bin(x)[2:].zfill(8) for x in message.encode('UTF-8'))
        await ctx.send(ascii_bin)

    @_decode.command(name="binary")
    async def decode_binary(self, ctx: commands.Context, *, message: str):
        msg = message.replace(" ", "")
        bin_ascii = "".join([chr(int(msg[i:i+8],2)) for i in range(0,len(msg),8)])
        await ctx.send(bin_ascii)


    @_encode.command(name="dna")
    async def dna_encode(self, ctx: commands.Context, *, message: str):
        """Encodes a string into DNA 4 byte ACGT format"""
        dna = {"00": "A", "01": "T", "10": "G", "11": "C"}
        message = message.strip(" ")
        binary = ' '.join(bin(x)[2:].zfill(8) for x in message.encode('UTF-8')).replace(" ", "")
        binlist = [binary[i:i+2] for i in range(0, len(binary), 2)]
        newmsg = ""
        count = 0
        for letter in binlist:
            newmsg += dna[letter]
            count += 1
            if count == 4:
                count = 0
                newmsg += " "
        await ctx.send(newmsg)


    @_decode.command(name="dna")
    async def dna_decode(self,ctx: commands.Context, *, message: str):
        """Decodes a string of DNA in 4 byte ACGT format."""
        message = message.strip(" ")
        mapping = {}
        replacement = ""
        for i in range(0, 16):
            skip = [" ", "\n", "\r"]
            for character in message:
                if character in skip:
                    continue
                replacement += self.table[character][i]
            try:
                n = int("0b" + replacement, 2)
                mapping[i] = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode("utf8", "ignore")
            except TypeError:
                pass
            replacement = ""
        num = 1
        new_msg = ""
        for result in mapping.values():
            new_msg += str(num) + ": " + result + "\n"
            num += 1
        embed = discord.Embed(title=message,
                              description="```markdown\n" + new_msg[:1950] + "```",
                              timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)

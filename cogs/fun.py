import discord, random, os
from discord.ext import commands
from uwuipy import uwuipy
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class fun(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def uwu(self, ctx, *, message):
      if message == None:
            embed = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: what do you want me to uwuify?", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
      else:
            uwu = uwuipy()
            uwu_message = uwu.uwuify(message)
            await sendmsg(self, ctx, uwu_message, None, None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def kiss(self, ctx, user: discord.Member = None):
        if not user:
            embed = discord.Embed(color=Colours.standard,description=f"> {Emotes.warning} {ctx.author.mention}: would you really like to kiss yourself?")
            return await sendmsg(self, ctx, None, embed, None, None, None, None)

        elif user == ctx.author:
            return await sendmsg(self, ctx, "here, have a kiss :heart:", None, None, None, None, None)
        else:
            embed = discord.Embed(color=Colours.standard)
            embed.description = f"***{ctx.author.name} kissed {user.name}***"
            embed.set_image(url=f'https://purrbot.site/img/sfw/kiss/gif/kiss_{random.choice(["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016"])}.gif')
            await sendmsg(self, ctx, None, embed, None, None, None, None)  

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def hug(self, ctx, user: discord.Member = None):
        if not user:
            embed = discord.Embed(color=Colours.standard,description=f"> {Emotes.warning} {ctx.author.mention}: would you really like to hug yourself?")
            return await sendmsg(self, ctx, None, embed, None, None, None, None)

        elif user == ctx.author:
            return await sendmsg(self, ctx, "here, have a hug :heart:", None, None, None, None, None)

        else:
            embed = discord.Embed(color=Colours.standard)
            embed.description = f"***{ctx.author.name} hugged {user.name}***"
            embed.set_image(url=f'https://purrbot.site/img/sfw/hug/gif/hug_{random.choice(["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016"])}.gif')
            await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def emojify(self, ctx, *, text=None):
        if not text:
            return await ctx.reply("?")
        emojis = []
        for char in text.lower().replace(" ", "  "):
            if char.isdigit():
                number2emoji = {
                    "1": "one",
                    "2": "two",
                    "3": "three",
                    "4": "four",
                    "5": "five",
                    "6": "six",
                    "7": "seven",
                    "8": "eight",
                    "9": "nine",
                    "0": "zero",
                }

                emojis.append(f":{number2emoji[char]}:")

            elif char.isalpha():
                emojis.append(f":regional_indicator_{char}:")
            else:
                emojis.append(char)

        await sendmsg(self, ctx, " ".join(emojis), None, None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def morse(self, ctx, *, text: str):
        to_morse = {
            "a": ".-",
            "b": "-...",
            "c": "-.-.",
            "d": "-..",
            "e": ".",
            "f": "..-.",
            "g": "--.",
            "h": "....",
            "i": "..",
            "j": ".---",
            "k": "-.-",
            "l": ".-..",
            "m": "--",
            "n": "-.",
            "o": "---",
            "p": ".--.",
            "q": "--.-",
            "r": ".-.",
            "s": "...",
            "t": "-",
            "u": "..-",
            "v": "...-",
            "w": ".--",
            "x": "-..-",
            "y": "-.--",
            "z": "--..",
            "1": ".----",
            "2": "..---",
            "3": "...--",
            "4": "....-",
            "5": ".....",
            "6": "-....",
            "7": "--...",
            "8": "---..",
            "9": "----.",
            "0": "-----",
        }

        cipher = ""
        for letter in text:
            if letter.isalpha() or letter.isdigit():
                cipher += to_morse[letter.lower()] + " "
            else:
                cipher += letter
        await sendmsg(self, ctx, cipher, None, None, None, None, None)

async def setup(bot) -> None:
    await bot.add_cog(fun(bot))
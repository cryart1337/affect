import discord, datetime
import aiosqlite
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class afk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT reason, time FROM afk1 WHERE user = ? AND guild = ?", (message.author.id, message.guild.id,))
            data = await cursor.fetchone()
            if data:
                embed = discord.Embed(color = Colours.standard, description = f"> 👋 {message.author.mention}: Welcome back, you were last seen <t:{int(data[1])}:R>")
                await message.reply(embed=embed, delete_after=5) 
                await cursor.execute("DELETE FROM afk1 WHERE user = ? AND guild = ?", (message.author.id, message.guild.id,))
            if message.mentions:
                for mention in message.mentions:
                    await cursor.execute("SELECT reason, time FROM afk1 WHERE user = ? AND guild = ?", (mention.id, message.guild.id,))
                    data2 = await cursor.fetchone()
                    if data2 and mention.id != message.author.id:
                        embed = discord.Embed(color = Colours.standard, description = f"> 💤 {message.author.mention}: {mention.mention} is currently AFK: `{data2[0]}` - <t:{int(data2[1])}:R>")
                        await message.channel.send(embed=embed, delete_after=5)
        await self.bot.db.commit()

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def afk(self, ctx, *, reason = None):
        if reason == None:
            reason = "AFK"
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT reason, time FROM afk1 WHERE user = ? AND guild = ?", (ctx.author.id, ctx.guild.id,))
            data = await cursor.fetchone()
            if data:
                if data[0] == reason:
                    embed = discord.Embed(color = Colours.standard, description = f"> {Emotes.warning} {ctx.author.mention}: you're already afk with that reason")
                    return await sendmsg(self, ctx, None, embed, None, None, None, None)
                await cursor.execute("UPDATE afk1 SET reason = ? AND time = ? WHERE user = ? AND guild = ?", (reason, ctx.author.id, ctx.guild.id, int(datetime.datetime.now().timestamp()),))
            else:
                await cursor.execute("INSERT INTO afk1 (user, guild, reason, time) VALUES (?, ?, ?, ?)", (ctx.author.id, ctx.guild.id, reason, int(datetime.datetime.now().timestamp()),))
                embed = discord.Embed(color = Colours.standard, description = f"> {Emotes.approve} {ctx.author.mention}: You're now **AFK:** `{reason}`")
                await sendmsg(self, ctx, None, embed, None, None, None, None)
        await self.bot.db.commit()

async def setup(bot) -> None:
    await bot.add_cog(afk(bot))
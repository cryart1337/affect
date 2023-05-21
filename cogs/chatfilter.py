import discord
import aiosqlite
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class chatfilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT trigger FROM chatfilter WHERE guild = {}".format(ctx.guild.id))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[0]
                            if ctx.author.bot:
                                pass
                            else:
                                if trigger.lower() in ctx.content.lower():
                                    await ctx.delete()
                                    embed = discord.Embed(color=Colours.standard,description = f"> {Emotes.nono} {ctx.author.mention}: That word is not allowed here")
                                    msg = await ctx.channel.send(embed=embed, delete_after=2) 

    
    @commands.group()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def chatfilter(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Command: chatfilter", description="you can blacklisted a word",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="[word]")
            e.add_field(name="permissions", value="manage_messages", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;chatfilter add test\nSyntax: ;chatfilter clear\nSyntax: ;chatfilter show```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return

    @chatfilter.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def add(self, ctx, *, trigger):
        if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO chatfilter VALUES (?, ?)", (trigger, ctx.guild.id,))
            embed = discord.Embed(description = f"> {Emotes.approve} Successfully added trigger `{trigger}` to the filter", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @chatfilter.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def clear(self, ctx):
        if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM chatfilter WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"> {Emotes.approve} Successfully cleared blacklisted words", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @chatfilter.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def show(self, ctx):
        if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT trigger FROM chatfilter WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        response = table[0]
                        num += 1
                        auto += f"\n`{num}` {response}"
                    embed = discord.Embed(description = auto, color = Colours.standard)
                    embed.set_author(name = "> list of blacklisted words", icon_url = ctx.message.author.display_avatar)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
        except Exception as e:
            print(e)

async def setup(bot) -> None:
    await bot.add_cog(chatfilter(bot))
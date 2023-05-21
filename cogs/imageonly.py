import discord
import aiosqlite
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class imageonly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT channel FROM imageonly WHERE guild = {}".format(ctx.guild.id))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[0]
                            channel = self.bot.get_channel(trigger)
                            if ctx.author.bot:
                                pass
                            else:
                                if ctx.channel.id == channel.id:
                                    if ctx.attachments:
                                        pass
                                    else:
                                        await ctx.delete()

    
    @commands.group()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def imageonly(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Command: imageonly", description="only pictures on the image channel only",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="moderation")
            e.add_field(name="Arguments", value="<subcommand> [channel]")
            e.add_field(name="permissions", value="manage_guild", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;imageonly add #media\nSyntax: ;imageonly clear\nSyntax: ;imageonly show```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return

    @imageonly.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def add(self, ctx, *, channel: discord.TextChannel):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO imageonly VALUES (?, ?)", (channel.id, ctx.guild.id,))
            e = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: the channel has been successfully set up",color=Colours.standard)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @imageonly.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def clear(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM imageonly WHERE guild = ?", (ctx.guild.id,))
            e = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: the channel has been successfully deleted",color=Colours.standard)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @imageonly.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def show(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT channel FROM imageonly WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        response = table[0]
                        channel = self.bot.get_channel(response)
                        num += 1
                        auto += f"\n`{num}` {channel.mention}"
                    embed = discord.Embed(description = auto, color = Colours.standard)
                    embed.set_author(name = "> list of image-only channels", icon_url = ctx.message.author.display_avatar)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
        except Exception as e:
            print(e)

async def setup(bot) -> None:
    await bot.add_cog(imageonly(bot))
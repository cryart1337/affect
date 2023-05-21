import discord
import aiosqlite
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT role FROM autorole WHERE guild = {}".format(member.guild.id))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            trigger = table[0]
                            role = member.guild.get_role(trigger)
                            if role in member.roles:
                                pass
                            else:
                                await member.add_roles(role)
                    else:
                        pass
    
    @commands.group()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Command: autorole", description="when you select a role it is automatically given to the members",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [@role]")
            e.add_field(name="permissions", value="manage_guild", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;autorole add @test\nSyntax: ;autorole clear\nSyntax: ;autorole remove @test\nSyntax: ;autorole show```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return 

    @autorole.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def add(self, ctx, *, role: discord.Role):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO autorole VALUES (?, ?)", (role.id, ctx.guild.id,))
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: Now assigning {role.mention} to new members", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)
    @autorole.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def clear(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autorole WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: No longer assigning any role to new members", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autorole.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def show(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT role FROM autorole WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        response = table[0]
                        role = ctx.guild.get_role(response)
                        num += 1
                        auto += f"\n`{num}` {role.mention}"
                    embed = discord.Embed(description = auto, color = Colours.standard)
                    embed.set_author(name = "> list of automatically assigned roles", icon_url = ctx.message.author.display_avatar)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
        except Exception as e:
            print(e)

    @autorole.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def delete(self, ctx, *, msg: discord.Role):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autorole WHERE guild = ? AND role LIKE ?", (ctx.guild.id, msg.id,))
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: No longer assigning {msg.mention} to new members", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

async def setup(bot) -> None:
    await bot.add_cog(autorole(bot))
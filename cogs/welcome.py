import discord
from discord.ext import commands
from utils.embedparser import to_object
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(member.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                msg = check[1]
                chan = check[2]
                channel = self.bot.get_channel(chan)
                user = member
                guild = member.guild
                z = msg.replace('{user}', str(user)).replace('{user.name}', str(user.name)).replace('{user.mention}', str(user.mention)).replace('{user.avatar}', str(user.display_avatar.url)).replace('{user.joined_at}', f'<t:{int(user.created_at.timestamp())}:R>').replace('{user.discriminator}', str(user.discriminator)).replace('{guild.name}', str(guild.name)).replace('{guild.count}', str(guild.member_count)).replace('{guild.icon}', str(guild.icon)).replace('{guild.id}', str(guild.id))
                x = await to_object(z)
                await channel.send(**x)

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def welcome(self, ctx):
        e = discord.Embed(title="Command: welcome", description="configure a welcome message for your server",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="Arguments", value="<subcommand> [message / channel]")
        e.add_field(name="permissions", value="manage_guild", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;welcome message\nSyntax: ;welcome channel\nSyntax: ;welcome config\nSyntax: ;welcome variables\nSyntax: ;welcome delete\nSyntax: ;welcome test```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return

    @welcome.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def message(self, ctx, *, code=None):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")  
        embed = discord.Embed(description=f"""> {Emotes.approve} {ctx.author.mention}: set welcome message: 
        ```{code}```""", color=Colours.standard)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("INSERT INTO welcome VALUES (?, ?, ?)", (ctx.guild.id, code, None))
                await self.bot.db.commit()
                await sendmsg(self, ctx, None, embed, None, None, None, None)
            elif check is not None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("UPDATE welcome SET message = ? WHERE guild = ?", (code, ctx.guild.id))
                await self.bot.db.commit()
                await sendmsg(self, ctx, None, embed, None, None, None, None)

    @welcome.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def channel(self, ctx, channel: discord.TextChannel = None):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild") 
        embed = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: set welcome channel to {channel.mention}", color=Colours.standard)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("INSERT INTO welcome VALUES (?, ?, ?)", (ctx.guild.id, None, channel.id))
                await self.bot.db.commit()
                await sendmsg(self, ctx, None, embed, None, None, None, None)
            elif check is not None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("UPDATE welcome SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id))
                await self.bot.db.commit()
                await sendmsg(self, ctx, None, embed, None, None, None, None)

    @welcome.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def config(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild") 
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            msg = check[1] or "welcome message not set"
            chan = f"<#{check[2]}>" or "`welcome channel not set`"
            embed = discord.Embed(color=Colours.standard)
            embed.add_field(name="message", value=f"```{msg}```")
            embed.add_field(name="channel", value=f"{chan}")
            embed.set_author(name=f"welcome config {ctx.guild.name}",icon_url=ctx.guild.icon)
            await sendmsg(self, ctx, None, embed, None, None, None, None)

    @welcome.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def variables(self, ctx):
        e = discord.Embed(title="Command: welcome variables", description="use the welome variables for your welcome message/embed",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="guild variables",value="```{guild.name} - return server's name\n{guild.count} - return server's member count\n{guild.icon} - returns server's icon\n{guild.id} - returns server's id```", inline=False)
        e.add_field(name="user variables",value="```{user} - returns user full name\n{user.name} return user's username\n{user.mention} - mention user\n{user.avatar} - return user's avatar\n{user.discriminator}- return user's discriminator\n{user.joined_at} - returns the  relative time user joined the server```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return

    @welcome.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def delete(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")  
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("DELETE FROM welcome WHERE guild = {}".format(ctx.guild.id))
        await self.bot.db.commit()
        embed = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: deleted the welcome message for `{ctx.guild.name}`", color=Colours.standard)
        await sendmsg(self, ctx, None, embed, None, None, None, None)

    @welcome.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def test(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild") 
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                msg = check[1]
                chan = check[2]
                channel = self.bot.get_channel(chan)
                user = ctx.author
                guild = ctx.guild
                z = msg.replace('{user}', str(user)).replace('{user.name}', str(user.name)).replace('{user.mention}', str(user.mention)).replace('{user.avatar}', str(user.display_avatar.url)).replace('{user.joined_at}', f'<t:{int(user.created_at.timestamp())}:R>').replace('{user.discriminator}', str(user.discriminator)).replace('{guild.name}', str(guild.name)).replace('{guild.count}', str(guild.member_count)).replace('{guild.icon}', str(guild.icon)).replace('{guild.id}', str(guild.id))
                x = await to_object(z)
                await channel.send(**x)
            elif check is None:
                embed = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: welcome message isnt configured for `{ctx.guild.name}`", color=Colours.standard)
                await sendmsg(self, ctx, None, embed, None, None, None, None)

async def setup(bot) -> None:
    await bot.add_cog(welcome(bot))

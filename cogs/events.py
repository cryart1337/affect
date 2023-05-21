import discord, difflib
from discord.ext import commands
from utility import Emotes, Colours

async def noperms(self, ctx, permission):
    e = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: you are missing permission `{permission}`")
    await sendmsg(self, ctx, None, e, None, None, None, 4)

async def sendmsg(self, ctx, content, embed, view, file, allowed_mentions, delete_after):
    if ctx.guild is None:
        return
    try:
        await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=False, delete_after=delete_after)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, delete_after=delete_after)

def blacklist(): 
        async def predicate(ctx): 
            if ctx.guild is None:
             return False
            async with ctx.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(ctx.author.id))
                check = await cursor.fetchone()
                if check is not None: 
                   await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: You are blacklisted. dm <@928364018870136902> or <@1065294553659211806> for any question about your blacklist"), mention_author=False)
                return check is None
        return commands.check(predicate)   

class events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return
        if message.author.bot:
            return
        if message.content == f"<@{self.bot.user.id}>":
            prefixes = []
            for l in set(p for p in await self.bot.command_prefix(self.bot, message)):
                prefixes.append(l)
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label=f"prefixes: " + " ".join(f"{g}" for g in prefixes), url="https://discord.gg/affectbot", emoji=Emotes.link))
            await message.reply(view=view, mention_author=False)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after): 
        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): 
        if isinstance(error, commands.CommandNotFound):
            x=[cmd.name.lower() for cmd in self.bot.commands]
            cmd=ctx.message.content.split()[0].strip('#')
            used=ctx.message.content.split()[0]
            
            z=difflib.get_close_matches(cmd, x)
            if z:
                p=ctx.prefix+z[0]
                embed=discord.Embed(color=Colours.standard)
                embed.description=f'> {Emotes.warning} {ctx.author.mention}: **{used}** isnt a __**valid**__ command, did you mean `{p}`?'
                await sendmsg(self, ctx, None, embed, None, None, None, None)
        elif isinstance(error, commands.CheckFailure):
            return
        else:
            try:
                embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: {error}")
                await sendmsg(self, ctx, None, embed, None, None, None, None)
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(color=Colours.standard, description=f"Joined on **{guild.name}** (`{guild.id}`) | Owner: {guild.owner} (`{guild.owner.id}`) | Creation Date: <t:{int(guild.created_at.timestamp())}:d>")
        embed.set_footer(text=f"members: {guild.member_count}", icon_url=guild.icon)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"Guild #{len(self.bot.guilds)}", disabled=True, style=discord.ButtonStyle.green))
        await self.bot.get_channel(1105207290107277342).send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        embed = discord.Embed(color=Colours.standard, description=f"Out of **{guild.name}** (`{guild.id}`) | Owner: {guild.owner} (`{guild.owner.id}`) | Creation Date: <t:{int(guild.created_at.timestamp())}:d>")
        embed.set_footer(text=f"members: {guild.member_count}", icon_url=guild.icon)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"Guild #{len(self.bot.guilds)}", disabled=True, style=discord.ButtonStyle.red))
        await self.bot.get_channel(1105207290107277342).send(embed=embed, view=view)

async def setup(bot) -> None:
    await bot.add_cog(events(bot))
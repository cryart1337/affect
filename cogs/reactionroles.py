import discord, aiosqlite  
from discord.ext import commands 
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

class reactionrole(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 

    @commands.group()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def reactionrole(self, ctx):
        if ctx.subcommand_passed is not None:
            return
        e = discord.Embed(title="Command: reactionrole", description="give a user a role when they react to a message",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="Arguments", value="<subcommand> [roleid] [messageid] <emoji>")
        e.add_field(name="permissions", value="manage_guild", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;reactionrole add 12345678910 12345678910 :heart:\nSyntax: ;reactionrole remove 12345678910 12345678910 :heart:\nSyntax: ;reactionrole list```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return 
    
    @reactionrole.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def add(self, ctx, role_id: int, message_id: int, emoji: str):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        async with self.bot.db.cursor() as cursor:
            await cursor.execute('INSERT INTO reaction_roles (role_id, message_id, emoji) VALUES (?, ?, ?)', (role_id, message_id, emoji))
            await cursor.commit()
        message = await ctx.channel.fetch_message(message_id)
        await message.add_reaction(emoji)
        e = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: Reaction role added successfully",color=Colours.standard)
        await sendmsg(self, ctx, None, e, None, None, None, None)

    @reactionrole.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def remove(self, ctx, role: discord.Role, message: discord.Message, emoji: str):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        async with aiosqlite.connect('main.db') as db:
            result = await db.execute('SELECT * FROM reaction_roles WHERE role_id = ? AND message_id = ? AND emoji = ?', (role.id, message.id, emoji))
            row = await result.fetchone()
            if row is None:
                e = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: Invalid roleid, messageid, or emoji",color=Colours.standard)
                await ctx.send(embed=e, mention_author=False)
                return
            await db.execute('DELETE FROM reaction_roles WHERE role_id = ? AND message_id = ? AND emoji = ?', (role.id, message.id, emoji))
            await db.commit()
        await message.clear_reaction(emoji)
        e = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: Reaction role removed successfully",color=Colours.standard) 
        await sendmsg(self, ctx, None, e, None, None, None, None)

    @reactionrole.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def list(self, ctx):
        async with aiosqlite.connect('main.db') as db:
            if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
            cursor = await db.execute('SELECT role_id, message_id, emoji FROM reaction_roles')
            rows = await cursor.fetchall()
        embed = discord.Embed(title='> reaction role list', color=Colours.standard)
        for row in rows:
            role = ctx.guild.get_role(row[0])
            message = await ctx.channel.fetch_message(row[1])
            embed.add_field(name=f'{message.id} - {role.name}', value=f'React with {row[2]} to get the {role.name} role', inline=False)
        await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        async with aiosqlite.connect('main.db') as db:
            cursor = await db.execute('SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji = ?', (payload.message_id, str(payload.emoji)))
            row = await cursor.fetchone()
            if row is not None:
                guild = await self.bot.fetch_guild(payload.guild_id)
                member = await guild.fetch_member(payload.user_id)
                role = guild.get_role(row[0])
                if role is not None:
                    await member.add_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        async with aiosqlite.connect('main.db') as db:
            cursor = await db.execute('SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji = ?', (payload.message_id, str(payload.emoji)))
            row = await cursor.fetchone()
            if row is not None:
                guild = await self.bot.fetch_guild(payload.guild_id)
                member = await guild.fetch_member(payload.user_id)
                role = guild.get_role(row[0])
                if role is not None:
                    await member.remove_roles(role)

async def setup(bot) -> None: 
    await bot.add_cog(reactionrole(bot)) 
import discord
import asyncio
import aiohttp
import random
import json
import button_paginator as pg
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist


def check_whitelist():
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return
        if ctx.author.id == ctx.guild.owner.id:
            return True
        async with ctx.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
            check = await cursor.fetchone()
            if check is None:
                e = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: You are not whitelisted")
                await ctx.reply(embed=e, mention_author=False)
                return False
            return check is not None
    return commands.check(predicate)


def check_owner():
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        if ctx.author.id != ctx.guild.owner.id:
            e = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: Only the server owner can use this command")
            await ctx.reply(embed=e, mention_author=False)
            return False
        return ctx.author.id == ctx.guild.owner.id
    return commands.check(predicate)


class Antinuke(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.Member):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'ban'".format(guild.id))
            check = await cursor.fetchone()
            if check is not None:
                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                    if entry.user.top_role.position >= guild.get_member(self.bot.user.id).top_role.position:
                        return
                    await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(guild.id, entry.user.id))
                    chec = await cursor.fetchone()
                    if chec is None:
                        punishment = check[2]
                        try:
                            if punishment == "ban":
                                await entry.user.ban(reason="AntiNuke: banning people")
                            elif punishment == "kick":
                                await entry.user.kick(reason="AntiNuke: banning people")
                            elif punishment == "strip":
                                for role in entry.user.roles:
                                    if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                                        try:
                                            if role.is_bot_managed():
                                                await role.edit(permissions=discord.Permissions.none())
                                                continue
                                            else:
                                                async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                                                    async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                                                        if r.status == 429:
                                                            await asyncio.sleep(3)
                                        except:
                                            continue
                        except:
                            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'kick'".format(member.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                    if entry.user.top_role.position >= member.guild.get_member(self.bot.user.id).top_role.position:
                        return
                    await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(member.guild.id, entry.user.id))
                    chec = await cursor.fetchone()
                    if chec is None:
                        punishment = check[2]
                        try:
                            if punishment == "ban":
                                await entry.user.ban(reason="AntiNuke: kicking people")
                            elif punishment == "kick":
                                await entry.user.kick(reason="AntiNuke: kicking people")
                            elif punishment == "strip":
                                for role in entry.user.roles:
                                    if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                                        try:
                                            if role.is_bot_managed():
                                                await role.edit(permissions=discord.Permissions.none())
                                                continue
                                            else:
                                                async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                                                    async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{member.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                                                        if r.status == 429:
                                                            await asyncio.sleep(3)
                                        except:
                                            continue
                        except:
                            pass

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        if str(before.vanity_url_code) != str(after.vanity_url_code):
            if before.vanity_url_code is None:
                return
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'vanity'".format(before.id))
                check = await cursor.fetchone()
                if check is not None:
                    async for entry in before.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
                        if entry.user.top_role.position >= before.get_member(self.bot.user.id).top_role.position:
                            return
                        await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(before.id, entry.user.id))
                        chec = await cursor.fetchone()
                        if chec is None:
                            await before.edit(vanity_code=before.vanity_url_code)
                            punishment = check[2]
                            try:
                                if punishment == "ban":
                                    await entry.user.ban(reason="AntiNuke: changing vanity")
                                elif punishment == "kick":
                                    await entry.user.kick(reason="AntiNuke: changing vanity")
                                elif punishment == "strip":
                                    for role in entry.user.roles:
                                        if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                                            try:
                                                if role.is_bot_managed():
                                                    await role.edit(permissions=discord.Permissions.none())
                                                    continue
                                                else:
                                                    async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                                                        async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{before.id}/members/{entry.user.id}/roles/{role.id}") as r:
                                                            if r.status == 429:
                                                                await asyncio.sleep(3)
                                            except:
                                                continue
                            except:
                                pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, rol: discord.Role):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'roledelete'".format(rol.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                async for entry in rol.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
                    if entry.user.top_role.position >= rol.guild.get_member(self.bot.user.id).top_role.position:
                        return
                    await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(rol.guild.id, entry.user.id))
                    chec = await cursor.fetchone()
                    if chec is None:
                        punishment = check[2]
                        try:
                            if punishment == "ban":
                                await entry.user.ban(reason="AntiNuke: deleting roles")
                            elif punishment == "kick":
                                await entry.user.kick(reason="AntiNuke: deleting roles")
                            elif punishment == "strip":
                                for role in entry.user.roles:
                                    if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                                        try:
                                            if role.is_bot_managed():
                                                await role.edit(permissions=discord.Permissions.none())
                                                continue
                                            else:
                                                async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                                                    async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{role.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                                                        if r.status == 429:
                                                            await asyncio.sleep(3)
                                        except:
                                            continue
                        except:
                            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'channeldelete'".format(channel.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                    if entry.user.top_role.position >= channel.guild.get_member(self.bot.user.id).top_role.position:
                        return
                    await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(channel.guild.id, entry.user.id))
                    chec = await cursor.fetchone()
                    if chec is None:
                        punishment = check[2]
                        try:
                            if punishment == "ban":
                                await entry.user.ban(reason="AntiNuke: deleting channels")
                            elif punishment == "kick":
                                await entry.user.kick(reason="AntiNuke: deleting channels")
                            elif punishment == "strip":
                                for role in entry.user.roles:
                                    if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                                        try:
                                            if role.is_bot_managed():
                                                await role.edit(permissions=discord.Permissions.none())
                                                continue
                                            else:
                                                async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                                                    async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{channel.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                                                        if r.status == 429:
                                                            await asyncio.sleep(3)
                                        except:
                                            continue
                        except:
                            pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        if before.position >= before.guild.get_member(self.bot.user.id).top_role.position and after.position >= after.guild.get_member(self.bot.user.id).top_role.position:
            return
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'roleupdate'".format(before.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                    if entry.user.top_role.position >= before.guild.get_member(self.bot.user.id).top_role.position:
                        return
                    await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(before.guild.id, entry.user.id))
                    chec = await cursor.fetchone()
                    if chec is None:
                        if before.permissions != after.permissions:
                            await after.edit(permissions=before.permissions)
                        elif before.mentionable != after.mentionable:
                            await after.edit(mentionable=before.mentionable)
                        punishment = check[2]
                        try:
                            if punishment == "ban":
                                await entry.user.ban(reason="AntiNuke: updating roles")
                            elif punishment == "kick":
                                await entry.user.kick(reason="AntiNuke: updating roles")
                            elif punishment == "strip":
                                for role in entry.user.roles:
                                    if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                                        try:
                                            if role.is_bot_managed():
                                                await role.edit(permissions=discord.Permissions.none())
                                                continue
                                            else:
                                                async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                                                    async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{before.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                                                        if r.status == 429:
                                                            await asyncio.sleep(3)
                                        except:
                                            continue
                        except:
                            pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'antibot'".format(member.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                    if entry.user.top_role.position >= member.guild.get_member(self.bot.user.id).top_role.position:
                        return
                    if member.id == self.bot.user.id: 
                        await member.guild.ban(member, reason="AntiNuke: adding bots")
                    await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(member.guild.id, entry.user.id))
                    chec = await cursor.fetchone()
                    if chec is None:
                        punishment = check[2]
                        try:
                            if punishment == "ban":
                                await entry.user.ban(reason="AntiNuke: adding bots")
                            elif punishment == "kick":
                                await entry.user.kick(reason="AntiNuke: adding bots")
                            elif punishment == "strip":
                                for role in entry.user.roles:
                                    if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                                        try:
                                            if role.is_bot_managed():
                                                await role.edit(permissions=discord.Permissions.none())
                                                continue
                                            else:
                                                async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                                                    async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{member.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                                                        if r.status == 429:
                                                            await asyncio.sleep(3)
                                        except:
                                            continue
                        except:
                            pass 

    @commands.group(aliases=["wl"], invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_owner()
    @blacklist()
    async def whitelist(self, ctx):
        e = discord.Embed(title="Command: whitelist", description="whitelist your trusted members to prevent them being detected by the antinuke",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="Arguments", value="<subcommand> [member]")
        e.add_field(name="permissions", value="administrator", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;whitelist add @andreilord\nSyntax: ;whitelist remove @andreilord\nSyntax: ;whitelist list```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return 

    @whitelist.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def list(self, ctx):
        i = 0
        k = 1
        l = 0
        mes = ""
        number = []
        messages = []
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {}".format(ctx.guild.id))
            results = await cursor.fetchall()
            if len(results) == 0:
                e = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: there are no whitelisted members")
                return await sendmsg(self, ctx, None, e, None, None, None, None)
            for result in results:
                mes = f"{mes}`{k}` {await self.bot.fetch_user(result[1])}\n"
                k += 1
                l += 1
                if l == 10:
                    messages.append(mes)
                    number.append(discord.Embed(color=Colours.standard, title=f"whitelisted ({len(results)})", description=messages[i]))
                    i += 1
                    mes = ""
                    l = 0

            messages.append(mes)
            embed = discord.Embed(
                color=Colours.standard, title=f"whitelisted ({len(results)})", description=messages[i])
            number.append(embed)
            if len(number) > 1:
                paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
                paginator.add_button('prev', emoji='<:left:1100418278272290846>')
                paginator.add_button('next', emoji='<:right:1100418264028426270>')
                await paginator.start()
            else:
                await ctx.send(embed=embed)

    @whitelist.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_owner()
    @blacklist()
    async def add(self, ctx: commands.Context, *, member: discord.Member = None):
        if member is None:
            e = discord.Embed(title="Command: whitelist", description="whitelist your trusted members to prevent them being detected by the antinuke",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [member]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;whitelist add @andreilord\nSyntax: ;whitelist remove @andreilord\nSyntax: ;whitelist list```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        async with ctx.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
            check = await cursor.fetchone()
            if check is not None:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: This user is already whitelisted"), mention_author=False)
            await cursor.execute("INSERT INTO whitelist VALUES (?,?)", (ctx.guild.id, member.id))
            await self.bot.db.commit()
            await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Whitelisted {member.mention}"), mention_author=False)

    @whitelist.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_owner()
    @blacklist()
    async def remove(self, ctx, *, member: discord.Member):
        if member is None:
            e = discord.Embed(title="Command: whitelist", description="whitelist your trusted members to prevent them being detected by the antinuke",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [member]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;whitelist add @andreilord\nSyntax: ;whitelist remove @andreilord\nSyntax: ;whitelist list```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        async with ctx.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
            check = await cursor.fetchone()
            if check is None:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: This user is not whitelisted"), mention_author=False)
            await cursor.execute("DELETE FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
            await self.bot.db.commit()
            await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed whitelist from {member.mention}"), mention_author=False)

    @commands.group(aliases=["an"], invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def antinuke(self, ctx):
        e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
        e.add_field(name="permissions", value="administrator", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
        e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def settings(self, ctx):
        vanity = f"{Emotes.nono} (`no`)"
        ban = f"{Emotes.nono} (`no`)"
        kick = f"{Emotes.nono} (`no`)"
        channel = f"{Emotes.nono} (`no`)"
        roleupdate = f"{Emotes.nono} (`no`)"
        roledelete = f"{Emotes.nono} (`no`)"
        antibot = f"{Emotes.nono} (`no`)"
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {}".format(ctx.guild.id))
            results = await cursor.fetchall()
            for result in results:
                if result[1] == "vanity": vanity = f"{Emotes.approve} (`yes`)"
                elif result[1] == "ban": ban = f"{Emotes.approve} (`yes`)"
                elif result[1] == "kick": kick = f"{Emotes.approve} (`yes`)"
                elif result[1] == "channeldelete": channel = f"{Emotes.approve} (`yes`)"
                elif result[1] == "roleupdate": roleupdate = f"{Emotes.approve} (`yes`)"
                elif result[1] == "roledelete": roledelete = f"{Emotes.approve} (`yes`)"
                elif result[1] == "antibot": antibot = f"{Emotes.approve} (`yes`)"

            embed = discord.Embed(color=Colours.standard)
            embed.set_thumbnail(url=ctx.guild.icon or "")
            embed.add_field(name="antinuke settings",value=f"<:minus:1105930417095319622> ban - {ban}\n<:minus:1105930417095319622> kick - {kick}\n<:minus:1105930417095319622> channel delete - {channel}\n<:minus:1105930417095319622> role update - {roleupdate}\n<:minus:1105930417095319622> role delete - {roledelete}\n<:minus:1105930417095319622> anti bot - {antibot}", inline=False)
            embed.set_footer(text="For more information about this command use (;antinuke)")
            await ctx.reply(embed=embed, mention_author=False)

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def vanity(self, ctx: commands.Context, option=None, punishment=None):
        if option is None:
            e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
            e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if option.lower() == "set":
            if option is None or punishment is None:
                e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
                e.add_field(name="permissions", value="administrator", inline=True)
                e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
                e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return
            if not punishment.lower() in ["ban", "kick", "strip"]:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between ban, kick or strip"), mention_author=False)
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                check = await cursor.fetchone()
                if check is not None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti vanity update module is already configured"), mention_author=False)
                await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name, punishment))
                await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Added anti vanity update module"), mention_author=False)
        elif option.lower() == "unset":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                check = await cursor.fetchone()
                if check is None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti vanity update module is not configured"), mention_author=False)
                await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed anti vanity update module"), mention_author=False)

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def ban(self, ctx: commands.Context, option=None, punishment=None):
        if option is None:
            e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
            e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if option.lower() == "set":
            if option is None or punishment is None:
                e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
                e.add_field(name="permissions", value="administrator", inline=True)
                e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
                e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return
            if not punishment.lower() in ["ban", "kick", "strip"]:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between ban, kick or strip"), mention_author=False)
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                check = await cursor.fetchone()
                if check is not None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti ban module is already configured"), mention_author=False)
                await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name, punishment))
                await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Added anti ban module"), mention_author=False)
        elif option.lower() == "unset":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                check = await cursor.fetchone()
                if check is None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti ban is not configured"), mention_author=False)
                await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed anti vaniy module"), mention_author=False)

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def kick(self, ctx: commands.Context, option=None, punishment=None):
        if option is None:
            e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
            e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if option.lower() == "set":
            if option is None or punishment is None:
                e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
                e.add_field(name="permissions", value="administrator", inline=True)
                e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
                e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return
            if not punishment.lower() in ["ban", "kick", "strip"]:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between kick, kick or strip"), mention_author=False)
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                check = await cursor.fetchone()
                if check is not None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti kick module is already configured"), mention_author=False)
                await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name, punishment))
                await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Added anti kick module"), mention_author=False)
        elif option.lower() == "unset":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                check = await cursor.fetchone()
                if check is None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti kick is not configured"), mention_author=False)
                await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed anti vaniy module"), mention_author=False)

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def channel(self, ctx: commands.Context, option=None, punishment=None):
        if option is None:
            e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
            e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if option.lower() == "set":
            if option is None or punishment is None:
                e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
                e.add_field(name="permissions", value="administrator", inline=True)
                e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
                e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return
            if not punishment.lower() in ["ban", "kick", "strip"]:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between channel, channel or strip"), mention_author=False)
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}delete'")
                check = await cursor.fetchone()
                if check is not None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti channel delete module is already configured"), mention_author=False)
                await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name+"delete", punishment))
                await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Added anti channel delete module"), mention_author=False)
        elif option.lower() == "unset":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}delete'")
                check = await cursor.fetchone()
                if check is None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti channel delete is not configured"), mention_author=False)
                await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}delete'")
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed anti channel delete module"), mention_author=False)

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def roledelete(self, ctx: commands.Context, option=None, punishment=None):
        if option is None:
            e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
            e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if option.lower() == "set":
            if option is None or punishment is None:
                e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
                e.add_field(name="permissions", value="administrator", inline=True)
                e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
                e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return
            if not punishment.lower() in ["ban", "kick", "strip"]:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between ban, kick or strip"), mention_author=False)
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roledelete'")
                check = await cursor.fetchone()
                if check is not None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti role delete module is already configured"), mention_author=False)
                await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, "roledelete", punishment))
                await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Added anti role delete module"), mention_author=False)
        elif option.lower() == "unset":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roledelete'")
                check = await cursor.fetchone()
                if check is None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti role delete is not configured"), mention_author=False)
                await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roledelete'")
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed anti role delete module"), mention_author=False)

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def roleupdate(self, ctx: commands.Context, option=None, punishment=None):
        if option is None:
            e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
            e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if option.lower() == "set":
            if option is None or punishment is None:
                e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
                e.add_field(name="permissions", value="administrator", inline=True)
                e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
                e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return
            if not punishment.lower() in ["ban", "kick", "strip"]:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between ban, kick or strip"), mention_author=False)
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roleupdate'")
                check = await cursor.fetchone()
                if check is not None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti role update module is already configured"), mention_author=False)
                await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, "roleupdate", punishment))
                await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Added anti role update module"), mention_author=False)
        elif option.lower() == "unset":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roleupdate'")
                check = await cursor.fetchone()
                if check is None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti role update is not configured"), mention_author=False)
                await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roleupdate'")
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed anti role update module"), mention_author=False)

    @antinuke.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    @blacklist()
    async def antibot(self, ctx: commands.Context, option=None, punishment=None):
        if option is None:
            e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
            e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if option.lower() == "set":
            if option is None or punishment is None:
                e = discord.Embed(title="Command: antinuke", description="protect your server against nukes and raids",color=Colours.standard, timestamp=ctx.message.created_at)
                e.add_field(name="category", value="config")
                e.add_field(name="Arguments", value="<subcommand> [set/unset] [ban/kick/strip]")
                e.add_field(name="permissions", value="administrator", inline=True)
                e.add_field(name="Command Usage",value="```Syntax: ;antinuke settings\nSyntax: ;antinuke vanity\nSyntax: ;antinuke ban\nSyntax: ;antinuke kick\nSyntax: ;antinuke channel\nSyntax: ;antinuke roledelete\nSyntax: ;antinuke roleupdate\nSyntax: ;antinuke antibot```", inline=False)
                e.add_field(name="Punishments", value="```ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action```", inline=False)
                await sendmsg(self, ctx, None, e, None, None, None, None)
                return
            if not punishment.lower() in ["ban", "kick", "strip"]:
                return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between ban, kick or strip"), mention_author=False)
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'antibot'")
                check = await cursor.fetchone()
                if check is not None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti bot update module is already configured"), mention_author=False)
                await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, "antibot", punishment))
                await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Added anti bot update module"), mention_author=False)
        elif option.lower() == "unset":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'antibot'")
                check = await cursor.fetchone()
                if check is None:
                    return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Anti bot update is not configured"), mention_author=False)
                await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'antibot'")
                await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Removed anti bot update module"), mention_author=False)

async def setup(bot) -> None:
    await bot.add_cog(Antinuke(bot))

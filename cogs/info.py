import discord
import time
import arrow
import psutil
import aiohttp
import datetime
import random
import os
import button_paginator as pg
from discord.ext import commands
from discord import Message
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist
from typing import Union, Optional
from io import BytesIO

DISCORD_API_LINK = "https://discord.com/api/invite/"
reaction_message_author = {}
reaction_message_author_avatar = {}
reaction_message_emoji_url = {}
reaction_message_emoji_name = {}
reaction_message_id = {}
edit_message_author = {}
edit_message_content1 = {}
edit_message_content2 = {}
edit_message_author_avatar = {}
edit_message_id = {}


class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message):
        if not message.guild:
            return
        if message.author.bot:
            return
        if message.attachments:
            attachment = message.attachments[0].url
        else:
            attachment = "none"

        author = str(message.author)
        content = message.content
        avatar = message.author.display_avatar.url
        async with self.bot.db.cursor() as curso:
            await curso.execute("INSERT INTO snipe VALUES (?,?,?,?,?,?)", (message.guild.id, message.channel.id, author, content, attachment, avatar))
            await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_message_edit(self, old, new):
        if old.author.bot:
            return
        if old.content == new.content:
            return
        edit_message_author[old.channel.id] = old.author
        edit_message_author_avatar[old.channel.id] = old.author.display_avatar.url
        edit_message_content1[old.channel.id] = old.content
        edit_message_content2[new.channel.id] = new.content
        edit_message_id[old.channel.id] = new.id

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member is None:
            return
        if member.bot:
            return
        reaction_message_author[payload.channel_id] = member.name
        reaction_message_author_avatar[payload.channel_id] = member.display_avatar.url
        reaction_message_emoji_url[payload.channel_id] = payload.emoji.url
        reaction_message_emoji_name[payload.channel_id] = payload.emoji.name
        reaction_message_id[payload.channel_id] = payload.message_id

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT user FROM nodata WHERE user = ?", (before.id,))
                data = await cursor.fetchone()
                if data:
                    pass
                else:
                    if before.name == after.name:
                        return
                    else:
                        await cursor.execute("INSERT INTO oldusernamess (username, discriminator, time, user) VALUES (?, ?, ?, ?)", (before.name, before.discriminator, int(datetime.datetime.now().timestamp()), before.id,))
                        await self.bot.db.commit()
        except Exception as e:
            print(e)

    @commands.command(help="set your own prefix")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def selfprefix(self, ctx: commands.Context, prefix: str):
        if len(prefix) > 3:
            return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"{Emotes.nono} {ctx.author.mention}: The prefix is too long"), None, None, None, None)
        if prefix == None:
            e = discord.Embed(title="Command: selfprefix", description="set your own prefix",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[prefix]")
            e.add_field(name="Command Usage",
                        value="```Syntax: ;selfprefix ?```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return

        async with self.bot.db.cursor() as cursor:
            if prefix.lower() == "none":
                await cursor.execute("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id))
                check = await cursor.fetchone()
                if check is not None:
                    await cursor.execute("DELETE FROM selfprefix WHERE user_id = {}".format(ctx.author.id))
                    await self.bot.db.commit()
                    await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"{Emotes.approve} {ctx.author.mention}: removed your self prefix"), None, None, None, None)
                elif check is None:
                    await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"{Emotes.nono} {ctx.author.mention}: you don't have a self prefix"), None, None, None, None)
            else:
                await cursor.execute("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id))
                result = await cursor.fetchone()
                if result is not None:
                    sql = ("UPDATE selfprefix SET pref = ? WHERE user_id = ?")
                    val = (prefix, ctx.author.id)
                    await cursor.execute(sql, val)
                    embed = discord.Embed(
                        color=Colours.standard, description=f"{Emotes.approve} {ctx.author.mention}: self prefix changed to `{prefix}`")
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
                    await self.bot.db.commit()
                elif result is None:
                    sql = ("INSERT INTO selfprefix VALUES(?,?)")
                    val = (prefix, ctx.author.id)
                    await cursor.execute(sql, val)
                    embed = discord.Embed(
                        color=Colours.standard, description=f"{Emotes.approve} {ctx.author.mention}: self prefix changed to `{prefix}`")
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
                    await self.bot.db.commit()

    @commands.command(description="info")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def guildprefix(self, ctx: commands.Context, prefix: str):
        if len(prefix) > 3:
            return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"{Emotes.nono} {ctx.author.mention}: The prefix is too long"), None, None, None, None)
        if not ctx.author.guild_permissions.manage_guild:
            return await noperms(self, ctx, "manage_guild")
        if prefix == None:
            e = discord.Embed(title="Command: guildprefix", description="changes the guild prefix",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Permissions", value="manage_guild")
            e.add_field(name="Arguments", value="[prefix]")
            e.add_field(name="Command Usage",
                        value="```Syntax: ;guildprefix ?```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return

        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT prefix, * FROM prefixes WHERE guild_id = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                sql = ("UPDATE prefixes SET prefix = ? WHERE guild_id = ?")
                val = (prefix, ctx.guild.id)
                await cursor.execute(sql, val)
                embed = discord.Embed(
                    color=Colours.standard, description=f"{Emotes.approve} {ctx.author.mention}: guild prefix changed to `{prefix}`")
                await sendmsg(self, ctx, None, embed, None, None, None, None)
            elif check is None:
                sql = ("INSERT INTO prefixes VALUES(?,?)")
                val = (ctx.guild.id, prefix)
                await cursor.execute(sql, val)
                embed = discord.Embed(
                    color=Colours.standard, description=f"{Emotes.approve} {ctx.author.mention}: guild prefix changed to `{prefix}`")
                await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()

    @commands.command(description="info", aliases=["about", "bi"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def botinfo(self, ctx: commands.Context):
        contents = (discord.Embed(color=Colours.standard, description=f"```toml\naffect its a multipurpose bot, running on discord.py {discord.__version__}, the bot was created on 2023-04-22```\nDeveloped by <@928364018870136902> & <@1065294553659211806>\nProcessed **{len(set(self.bot.walk_commands()))}** commands\nConsuming\n・**CPU:** {psutil.cpu_percent()}%\n・**Memory Usage:** {psutil.virtual_memory().percent}%\n・**Available Memory:** {round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)}%\n"),
                    (discord.Embed(color=Colours.standard,
                     description=f"```toml\n.     Stats```\n```toml\n[users] {len(self.bot.users)}\n[guilds] {len(self.bot.guilds)}\n[channels] {sum(len(guild.channels) for guild in self.bot.guilds)}\n[shard] {ctx.guild.shard_id}/{self.bot.shard_count}```")),
                    (discord.Embed(color=Colours.standard, description=f"```toml\n.     Client```\n```toml\n[commands] {len(set(self.bot.walk_commands()))}\n[ping] {int(round(self.bot.latency * 1000) / 11)}ms\n[discord.py] {discord.__version__}\n[uptime] {str(datetime.timedelta(seconds=int(round(time.time()-self.bot.uptime))))}\n[website] affectbot.xyz```")))
        paginator = pg.Paginator(
            self.bot, contents, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji='<:left:1100418278272290846>')
        paginator.add_button('next', emoji='<:right:1100418264028426270>')
        await paginator.start()

    @commands.command(help="shows bot's latency")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def ping(self, ctx):
        await ctx.reply(f"...pong :ping_pong:`{int(round(self.bot.latency * 1000) / 11)}ms`", mention_author=False)

    @commands.command(aliases=["h"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def help(self, ctx):
        embeds = []
        embeds.append(discord.Embed(color=Colours.standard, description="").set_author(name="affect help menu", icon_url=self.bot.user.display_avatar.with_format('png')).add_field(name=f"", value="for command help do `;help [command]`", inline=False).add_field(name=f"**home**",
                      value=f"select a category in the menu to view it's commands").set_footer(text=f"{len(set(self.bot.walk_commands()))} commands | {len(self.bot.users)} users | {len(self.bot.guilds)} servers"))
        embeds.append(discord.Embed(color=Colours.standard, description="> `botinfo` | `ping` | `useravatar` | `banner` | `invite` | `selfprefix` | `guildprefix` | `spotify` | `userinfo` | `addemoji` | `addmultiple` | `removeemoji` | `emojilist` | `pastusernames` | `clearnames` | `serverinfo` | `membercount` | `afk` | `snipe` | `reactionsnipe` | `editsnipe` | `sbanner` | `sicon` | `tags` | `roles` | `boosters` | `getbotinvite` | `ben`").set_author(
            name="affect", icon_url=self.bot.user.display_avatar.with_format('png')).set_footer(text=f"info commands"))
        embeds.append(discord.Embed(color=Colours.standard, description="> `ban` | `unban` | `kick` | `createembed` | `nuke` | `slowmode` | `lock` | `unlock` | `mute` | `unmute` | `imageonly` | `purge` | `stripstaff` | `restore` | `jail` | `unjail`").set_author(
            name="affect", icon_url=self.bot.user.display_avatar.with_format('png')).set_footer(text=f"moderation commands"))
        embeds.append(discord.Embed(color=Colours.standard, description="> `reactionrole` | `chatfilter` | `autorole` | `autoresponder` | `rolemenu` | `lastfm` | `join2create` | `welcome` | `goodbye` | `whitelist` | `antinuke` | `tracker` | `joindm` | `setjail` | `unsetjail`").set_author(
            name="affect", icon_url=self.bot.user.display_avatar.with_format('png')).set_footer(text=f"config commands"))
        embeds.append(discord.Embed(color=Colours.standard, description="> `uwu` | `kiss` | `hug` | `emojify` | `morse` | `ttt`").set_author(
            name="affect", icon_url=self.bot.user.display_avatar.with_format('png')).set_footer(text=f"fun commands"))
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji='<:left:1100418278272290846>')
        paginator.add_button('next', emoji='<:right:1100418264028426270>')
        await paginator.start()

    @commands.command(aliases=["av"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def avatar(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(
            color=Colours.standard, title=f"{member.name}'s avatar", url=member.avatar.url)
        if isinstance(member, discord.Member):
            if not member.avatar:
                embed = discord.Embed(
                    color=Colours.standard, title=f"{member.name}'s avatar", url=member.display_avatar.url)
                embed.set_image(url=member.display_avatar.url)
            else:
                embed = discord.Embed(
                    color=Colours.standard, title=f"{member.name}'s avatar", url=member.avatar.url)
                embed.set_image(url=member.avatar.url)

            await sendmsg(self, ctx, None, embed, None, None, None, None)

        elif isinstance(member, discord.User):
            embed = discord.Embed(
                color=Colours.standard, title=f"{member.name}'s avatar", url=member.display_avatar.url)
            embed.set_image(url=member.display_avatar.url)
            await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def banner(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author
        user = await self.bot.fetch_user(member.id)
        if not user.banner:
            e = discord.Embed(
                color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: this user doesn't have a banner")
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return

        embed = discord.Embed(color=Colours.standard,
                              title=f"{user.name}'s banner", url=user.banner.url)
        embed.set_image(url=user.banner.url)
        await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.command(description="invite me OwO", aliases=["inv"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def invite(self, ctx):
        button = discord.ui.Button(label="invite affect", style=discord.ButtonStyle.url, url=discord.utils.oauth_url(
            client_id=self.bot.user.id, permissions=discord.Permissions.all()))
        button2 = discord.ui.Button(
            label="support", style=discord.ButtonStyle.url, url="https://discord.gg/affectbot")
        button3 = discord.ui.Button(
            label="website", style=discord.ButtonStyle.url, url="http://affectbot.xyz/")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        await sendmsg(self, ctx, None, None, view, None, None, None)

    @commands.command(description="Shows the Spotify song a user is listening to")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def spotify(self, ctx, user: discord.Member = None):
        try:
            if user == None:
                user = ctx.author
                pass
            if user.activities:
                for activity in user.activities:
                    if str(activity).lower() == "spotify":
                        embed = discord.Embed(color=Colours.standard)
                        embed.add_field(
                            name="**Song**", value=f"**[{activity.title}](https://open.spotify.com/embed/track/{activity.track_id})**", inline=True)
                        embed.add_field(
                            name="**Artist**", value=f"**[{activity.artist}](https://open.spotify.com/embed/track/{activity.track_id})**", inline=True)
                        embed.set_thumbnail(url=activity.album_cover_url)
                        embed.set_author(
                            name=ctx.message.author.name, icon_url=ctx.message.author.avatar)
                        embed.set_footer(
                            text=f"Album: {activity.album}", icon_url=activity.album_cover_url)
                        await sendmsg(self, ctx, None, embed, None, None, None, None)
                        return
            embed = discord.Embed(
                description=f"{Emotes.nono} {ctx.message.author.mention}: **{user}** is not listening to spotify", colour=Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            return
        except Exception as e:
            print(e)

    @commands.command(aliases=["ui", "whois"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def userinfo(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author

        k = 0
        for guild in self.bot.guilds:
            if guild.get_member(member.id) is not None:
                k += 1

        if isinstance(member, discord.Member):
            if str(member.status) == "online":
                status = "<:onlinebot:1104407810046955601>"
            elif str(member.status) == "dnd":
                status = "<:dndbot:1104407917140123759>"
            elif str(member.status) == "idle":
                status = "<:idlebot:1104407956558204969> "
            elif str(member.status) == "offline":
                status = "<:offlinebot:1104407869253763112>"
            embed = discord.Embed(color=Colours.standard)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=member.name,
                             icon_url=member.display_avatar.url)
            embed.add_field(
                name="joined", value=f"<t:{int(member.joined_at.timestamp())}:F>\n<t:{int(member.joined_at.timestamp())}:R>", inline=False)
            members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
            embed.add_field(name="join position", value=str(
                members.index(member) + 1), inline=False)
            if member.activity:
                activity = member.activity.name
            else:
                activity = ""

            embed.add_field(name="status", value=status +
                            " " + activity, inline=False)
            embed.add_field(
                name="registered", value=f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>", inline=False)
            if len(member.roles) > 1:
                role_string = ' '.join([r.mention for r in member.roles][1:])
                embed.add_field(name="roles [{}]".format(
                    len(member.roles) - 1), value=role_string, inline=False)
            embed.set_footer(text='ID: ' + str(member.id) +
                             f" | {k} mutual server(s)")
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            return
        elif isinstance(member, discord.User):
            e = discord.Embed(color=Colours.standard)
            e.set_author(name=f"{member}", icon_url=member.display_avatar.url)
            e.set_thumbnail(url=member.display_avatar.url)
            e.add_field(
                name="registered", value=f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>", inline=False)
            e.set_footer(text='ID: ' + str(member.id) +
                         f" | {k} mutual server(s)")
            await sendmsg(self, ctx, None, e, None, None, None, None)

    @commands.command(help="add an emoji")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def addemoji(self, ctx, emoji: Union[discord.Emoji, discord.PartialEmoji] = None, *, name=None):
        if not ctx.author.guild_permissions.manage_emojis_and_stickers:
            return await noperms(self, ctx, "manage_emojis_and_stickers")
        if emoji is None:
            e = discord.Embed(title="Command: addemoji", description="add an emoji",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[emoji] <name>")
            e.add_field(name="permissions",
                        value="manage_emojis_and_stickers", inline=True)
            e.add_field(name="Command Usage",
                        value="```Syntax: ;addemoji :affectontop: affect```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if name == None:
            name = emoji.name

        url = emoji.url
        async with aiohttp.ClientSession() as ses:
            async with ses.get(url) as r:
                try:
                    img = BytesIO(await r.read())
                    bytes = img.getvalue()
                    emoji = await ctx.guild.create_custom_emoji(image=bytes, name=name)
                    added = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: added emoji `{name}` | {emoji}")
                    await sendmsg(self, ctx, None, added, None, None, None, None)
                except discord.HTTPException as re:
                    pass

    @commands.command(help="add multiple emoji")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def addmultiple(self, ctx: commands.Context, *emoji: discord.PartialEmoji):
        if not ctx.author.guild_permissions.manage_emojis_and_stickers:
            return await noperms(self, ctx, "manage_emojis_and_stickers")
        if len(emoji) == 0:
            e = discord.Embed(title="Command: addmultiple", description="add multiple emoji",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[emojis]")
            e.add_field(name="permissions",
                        value="manage_emojis_and_stickers", inline=True)
            e.add_field(name="Command Usage",
                        value="```Syntax: ;addmultiple :affectontop: :affectontop2:```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        if len(emoji) > 20:
            emm = discord.Embed(
                description=f"> {Emotes.nono} you can only add up to 20 emojis at once", color=Colours.standard)
            return await sendmsg(self, ctx, None, emm, None, None, None, None)
        emojis = []
        for emo in emoji:
            url = emo.url
            async with aiohttp.ClientSession() as ses:
                async with ses.get(url) as r:
                    try:
                        img = BytesIO(await r.read())
                        bytes = img.getvalue()
                        emoj = await ctx.guild.create_custom_emoji(image=bytes, name=emo.name)
                        emojis.append(f"{emoj}")
                    except discord.HTTPException as re:
                        pass

        embed = discord.Embed(
            color=Colours.standard, title=f"> {Emotes.approve} added {len(emojis)} emojis")
        embed.description = "".join(map(str, emojis))
        await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.command(help="delete an emoji")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def removeemoji(self, ctx, *, emoji: discord.Emoji = None):
        if not ctx.author.guild_permissions.manage_emojis_and_stickers:
            return await noperms(self, ctx, "manage_emojis_and_stickers")
        if emoji is None:
            e = discord.Embed(title="Command: removeemoji", description="delete an emoji",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[emoji]")
            e.add_field(name="permissions",
                        value="manage_emojis_and_stickers", inline=True)
            e.add_field(name="Command Usage",
                        value="```Syntax: ;removeemoji :affectontop:```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        try:
            await emoji.delete(reason=f"emoji deleted by {ctx.author}")
            emm2 = discord.Embed(
                description=f"> {Emotes.approve} the emoji has been successfully deleted", color=Colours.standard)
            return await sendmsg(self, ctx, None, emm2, None, None, None, None)
        except Exception as e:
            emm3 = discord.Embed(
                description=f"> {Emotes.nono} unable to delete emoji", color=Colours.standard)
            return await sendmsg(self, ctx, None, emm3, None, None, None, None)

    @commands.command(help="see the list of emojis on the server")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def emojilist(self, ctx):
        i = 0
        k = 1
        l = 0
        mes = ""
        number = []
        messages = []
        for emoji in ctx.guild.emojis:
            mes = f"{mes}`{k}` {emoji} - ({emoji.name})\n"
            k += 1
            l += 1
            if l == 10:
                messages.append(mes)
                number.append(discord.Embed(
                    color=Colours.standard, title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
                i += 1
                mes = ""
                l = 0

        messages.append(mes)
        number.append(discord.Embed(color=Colours.standard,
                      title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji='<:left:1100418278272290846>')
        paginator.add_button('next', emoji='<:right:1100418264028426270>')
        await paginator.start()

    @commands.command(aliases=['names', 'usernames'])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def pastusernames(self, ctx, member: discord.User = None):
        try:
            if member == None:
                member = ctx.author
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT username, discriminator, time FROM oldusernamess WHERE user = ?", (member.id,))
                data = await cursor.fetchall()
                i = 0
                page = 1
                k = 1
                l = 0
                mes = ""
                embeds = []
                messages = []
                if data:
                    for table in data[::-1]:
                        username = table[0]
                        discrim = table[1]
                        mes = f"{mes}`{k}` {username}#{discrim} — <t:{int(table[2])}:R>\n"
                        k += 1
                        l += 1
                        if l == 10:
                            messages.append(mes)
                            i += 1
                            embeds.append(discord.Embed(color=Colours.standard, description=messages[i]).set_author(name=f"{member.name}'s past usernames", icon_url=member.avatar).set_footer(
                                text=f"{page}/{int(len(data)/10)+1 if len(data)/10 > int(len(data)/10) and int(len(data)/10) < int(len(data)/10)+1 else int(len(data)/10)} ({len(data)} entries)"))
                            page += 1
                            mes = ""
                            l = 0
                    messages.append(mes)
                    embeds.append(discord.Embed(color=Colours.standard, description=messages[i]).set_author(name=f"{member.name}'s past usernames", icon_url=member.avatar).set_footer(
                        text=f"{page}/{int(len(data)/10)+1 if len(data)/10 > int(len(data)/10) and int(len(data)/10) < int(len(data)/10)+1 else int(len(data)/10)} ({len(data)} entries)"))
                    paginator = pg.Paginator(
                        self.bot, embeds, ctx, invoker=ctx.author.id)
                    paginator.add_button(
                        'prev', emoji='<:left:1100418278272290846>')
                    paginator.add_button(
                        'next', emoji='<:right:1100418264028426270>')
                    await paginator.start()
                else:
                    emm3 = discord.Embed(
                        description=f"> {Emotes.warning} {ctx.author.mention}: no logged usernames for {member}", color=Colours.standard)
                    await sendmsg(self, ctx, None, emm3, None, None, None, None)
        except Exception as e:
            print(e)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def clearnames(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM oldusernamess WHERE user = ?", (ctx.author.id,))
            emm3 = discord.Embed(
                description=f"> {Emotes.approve} {ctx.author.mention}: all your old names have been successfully deleted", color=Colours.standard)
            await sendmsg(self, ctx, None, emm3, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @commands.command(aliases=['mc'], description="view the server's member count")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def membercount(self, ctx: commands.Context):

        total = len(ctx.guild.members)
        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = len([m for m in ctx.guild.members if m.bot])

        embed = discord.Embed(color=Colours.standard)
        embed.set_author(name=f"{ctx.guild.name}'s membercount")

        embed.add_field(name=f'Members', value=f'{total:,}', inline=True)
        embed.add_field(
            name=f'Users ({humans/total*100:.2f}%)', value=f'{humans:,}', inline=True)
        embed.add_field(
            name=f'Bots ({bots/total*100:.2f}%)', value=f'{bots:,}', inline=True)

        return await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.command(description='View information about a server')
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def serverinfo(self, ctx: commands.Context, invite: Optional[discord.Invite] = None):

        guild = ctx.guild if not invite else invite.guild

        embed = discord.Embed(color=Colours.standard, title=guild.name)
        embed.set_author(name=ctx.author.name,
                         icon_url=ctx.author.display_avatar.with_format("png"))

        view = discord.ui.View()
        owner_parts = dict()
        other_parts = dict()
        boost_parts = dict()
        member_parts = dict()
        channel_parts = dict()
        platform_parts = dict()

        dicon, icon = (str(guild.icon) == 'None',
                       'https://discord.gg/affectbot' if not guild.icon else str(guild.icon))

        dbanner, banner = (str(guild.banner) == 'None',
                           'https://discord.gg/affectbot' if not guild.banner else str(guild.banner))

        dsplash, splash = (str(guild.splash) == 'None',
                           'https://discord.gg/affectbot' if not guild.splash else str(guild.splash))

        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.url, label='icon', url=icon, disabled=dicon))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                      label='banner', url=banner, disabled=dbanner))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                      label='splash', url=splash, disabled=dsplash))

        partnered = 'PARTNERED' in guild.features
        vanity = f'.gg/{guild.vanity_url_code if guild.vanity_url_code else None}'
        created = arrow.get(guild.created_at).humanize()

        if isinstance(guild, discord.Guild):

            boost_count = guild.premium_subscription_count
            booster_count = len(guild.premium_subscribers)
            boost_tier = guild.premium_tier
            owner = guild.owner
            members = len(guild.members)
            humans = len([m for m in guild.members if not m.bot])
            bots = len([m for m in guild.members if m.bot])

            large = 'true' if guild.large else 'false'
            id = guild.id

            pc, web, phone = (
                len([m for m in guild.members if str(
                    m.desktop_status) != 'offline']),
                len([m for m in guild.members if str(m.web_status) != 'offline']),
                len([m for m in guild.members if str(m.mobile_status) != 'offline'])
            )

            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            channels = text_channels+voice_channels
            roles = len(guild.roles[1:])
            emojis = len(guild.emojis)
            verification_level = str(guild.verification_level)

            owner_parts = [
                f'{owner.mention}: {owner}',
                f'`{owner.id}`'
            ]
            boost_parts = [
                f'**level:** {boost_tier}',
                f'**boosters:** {booster_count}',
                f'**boosts:** {boost_count}'
            ]
            member_parts = [
                f'**total:** {members}',
                f'**humans:** {humans}',
                f'**bots:** {bots}'
            ]
            channel_parts = [
                f'**total:** {channels}',
                f'**text:** {text_channels}',
                f'**voice:** {voice_channels}'
            ]
            platform_parts = [
                f'**desktop:** {pc}',
                f'**web:** {web}',
                f'**mobile:** {phone}'
            ]
            other_parts = [
                f'**roles:** {roles}',
                f'**emojis:** {emojis}',
                f'**verification:** {verification_level}'
            ]

            embed.add_field(name='Owner', value='\n'.join(owner_parts))
            embed.add_field(name='Boost', value='\n'.join(boost_parts))
            embed.add_field(name='Members', value='\n'.join(member_parts))
            embed.add_field(name='Channels', value='\n'.join(channel_parts))
            embed.add_field(name='Platforms', value='\n'.join(platform_parts))
            embed.add_field(name='Other', value='\n'.join(other_parts))

            embed.description = '\n'.join(
                [f'**id:** {guild.id}', f'**created:** {created}'])

        elif isinstance(guild, discord.PartialInviteGuild):

            boost_count = guild.premium_subscription_count
            verification_level = str(guild.verification_level)

            embed.description = '\n'.join(
                [f'**id:** {guild.id}', f'**created:** {created}'])
            embed.add_field(name='Boost', value=f'**boosts:** {boost_count}')
            embed.add_field(
                name='Other',  value=f'**verification:** {verification_level}')

        if dicon is False:
            embed.set_thumbnail(url=icon)

        if guild.vanity_url_code is not None:
            embed.set_footer(text=vanity)
        return await sendmsg(self, ctx, None, embed, view, None, None, None)

    @commands.command(aliases=["s"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def snipe(self, ctx: commands.Context):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM snipe WHERE guild_id = {} AND channel_id = {}".format(ctx.guild.id, ctx.channel.id))
            chec = await cursor.fetchall()
            embeds = []
            try:
                results = chec[::-1]
                i = 0
                for check in results:
                    i += 1
                    sniped = check
                    em = discord.Embed(
                        color=Colours.standard, description=sniped[3] + f"\n[Video]({check[4]})" if ".mp4" in sniped[4] or ".mov" in sniped[4] else sniped[3])
                    em.set_author(name=sniped[2], icon_url=sniped[5])
                    em.set_footer(text="{}/{}".format(i, len(results)))
                    if check[4] != "none":
                        em.set_image(
                            url=sniped[4] if not ".mp4" in sniped[4] or not ".mov" in sniped[4] else "")
                    embeds.append(em)
                if len(embeds) == 1:
                    return await sendmsg(self, ctx, None, embeds[0], None, None, None, None)
                else:
                    paginator = pg.Paginator(
                        self.bot, embeds, ctx, invoker=ctx.author.id)
                    paginator.add_button(
                        'prev', emoji='<:left:1100418278272290846>')
                    paginator.add_button(
                        'next', emoji='<:right:1100418264028426270>')
                    await paginator.start()
            except IndexError:
                await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: there are no deleted messages in {ctx.channel.mention}"), None, None, None, None)

    @commands.command(aliases=["rs"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def reactionsnipe(self, ctx, *, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        try:
            em = discord.Embed(
                color=Colours.standard, description=f"> name emoji: **{reaction_message_emoji_name[channel.id]}** | [message link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{reaction_message_id[channel.id]})")
            em.set_author(
                name=reaction_message_author[channel.id], icon_url=reaction_message_author_avatar[channel.id])
            em.set_image(url=reaction_message_emoji_url[channel.id])
            await sendmsg(self, ctx, None, em, None, None, None, None)
        except:
            await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: there is no deleted reaction in {channel.mention}"), None, None, None, None)

    @commands.command(aliases=["es"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def editsnipe(self, ctx, *, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        try:
            em = discord.Embed(
                color=Colours.standard, description=f"> edited in {channel.mention} | [jump](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{edit_message_id[channel.id]})")
            em.set_author(
                name=edit_message_author[channel.id], icon_url=edit_message_author_avatar[channel.id])
            em.add_field(
                name="old", value=edit_message_content1[channel.id], inline=False)
            em.add_field(
                name="new", value=edit_message_content2[channel.id], inline=False)
            await sendmsg(self, ctx, None, em, None, None, None, None)
        except:
            await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: there is no edited message in {channel.mention}"), None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def sbanner(self, ctx, *, link=None):
        if link == None:
            e = discord.Embed(title="Command: sbanner", description="get a server's banner based on it's invite code",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[invite code]")
            e.add_field(name="Command Usage",
                        value="```Syntax: ;sbanner affectbot```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return

        invite_code = link
        async with aiohttp.ClientSession() as cs:
            async with cs.get(DISCORD_API_LINK + invite_code) as r:
                data = await r.json()

        try:
            format = ""
            if "a_" in data["guild"]["banner"]:
                format = ".gif"
            else:
                format = ".png"

            embed = discord.Embed(color=Colours.standard,
                                  title=data["guild"]["name"] + "'s banner")
            embed.set_image(url="https://cdn.discordapp.com/banners/" +
                            data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024")
            await sendmsg(self, ctx, None, embed, None, None, None, None)
        except:
            e = discord.Embed(
                color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** banner")
            await sendmsg(self, ctx, None, e, None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def sicon(self, ctx, *, link=None):
        if link == None:
            e = discord.Embed(title="Command: sbanner", description="get a server's icon based on it's invite code",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[invite code]")
            e.add_field(name="Command Usage",
                        value="```Syntax: ;sicon affectbot```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return

        invite_code = link
        async with aiohttp.ClientSession() as cs:
            async with cs.get(DISCORD_API_LINK + invite_code) as r:
                data = await r.json()

        try:
            format = ""
            if "a_" in data["guild"]["icon"]:
                format = ".gif"
            else:
                format = ".png"

            embed = discord.Embed(color=Colours.standard,
                                  title=data["guild"]["name"] + "'s icon")
            embed.set_image(url="https://cdn.discordapp.com/icons/" +
                            data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
            await sendmsg(self, ctx, None, embed, None, None, None, None)
        except:
            e = discord.Embed(
                color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** icon")
            await sendmsg(self, ctx, None, e, None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def boosters(self, ctx):
        embeds = []
        boosters = [m for m in ctx.guild.members if m.premium_since]
        boosters = sorted(boosters, key=lambda m: m.joined_at, reverse=True)
        if len(boosters) == 0:
            embed = discord.Embed(
                color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: This server doesn't have boosts")
            return await sendmsg(self, ctx, None, embed, None, None, None, None)
        maxpages = 0
        boosterscount = 0
        pagenum = 0
        for i in range(0, len(boosters), 10):
            maxpages += 1
        for i in range(0, len(boosters), 10):
            pagenum += 1
            embed = discord.Embed(color=Colours.standard)
            boosterslist = ""
            for booster in boosters[i:i + 10]:
                boosterscount += 1
                boosterslist += f"`{boosterscount}` {booster.mention} - <t:{int(booster.premium_since.timestamp())}:R>\n"
            embed.description = boosterslist
            embed.set_footer(
                text=f"Page {pagenum}/{maxpages} | {len(boosters)} boosters")
            embeds.append(embed)
        if len(embeds) == 1:
            await sendmsg(self, ctx, None, embeds[0], None, None, None, None)
        else:
            paginator = pg.Paginator(
                self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji='<:left:1100418278272290846>')
            paginator.add_button('next', emoji='<:right:1100418264028426270>')
            await paginator.start()

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def roles(self, ctx: commands.Context):
        i = 0
        k = 1
        l = 0
        mes = ""
        number = []
        messages = []
        for role in ctx.guild.roles:
            mes = f"{mes}`{k}` {role.mention} - <t:{int(role.created_at.timestamp())}:R> ({len(role.members)} members)\n"
            k += 1
            l += 1
            if l == 10:
                messages.append(mes)
                number.append(discord.Embed(
                    color=Colours.standard, title=f"There are ({len(ctx.guild.roles)}) roles in {ctx.guild.name}", description=messages[i]))
                i += 1
                mes = ""
                l = 0

        messages.append(mes)
        embed = discord.Embed(
            color=Colours.standard, title=f"There are ({len(ctx.guild.roles)}) roles in {ctx.guild.name}", description=messages[i])
        number.append(embed)
        if len(number) > 1:
            paginator = pg.Paginator(
                self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji='<:left:1100418278272290846>')
            paginator.add_button('next', emoji='<:right:1100418264028426270>')
            await paginator.start()
        else:
            await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def getbotinvite(self, ctx, id: discord.User = None):
        if id is None:
            e = discord.Embed(title="Command: getbotinvite", description="gets the invite link with administrator permission of a bot",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[bot_id]")
            e.add_field(name="Command Usage",
                        value="```Syntax: ;getbotinvite 1099419972024942744```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        else:
            embed = discord.Embed(
                color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: This isn't a bot")
            if not id.bot:
                return await sendmsg(self, ctx, None, embed, None, None, None, None)
            embed = discord.Embed(
                color=Colours.standard, description=f"Click **[here](https://discord.com/api/oauth2/authorize?client_id={id.id}&permissions=0&scope=bot%20applications.commands)** to invite the bot")
            await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.command(name="ben", description="utility", help="ask ben a question", usage="(question)")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def ben(self, ctx, *, question: str = None):
        if not question:
            e = discord.Embed(title="Command: ben", description="ask ben a question",
                              color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="utility")
            e.add_field(name="Arguments", value="[question]")
            e.add_field(name="Command Usage",
                        value="```Syntax: ;ben affect is good?```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        async with ctx.typing():
            video = random.choice(os.listdir("stuff"))
            await ctx.reply(file=discord.File(f"stuff/{video}"))


async def setup(bot) -> None:
    await bot.add_cog(info(bot))

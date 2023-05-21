import discord
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist
from discord.ui import Modal


class vcModal(Modal, title="rename your voice channel"):
    name = discord.ui.TextInput(label="voice channel name",placeholder="give your channel a better name",required=True,style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        try:
            await interaction.user.voice.channel.edit(name=name)
            e = discord.Embed(
                color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: voice channel renamed to **{name}**")
            await interaction.response.send_message(embed=e, ephemeral=True)
        except Exception as er:
            em = discord.Embed(
                color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: an error occured {er}")
            await interaction.response.send_message(embed=em, ephemeral=True)


class vmbuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="", emoji="<:iconio_lock:1105205535680254053>", style=discord.ButtonStyle.gray, custom_id="persistent_view:lock")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=False)
                    emb = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: locked <#{interaction.user.voice.channel.id}>")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_unluck:1105205533482438686>", style=discord.ButtonStyle.gray, custom_id="persistent_view:unlock")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=True)
                    emb = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: unlocked <#{interaction.user.voice.channel.id}>")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_eye:1105205531502727189>", style=discord.ButtonStyle.gray, custom_id="persistent_view:reveal")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=True)
                    emb = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: revealed <#{interaction.user.voice.channel.id}>")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_eyeno:1105205529342644376>", style=discord.ButtonStyle.gray, custom_id="persistent_view:hide")
    async def hide(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=False)
                    emb = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: hidden <#{interaction.user.voice.channel.id}>")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_pen:1105205527052558498>", style=discord.ButtonStyle.gray, custom_id="persistent_view:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    rename = vcModal()
                    await interaction.response.send_modal(rename)

    @discord.ui.button(label="", emoji="<:iconio_plus:1105205524196241478>", style=discord.ButtonStyle.gray, custom_id="persistent_view:increase")
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    limit = interaction.user.voice.channel.user_limit
                    if limit == 99:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: I can't increase the limit for <#{interaction.user.voice.channel.id}>")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                    res = limit + 1
                    await interaction.user.voice.channel.edit(user_limit=res)
                    emb = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention} increased <#{interaction.user.voice.channel.id}> limit to **{res}** members")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_minus:1105205522011000892>", style=discord.ButtonStyle.gray, custom_id="persistent_view:decrease")
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    limit = interaction.user.voice.channel.user_limit
                    if limit == 0:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention} i can't decrease the limit for <#{interaction.user.voice.channel.id}>")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                    res = limit - 1
                    await interaction.user.voice.channel.edit(user_limit=res)
                    emb = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: decreased <#{interaction.user.voice.channel.id}> limit to **{res}** members")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_crown:1105205519939018792>", style=discord.ButtonStyle.gray, custom_id="persistent_view:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {}".format(interaction.user.voice.channel.id))
                che = await cursor.fetchone()
                if che is not None:
                    memberid = che[0]
                    member = interaction.guild.get_member(memberid)
                    if member in interaction.user.voice.channel.members:
                        embed = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: the owner is still in the voice channel")
                        await interaction.response.send_message(embed=embed, ephemeral=True, view=None)
                    else:
                        await cursor.execute(f"UPDATE vcs SET user_id = {interaction.user.id} WHERE voice = {interaction.user.voice.channel.id}")
                        await interaction.client.db.commit()
                        embed = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: you own {interaction.user.voice.channel.mention}")
                        await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_info:1105205518055772271>", style=discord.ButtonStyle.gray, custom_id="persistent_view:info")
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {}".format(interaction.user.voice.channel.id))
                che = await cursor.fetchone()
                if che is not None:
                    memberid = che[0]
                    member = interaction.guild.get_member(memberid)
                    embed = discord.Embed(color=Colours.standard, title=interaction.user.voice.channel.name,
                                          description=f"owner: **{member}** (`{member.id}`)\ncreated: <t:{int(interaction.user.voice.channel.created_at.timestamp())}:R>\nbitrate: **{interaction.user.voice.channel.bitrate/1000}kbps**\nconnected: **{len(interaction.user.voice.channel.members)}**")
                    embed.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.display_avatar)
                    embed.set_thumbnail(url=member.display_avatar)
                    await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:iconio_trash:1105205515962814544>", style=discord.ButtonStyle.gray, custom_id="persistent_view:delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                channeid = check[1]
                voicechannel = interaction.guild.get_channel(channeid)
                category = voicechannel.category
                if interaction.user.voice is None:
                    e = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in your voice channel")
                    await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                    return
                elif interaction.user.voice is not None:
                    if interaction.user.voice.channel.category != category:
                        emb = discord.Embed(
                            color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                        return

                await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
                che = await cursor.fetchone()
                if che is None:
                    embe = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {interaction.user.mention}: you don't own this voice channel")
                    await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                    return
                elif che is not None:
                    await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(interaction.user.voice.channel.id))
                    await interaction.client.db.commit()
                    await interaction.user.voice.channel.delete()
                    embed = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.approve} {interaction.user.mention}: deleted the channel")
                    await interaction.response.send_message(embed=embed, view=None, ephemeral=True)


class VoiceMaster(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(member.guild.id))
            check = await cursor.fetchone()
            if check is not None:
                chan = check[1]
                if (after.channel is not None and before.channel is None) or (after.channel is not None and before.channel is not None):
                    if after.channel.id == int(chan) and before.channel is None:
                        channel = await member.guild.create_voice_channel(f"{member.name}'s channel", category=after.channel.category)
                        await member.move_to(channel)
                        await cursor.execute("INSERT INTO vcs VALUES (?,?)", (member.id, after.channel.id))
                        await self.bot.db.commit()
                    elif before.channel is not None and after.channel is not None:
                        await cursor.execute("SELECT * FROM vcs WHERE voice = {}".format(before.channel.id))
                        chek = await cursor.fetchone()
                        if (chek is not None) and (before.channel is not None and after.channel.id == int(chan)):
                            if before.channel.category == after.channel.category:
                                if before.channel.id == after.channel.id:
                                    return
                                await before.channel.delete()
                                await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
                                await self.bot.db.commit()
                                await member.move_to(channel=None)
                            else:
                                chane = await member.guild.create_voice_channel(f"{member.name}'s channel", category=after.channel.category)
                                await member.move_to(chane)
                                await cursor.execute("INSERT INTO vcs VALUES (?,?)", (member.id, chane.id))
                                await self.bot.db.commit()
                        elif (chek is not None) and (before.channel is not None and after.channel.id != int(chan)):
                            if before.channel.category == after.channel.category:
                                if before.channel.id == after.channel.id:
                                    return
                                await before.channel.delete()
                                await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
                                await self.bot.db.commit()
                            elif after.channel.category != before.channel.category:
                                if before.channel.id == int(chan):
                                    return
                                channel = before.channel
                                members = channel.members
                                if len(members) == 0:
                                    await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
                                    await self.bot.db.commit()
                                    await channel.delete()

                elif before.channel is not None and after.channel is None:
                    async with self.bot.db.cursor() as curs:
                        await curs.execute("SELECT * FROM vcs WHERE voice = {}".format(before.channel.id))
                        cheki = await curs.fetchone()
                        if cheki is not None:
                            channel = before.channel
                            members = channel.members
                            if len(members) == 0:
                                await curs.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
                                await self.bot.db.commit()
                                await channel.delete()

    @commands.command(aliases=["j2c"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def join2create(self, ctx: commands.Context, option=None):
        if option == None:
            e = discord.Embed(title="Command: join2create", description="set join2create module for your server",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand>")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;join2create set\nSyntax: ;join2create unset```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
        elif option == "set":
            if not ctx.author.guild_permissions.administrator: return await noperms(self, ctx, "administrator")  
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
                check = await cursor.fetchone()
                if check is not None:
                    em = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: join2create is already set")
                    await ctx.reply(embed=em, mention_author=False)
                    return
                elif check is None:
                    category = await ctx.guild.create_category("join2create")
                    overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(
                        view_channel=True, send_messages=False)}
                    em = discord.Embed(color=Colours.standard, title="Join2Create",description="<:dot:1104737094691205182> Manage your custom **Join2Create** using this interface.")
                    em.set_author(name=f"{ctx.guild.name}")
                    em.set_image(url="https://media.discordapp.net/attachments/958138873765064825/1081567123006050324/5367303.png?width=1025&height=257")
                    text = await ctx.guild.create_text_channel("panel", category=category, overwrites=overwrite)
                    vc = await ctx.guild.create_voice_channel("Join2Create", category=category)
                    await text.send(embed=em, view=vmbuttons())
                    await cursor.execute("INSERT INTO voicemaster VALUES (?,?,?)", (ctx.guild.id, vc.id, text.id))
                    await self.bot.db.commit()
                    e = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: configured the join2create interface")
                    await ctx.reply(embed=e, mention_author=False)
        elif option == "unset":
            if not ctx.author.guild_permissions.administrator: return await noperms(self, ctx, "administrator") 
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
                check = await cursor.fetchone()
                if check is None:
                    em = discord.Embed(
                        color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: Join2Create isn't set")
                    await ctx.reply(embed=em, mention_author=False)
                    return
                elif check is not None:
                    try:
                        channelid = check[1]
                        interfaceid = check[2]
                        channel2 = ctx.guild.get_channel(interfaceid)
                        channel = ctx.guild.get_channel(channelid)
                        category = channel.category
                        channels = category.channels
                        for chan in channels:
                            try:
                                await chan.delete()
                            except:
                                continue

                        await category.delete()
                        await channel2.delete()
                        await cursor.execute("DELETE FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
                        await self.bot.db.commit()
                        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Join2Create has been disabled")
                        await ctx.reply(embed=embed, mention_author=False)
                        return
                    except:

                        await cursor.execute("DELETE FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
                        await self.bot.db.commit()
                        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: Join2Create has been disabled")
                        await ctx.reply(embed=embed, mention_author=False)
        else:
            e = discord.Embed(title="Command: join2create", description="set join2create module for your server",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand>")
            e.add_field(name="permissions", value="administrator", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;join2create set\n;join2create unset```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None, None)
            return


async def setup(bot) -> None: 
    await bot.add_cog(VoiceMaster(bot))

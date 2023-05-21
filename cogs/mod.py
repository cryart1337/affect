import discord, humanfriendly, datetime, aiohttp, random, asyncio, json, button_paginator as pg
from discord.ext import commands 
from discord.ui import View, Button
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist
from utils.embedparser import to_object
from humanfriendly import format_timespan

class moderation(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
     async with self.bot.db.cursor() as cursor:
       await cursor.execute("SELECT user FROM nodata WHERE user = {}".format(member.id))
       data = await cursor.fetchone()
       if data: return
       list = []
       for role in member.roles:
        list.append(role.id)
     
       sql_as_text = json.dumps(list)
       sql = ("INSERT INTO restore VALUES(?,?,?)")
       val = (member.guild.id, member.id, sql_as_text)
       await cursor.execute(sql, val)
       await self.bot.db.commit()

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def ban(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
     if not ctx.author.guild_permissions.ban_members: return await noperms(self, ctx, "ban_members")
     if member == None:
       e = discord.Embed(title="Command: ban", description="bans member from the server",color=Colours.standard, timestamp=ctx.message.created_at)
       e.add_field(name="category", value="moderation")
       e.add_field(name="Arguments", value="[member] <reason>")
       e.add_field(name="permissions", value="ban_members", inline=True)
       e.add_field(name="Command Usage",value="```Syntax: ;ban @andreilord test```", inline=False)
       await sendmsg(self, ctx, None, e, None, None, None, None)
       return 
  
     if member == None or member == ctx.message.author:
         e = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: you cannot ban yourself")
         await sendmsg(self, ctx, None, e, None, None, None, None)   
         return
     
     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
        nope = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: you can't ban {member.mention}")
        await sendmsg(self, ctx, None, nope, None, None, None, None)  
        return
 
     if reason == None:
         reason = "No reason provided"
 
     if ctx.guild.premium_subscriber_role in member.roles:
      button1 = Button(style=discord.ButtonStyle.grey, emoji=Emotes.approve)
      button2 = Button(style=discord.ButtonStyle.grey, emoji=Emotes.nono)
      embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} are you sure you want to ban {member.mention}? they are a server booster")
      async def button1_callback(interaction: discord.Interaction):
         if interaction.user != ctx.author:
             em = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {interaction.user.mention} this is not your message")
             await interaction.response.send_message(embed=em, ephemeral=True)
             return
         
         try: 
           await member.ban(reason=f"kicked by {ctx.author} - {reason}")
           embe = discord.Embed(color=Colours.standard, description=f"> {Emotes.hammer} {member.mention} got banned | {reason}")
           await interaction.response.edit_message(embed=embe, view=None)
           try:
            banned = discord.Embed(color=Colours.standard, title="ban case", description=f"you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
            banned.set_thumbnail(url=ctx.guild.icon.url)
            banned.add_field(name="moderator", value=ctx.author)
            banned.add_field(name="reason", value=reason)
            banned.set_footer(text=f"id: {ctx.guild.id}")  
            await member.send(embed=banned)
           except:
            pass   
         except:
          no = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: i don't have enough permissions to do this")
          await interaction.response.edit_message(embed=no, mention_author=False)
      button1.callback = button1_callback
 
      async def button2_callback(interaction: discord.Interaction):
         if interaction.user != ctx.author:
             em = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {interaction.user.mention} this is not your message")
             await interaction.response.send_message(embed=em, ephemeral=True)
             return
 
         embe = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} alright you changed your mind!")
         await interaction.response.edit_message(embed=embe, view=None)
 
      button2.callback = button2_callback
 
      view = View()
      view.add_item(button1)
      view.add_item(button2)
      await sendmsg(self, ctx, None, embed, view, None, None)       
 
     else:    
      try: 
       await member.ban(reason=f"banned by {ctx.author} - {reason}")
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.hammer} {member.mention} got banned | {reason}")
       await sendmsg(self, ctx, None, embed, None, None, None, None) 
       try: 
          banned = discord.Embed(color=Colours.standard, title="ban case", description=f"you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
          banned.set_thumbnail(url=ctx.guild.icon.url)
          banned.add_field(name="moderator", value=ctx.author)
          banned.add_field(name="reason", value=reason)
          banned.set_footer(text=f"id: {ctx.guild.id}")   
          await member.send(embed=banned)
       except: 
          pass 
      except:
         no = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: i don't have enough permissions to do this")
         await sendmsg(self, ctx, None, no, None, None, None, None)
 
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def unban(self, ctx: commands.Context, *, member: discord.User=None):
     if not ctx.author.guild_permissions.ban_members: return await noperms(self, ctx, "ban_members")   
     if member == None:
       e = discord.Embed(title="Command: unban", description="unbans member from server",color=Colours.standard, timestamp=ctx.message.created_at)
       e.add_field(name="category", value="moderation")
       e.add_field(name="Arguments", value="[member]")
       e.add_field(name="permissions", value="ban_members", inline=True)
       e.add_field(name="Command Usage",value="```Syntax: ;unban @andreilord```", inline=False)
       await sendmsg(self, ctx, None, e, None, None, None, None)
       return 
   
     try: 
      guild = ctx.guild
      embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {member} has been unbanned")
      await guild.unban(user=member)
      await ctx.reply(embed=embed, mention_author=False)
     except:
        emb = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: couldn't unban this member")
        await sendmsg(self, ctx, None, emb, None, None, None, None) 
    
    @commands.command(aliases=["ce"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def createembed(self, ctx, *, code: str=None):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        if not code:
            e = discord.Embed(description=f"> {Emotes.nono} please provide embed code [here](http://affectbot.xyz/embed.html)",color=Colours.standard)
            return await sendmsg(self, ctx, None, e, None, None, None, None)
        e = await to_object(code)
        await ctx.send(**e)
 
    @commands.command(help=f"deletes the channel and clones it")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def nuke(self, ctx):
        if not ctx.author.guild_permissions.manage_channels: return await noperms(self, ctx, "manage_channels")
        invoker = ctx.author.id
        channel = ctx.channel   
        class disabledbuttons(discord.ui.View):
            @discord.ui.button(style=discord.ButtonStyle.grey,disabled=True,emoji=Emotes.approve,)
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button):   
                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(name=interaction.channel.name,reason=f"original channel nuked by {invoker}",)
                ch = await interaction.guild.fetch_channel(ch.id)
                e = discord.Embed(description=f"> {Emotes.approve} <@{invoker}>: channel has been nuked successfully", color=Colours.standard)
                await ch.send(embed=e)   
            @discord.ui.button(style=discord.ButtonStyle.grey,disabled=True,emoji=Emotes.nono,)
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button):
                embed = discord.Embed(description=f"> {Emotes.warning} Are you sure you want to nuke this channel?\n> {Emotes.warning} It will remove all webhooks and invites.", color=Colours.standard)
                await interaction.response.edit_message(content=None, embed=embed, view=None)
                embed = discord.Embed(description=f"> {Emotes.approve} <@{interaction.user.id}>: channel nuke has been cancelled", color=Colours.standard)
                await interaction.channel.send(embed=embed)   
        class buttons(discord.ui.View):
            @discord.ui.button(style=discord.ButtonStyle.grey, emoji=Emotes.approve)
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button):   
                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(name=interaction.channel.name,reason=f"original channel nuked by {invoker}",)
                ch = await interaction.guild.fetch_channel(ch.id)
                e = discord.Embed(description=f"> {Emotes.approve} <@{invoker}>: channel has been nuked successfully", color=Colours.standard)
                await ch.send(embed=e)  
            @discord.ui.button(style=discord.ButtonStyle.grey, emoji=Emotes.nono)
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button):
                embed = discord.Embed(description=f"> {Emotes.warning} Are you sure you want to nuke this channel?\n> {Emotes.warning} It will remove all webhooks and invites.", color=Colours.standard)
                await interaction.response.edit_message(content=None, embed=embed, view=disabledbuttons())
                embed = discord.Embed(description=f"> {Emotes.approve} <@{interaction.user.id}>: channel nuke has been cancelled", color=Colours.standard)
                await interaction.channel.send(embed=embed)
        embed = discord.Embed(description=f"> {Emotes.warning} Are you sure you want to nuke this channel?\n> {Emotes.warning} It will remove all webhooks and invites.", color=Colours.standard)
        await sendmsg(self, ctx, None, embed, buttons(), None, None)
 
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def kick(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
     if not ctx.author.guild_permissions.kick_members: return await noperms(self, ctx, "kick_members")  
     if member == None:
       e = discord.Embed(title="Command: kick", description="kicks member from server",color=Colours.standard, timestamp=ctx.message.created_at)
       e.add_field(name="category", value="moderation")
       e.add_field(name="Arguments", value="[member] <reason>")
       e.add_field(name="permissions", value="kick_members", inline=True)
       e.add_field(name="Command Usage",value="```Syntax: ;kick @andreilord test```", inline=False)
       await sendmsg(self, ctx, None, e, None, None, None, None)
       return 
 
     if member == ctx.author:
      e = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: you can't kick yourserlf")
      await sendmsg(self, ctx, None, e, None, None, None, None)
      return
 
     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
        nope = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: you can't kick {member.mention}")
        await sendmsg(self, ctx, None, nope, None, None, None, None)
        return   
  
     if reason == None:
         reason = "No reason provided"
 
     if ctx.guild.premium_subscriber_role in member.roles:
      button1 = Button(style=discord.ButtonStyle.grey, emoji=Emotes.approve)
      button2 = Button(style=discord.ButtonStyle.grey, emoji=Emotes.nono)
      embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} are you sure you want to kick {member.mention}? they are a server booster")
      async def button1_callback(interaction: discord.Interaction):
         if interaction.user != ctx.author:
             em = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {interaction.user.mention} this is not your message")
             await interaction.response.send_message(embed=em, ephemeral=True)
             return
         
         try: 
           await member.kick(reason=f"kicked by {ctx.author} - {reason}")
           embe = discord.Embed(color=Colours.standard, description=f"> {Emotes.hammer} {member.mention} got kicked | {reason}")
           await interaction.response.edit_message(embed=embe, view=None)
           try:
            banned = discord.Embed(color=Colours.standard, title="kick case", description=f"you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
            banned.set_thumbnail(url=ctx.guild.icon.url)
            banned.add_field(name="moderator", value=ctx.author)
            banned.add_field(name="reason", value=reason)
            banned.set_footer(text=f"id: {ctx.guild.id}")  
            await member.send(embed=banned)
           except:
            print('cant dm')    
         except:
          no = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: i don't have enough permissions to do this")
          await interaction.response.edit_message(embed=no, mention_author=False)
      button1.callback = button1_callback
 
      async def button2_callback(interaction: discord.Interaction):
         if interaction.user != ctx.author:
             em = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {interaction.user.mention} this is not your message")
             await interaction.response.send_message(embed=em, ephemeral=True)
             return
 
         embe = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} alright you changed your mind!")
         await interaction.response.edit_message(embed=embe, view=None)
         
 
      button2.callback = button2_callback
 
      view = View()
      view.add_item(button1)
      view.add_item(button2)
      await sendmsg(self, ctx, None, embed, view, None, None)        
 
     else:
      try: 
       await member.kick(reason=f"kicked by {ctx.author} - {reason}")
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.hammer} {member.mention} got kicked | {reason}")
       await sendmsg(self, ctx, None, embed, None, None, None, None)
       try:
            banned = discord.Embed(color=Colours.standard, title="kick case", description=f"you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
            banned.set_thumbnail(url=ctx.guild.icon.url)
            banned.add_field(name="moderator", value=ctx.author)
            banned.add_field(name="reason", value=reason)
            banned.set_footer(text=f"id: {ctx.guild.id}")  
            await member.send(embed=banned)
       except:
            pass   
      except:
         no = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: i don't have enough permissions to do this")
         await sendmsg(self, ctx, None, no, None, None, None, None)      

    @commands.command(help="add slowmode to a channel")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def slowmode(self, ctx, seconds: int=None, channel: discord.TextChannel=None):
     if not ctx.author.guild_permissions.manage_channels: return await noperms(self, ctx, "manage_channels")  
 
     chan = channel or ctx.channel
     await chan.edit(slowmode_delay=seconds)
     em = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: set slowmode time for {chan.mention} to **{seconds} seconds**")
     await sendmsg(self, ctx, None, em, None, None, None, None)

    @commands.command(help="lock a channel")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def lock(self, ctx, channel : discord.TextChannel=None):
     if not ctx.author.guild_permissions.manage_channels: return await noperms(self, ctx, "manage_channels") 

     channel = channel or ctx.channel
     overwrite = channel.overwrites_for(ctx.guild.default_role)
     overwrite.send_messages = False
     await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
     e = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} locked {channel.mention}")
     await sendmsg(self, ctx, None, e, None, None, None, None)
 
    @commands.command(help="unlock a channel")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def unlock(self, ctx, channel : discord.TextChannel=None):
     if not ctx.author.guild_permissions.manage_channels: return await noperms(self, ctx, "manage_channels") 
 
     channel = channel or ctx.channel
     overwrite = channel.overwrites_for(ctx.guild.default_role)
     overwrite.send_messages = True
     await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
     e = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} unlocked {channel.mention}")
     await sendmsg(self, ctx, None, e, None, None, None, None)

    @commands.command(help="mute a member")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def mute(self, ctx: commands.Context, member: discord.Member=None, time=None, *, reason=None):
     if not ctx.author.guild_permissions.moderate_members: return await noperms(self, ctx, "moderate_members") 

     if member == None or time==None:
        e = discord.Embed(title="Command: mute", description="mute a member",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="moderation")
        e.add_field(name="Arguments", value="[member] [time] [reason]")
        e.add_field(name="permissions", value="moderate_members", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;mute @andreilord 10 test```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return
 
     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
         no = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} you can't timeout {member.mention}")
         await sendmsg(self, ctx, None, no, None, None, None, None)
         return
   
     if reason == None:
         reason = "No reason provided"
 
     try:
      time = humanfriendly.parse_timespan(time)
      await member.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=time), reason=reason)
      e = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {member.mention}: has been muted for {format_timespan(time)} | {reason}")
      await sendmsg(self, ctx, None, e, None, None, None, None)
     except:
       emb = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} i can't mute this member")  
       await sendmsg(self, ctx, None, emb, None, None, None, None)        
  
    @commands.command(help="unmute a member")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def unmute(self, ctx, member: discord.Member=None):
     if not ctx.author.guild_permissions.moderate_members: return await noperms(self, ctx, "moderate_members")      
     try: 
      if member == None:
        e = discord.Embed(title="Command: unmute", description="unmute a member",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="moderation")
        e.add_field(name="Arguments", value="[member]")
        e.add_field(name="permissions", value="moderate_members", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;unmute @andreilord```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return
 
      await member.timeout(None, reason=f'unmuted by {ctx.author}')
      e = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: unmuted {member.mention}")
      await sendmsg(self, ctx, None, e, None, None, None, None)
     except:
       emb = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} i can't unmute this member")  
       await sendmsg(self, ctx, None, emb, None, None, None, None) 

    @commands.command(help="bulk delete messages", description="moderation", usage="[amount] <member>")
    @commands.cooldown(1, 2, commands.BucketType.guild)  
    @blacklist()
    async def purge(self, ctx: commands.Context, amount: int=None, *, member: discord.Member=None):
     if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages") 
     if amount is None:
        e = discord.Embed(title="Command: purge", description="bulk delete messages",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="moderation")
        e.add_field(name="Arguments", value="[amount] <member>")
        e.add_field(name="permissions", value="manage_messages", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;purge 50\nSyntax: ;purge @andreilord 50```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return
 
     if member is None:
       await ctx.message.delete()
       await ctx.channel.purge(limit=amount)  
       e = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: purged `{amount}` messages",color=Colours.standard)
       await sendmsg(self, ctx, None, e, None, None, None, 2)
     elif member is not None:
       await ctx.message.delete()
       msg = []
       async for message in ctx.channel.history():
         if len(msg) == amount+1:
             break 
         else:
            if message.author == member: 
              msg.append(message)
 
       await ctx.channel.delete_messages(msg) 
       e = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: purged `{amount}` messages from {member}",color=Colours.standard)
       await sendmsg(self, ctx, None, e, None, None, None, 2)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def stripstaff(self, ctx: commands.Context, member: discord.Member=None):
     if not ctx.author.guild_permissions.administrator: return await noperms(self, ctx, "administrator")
     if member == None:
        e = discord.Embed(title="Command: stripstaff", description="removes all staff roles from a member",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="moderation")
        e.add_field(name="Arguments", value="[member]")
        e.add_field(name="permissions", value="administrator", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;stripstaff @andreilord```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return
     else:
      if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
        nope = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: you can't strip {member.mention}'s roles")
        await sendmsg(self, ctx, None, nope, None, None, None, None)
        return
      async with ctx.channel.typing():  
       for role in member.roles:
         if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
           try:
             async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
               async with cs.delete(f"https://discord.com/api/v{random.randint(6,7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                 if r.status == 429:
                   await asyncio.sleep(1)
           except:
             continue
 
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: removed staff roles from {member.mention}")        
       await sendmsg(self, ctx, None, embed, None, None, None, None)


    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def restore(self, ctx: commands.Context, *, member: discord.Member=None):
     if not ctx.author.guild_permissions.administrator: return await noperms(self, ctx, "administrator")
     if member == None:
        e = discord.Embed(title="Command: restore", description="restore member's roles",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="moderation")
        e.add_field(name="Arguments", value="[member]")
        e.add_field(name="permissions", value="administrator", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;restore @andreilord```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return
     async with self.bot.db.cursor() as cursor:
       if member == ctx.author:
        return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: you can't restore your own roles"), None, None, None, None)
 
       await cursor.execute(f"SELECT * FROM restore WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")   
       result = await cursor.fetchone()
       if result is None:
         await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention} there are no roles saved for {member.mention}"), None, None, None, None)
         return 
 
       succeed = ""
       failed = "" 
       to_dump = json.loads(result[2])
       for roleid in to_dump: 
            try: 
             role = ctx.guild.get_role(roleid)
             if role.name == "@everyone":
               continue
             await member.add_roles(role)  
             succeed = f"{succeed} {role.mention}"
            except: 
             failed = f"{failed} <@&{roleid}>"
     
       if len(succeed) == 0:
         added = "none"
       else:
         added = succeed  
 
       if len(failed) == 0:
         fail = "none"
       else:
         fail = failed
 
       await cursor.execute(f"DELETE FROM restore WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
       await self.bot.db.commit()
       embed = discord.Embed(color=Colours.standard, title="roles restored", description=f"target: {member.mention}")
       embed.set_thumbnail(url=member.display_avatar.url)
       embed.add_field(name=f"{Emotes.approve} added", value=added, inline=False)
       embed.add_field(name=f"{Emotes.nono} failed", value=fail, inline=False)
       await sendmsg(self, ctx, None, embed, None, None, None, None)

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def warn(self, ctx): 
     e = discord.Embed(title="Command: warn", description="warn members in your server",color=Colours.standard, timestamp=ctx.message.created_at)
     e.add_field(name="category", value="moderation")
     e.add_field(name="Arguments", value="<subcommand> [member] <reason>")
     e.add_field(name="permissions", value="manage_messages", inline=True)
     e.add_field(name="Command Usage",value="```Syntax: ;warn add @andreilord\nSyntax: ;warn remove @andreilord\nSyntax: ;warn list```", inline=False)
     await sendmsg(self, ctx, None, e, None, None, None, None)
     return

    @warn.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def add(self, ctx: commands.Context, member: discord.Member=None, *, reason: str=None): 
     if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
     if member is None: 
        e = discord.Embed(title="Command: warn", description="warn members in your server",color=Colours.standard, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="moderation")
        e.add_field(name="Arguments", value="<subcommand> [member] <reason>")
        e.add_field(name="permissions", value="manage_messages", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;warn add @andreilord test\nSyntax: ;warn remove @andreilord\nSyntax: ;warn list```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return
     if reason is None: reason = ""
     async with self.bot.db.cursor() as cursor:
       date = datetime.datetime.now()
       await cursor.execute("INSERT INTO warns VALUES (?,?,?,?)", (ctx.guild.id, member.id, ctx.author.id, reason))
       r = '- {}'.format(reason) if reason != "" else reason
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author}: warned {member.mention} {r}")
       await sendmsg(self, ctx, None, embed, None, None, None, None)

    @warn.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def remove(self, ctx: commands.Context, *, member: discord.Member=None): 
     if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
     if member is None: 
      e = discord.Embed(title="Command: warn", description="warn members in your server",color=Colours.standard, timestamp=ctx.message.created_at)
      e.add_field(name="category", value="moderation")
      e.add_field(name="Arguments", value="<subcommand> [member] <reason>")
      e.add_field(name="permissions", value="manage_messages", inline=True)
      e.add_field(name="Command Usage",value="```Syntax: ;warn add @andreilord test\nSyntax: ;warn remove @andreilord\nSyntax: ;warn list```", inline=False)
      await sendmsg(self, ctx, None, e, None, None, None, None)
      return
     async with self.bot.db.cursor() as cursor:
       await cursor.execute("SELECT * FROM warns WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))  
       check = await cursor.fetchall() 
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: this user has no warnings")
       await sendmsg(self, ctx, None, embed, None, None, None, None) 
       if check is None: return 
       await cursor.execute("DELETE FROM warns WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
       await self.bot.db.commit()
       embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author}: removed all {member.mention}'s warns")
       await sendmsg(self, ctx, None, embed, None, None, None, None)

    @warn.command() 
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def list(self, ctx: commands.Context, *, member: discord.Member): 
     if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
     if member is None: 
      e = discord.Embed(title="Command: warn", description="warn members in your server",color=Colours.standard, timestamp=ctx.message.created_at)
      e.add_field(name="category", value="moderation")
      e.add_field(name="Arguments", value="<subcommand> [member] <reason>")
      e.add_field(name="permissions", value="manage_messages", inline=True)
      e.add_field(name="Command Usage",value="```Syntax: ;warn add @andreilord test\nSyntax: ;warn remove @andreilord\nSyntax: ;warn list @andreilord```", inline=False)
      await sendmsg(self, ctx, None, e, None, None, None, None)
      return
     async with self.bot.db.cursor() as cursor:
       await cursor.execute("SELECT * FROM warns WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))  
       check = await cursor.fetchall()  
       if check is None: return await ctx.reply(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: this user has no warnings"), mention_author=False)
       i=0
       k=1
       l=0
       mes = ""
       number = []
       messages = []
       for result in check:
               mes = f"{mes}`{k}` by **{await self.bot.fetch_user(result[2])}** - {result[3]}\n"
               k+=1
               l+=1
               if l == 10:
                messages.append(mes)
                number.append(discord.Embed(color=Colours.standard, title=f"warns ({len(check)})", description=messages[i]))
                i+=1
                mes = ""
                l=0
     
     messages.append(mes)
     embed = discord.Embed(color=Colours.standard, title=f"warns ({len(check)})", description=messages[i])
     number.append(embed)
     if len(number) > 1:
      paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
      paginator.add_button('prev', emoji='<:left:1100418278272290846>')
      paginator.add_button('next', emoji='<:right:1100418264028426270>')
      await paginator.start()
     else:
      await ctx.send(embed=embed) 

    @commands.command(aliases=["setnick", "nick"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def nickname(self, ctx, member: discord.Member=None, *, nick=None):
     if not ctx.author.guild_permissions.manage_nicknames: return await noperms(self, ctx, "manage_nicknames") 
     if member == None:
      e = discord.Embed(title="Command: nickname", description="change an user's nickname",color=Colours.standard, timestamp=ctx.message.created_at)
      e.add_field(name="category", value="moderation")
      e.add_field(name="Arguments", value="[member] <nickname>")
      e.add_field(name="permissions", value="manage_messages", inline=True)
      e.add_field(name="Command Usage",value="```Syntax: ;nickname @andreilord boss```", inline=False)
      await sendmsg(self, ctx, None, e, None, None, None, None)
      return
 
     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
         e = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: can't change nickname to members with higher roles than yours")
         await sendmsg(self, ctx, None, e, None, None, None, None)
         return
 
     if nick == None or nick.lower() == "none":
        await member.edit(nick=None)
        embe = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: nickname cleared for {member.mention}")
        await sendmsg(self, ctx, None, embe, None, None, None, None)
        return
 
     try: 
      await member.edit(nick=nick)
      embe = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: changed {member.mention} nickname")
      await sendmsg(self, ctx, None, embe, None, None, None, None)
     except Exception as e:
        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: error occured while changing nickname - {e}")
        await sendmsg(self, ctx, None, embed, None, None, None, None)

async def setup(bot) -> None: 
    await bot.add_cog(moderation(bot))  
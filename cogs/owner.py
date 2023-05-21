import discord, button_paginator as pg
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg

class owner(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
       self.bot = bot           

   @commands.command(aliases=["guilds"])
   async def servers(self, ctx):
            if not ctx.author.id in self.bot.owner_ids: return 
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for guild in self.bot.guilds:
              mes = f"{mes}`{k}` {guild.name} ({guild.id}) - ({guild.member_count})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=Colours.standard, title=f"guilds ({len(self.bot.guilds)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            number.append(discord.Embed(color=Colours.standard, title=f"guilds ({len(self.bot.guilds)})", description=messages[i]))
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji='<:left:1100418278272290846>')
            paginator.add_button('next', emoji='<:right:1100418264028426270>') 
            await paginator.start()    

   @commands.command()
   async def unblacklist(self, ctx, *, member: discord.User=None): 
    if not ctx.author.id in self.bot.owner_ids: return
    if member is None: return
    async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(member.id)) 
      check = await cursor.fetchone()
      if check is None: return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"{Emotes.warning} {ctx.author.mention}: {member.mention} is not blacklisted"), None, None, None, None)
      await cursor.execute("DELETE FROM nodata WHERE user = {}".format(member.id))
      await self.bot.db.commit()
      await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: {member.mention} can use the bot"), None, None, None, None)

   @commands.command()
   async def blacklist(self, ctx, *, member: discord.User=None): 
    if not ctx.author.id in self.bot.owner_ids: return
    if member is None: return
    async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(member.id)) 
      check = await cursor.fetchone()
      if check is not None: return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: {member.mention} is already blacklisted"), None, None, None, None)
      await cursor.execute("INSERT INTO nodata VALUES (?)", (member.id,))
      await self.bot.db.commit()
      await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: {member.mention} can no longer use the bot"), None, None, None, None)     

   @commands.command()
   async def leaveguild(self, ctx, id: int = None):
       if not ctx.author.id in self.bot.owner_ids: return
       if id is None:
           return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: no guild id found"), None, None, None, 3)     
       guild = self.bot.get_guild(id)
       if guild is None:
           return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: no guild with this id"), None, None, None, 3)    
       await guild.leave()
       return await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: left {guild.name}"), None, None, None, 3)    

   @commands.command()
   async def portal(self, ctx, guildid: int = None):
       if not ctx.author.id in self.bot.owner_ids: return 
       if guildid == None:
          await sendmsg(self, ctx, None, discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: you didnt specifiy a guild id"), None, None, None, 3) 
       else:
           await ctx.message.delete()
           guild = self.bot.get_guild(guildid)
           for c in guild.text_channels:
               if c.permissions_for(guild.me).create_instant_invite:
                   invite = await c.create_invite()
                   await ctx.author.send(f"{guild.name} invite link - {invite}")
                   break
                
async def setup(bot) -> None:
    await bot.add_cog(owner(bot))      
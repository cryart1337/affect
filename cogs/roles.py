
import discord, typing, aiohttp, asyncio, random
from discord import Embed
from discord.ext import commands 
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist
from typing import Union
from io import BytesIO

class roles(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def rolemenu(self, ctx):
       e = discord.Embed(title="Command: role", description="manage roles on your server",color=Colours.standard, timestamp=ctx.message.created_at)
       e.add_field(name="category", value="config")
       e.add_field(name="Arguments", value="[subcommand] [target] [other]")
       e.add_field(name="permissions", value="manage_roles", inline=True)
       e.add_field(name="Command Usage",value="```Syntax: ;rolemenu create test\nSyntax: ;rolemenu delete test\nSyntax: ;rolemenu give @andreilord test\nSyntax: ;rolemenu giveall @test\nSyntax: ;rolemenu removeall @test\nSyntax: ;rolemenu remove @andreilord test\nSyntax: ;rolemenu rename test test1\nSyntax: ;rolemenu color test #fffff\nSyntax: ;rolemenu info test\nSyntax: ;rolemenu icon :affectontop: @test```", inline=False)
       await sendmsg(self, ctx, None, e, None, None, None, None)
       return

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def create(self, ctx, *, role_name: str):
        if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
        guild = ctx.guild
        existing_role = discord.utils.get(guild.roles, name=role_name)
        if existing_role:
            embed = discord.Embed(description = f"> {Emotes.warning} {ctx.author.mention}: A role with the name **{role_name}** already exists.",color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            return
        await guild.create_role(name=role_name)
        embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: A role with the name **{role_name}** has been made.",color = Colours.standard)
        await sendmsg(self, ctx, None, embed, None, None, None, None)
 

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def delete(self, ctx, *, role_name: str):
        if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await role.delete()
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: A role with the name *{role_name}* has been deleted.",color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
        else:
            embed = discord.Embed(description = f"> {Emotes.warning} {ctx.author.mention}: A role with the name *{role_name}* has not been found.",color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def give(self, ctx, member: discord.Member, *, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
        if role in member.roles:
            embed = discord.Embed(description = f"> {Emotes.warning} {ctx.author.mention}: member already has role {role.mention}",color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
        else:
            await member.add_roles(role)
        embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: {member.mention} has recieved the role {role.mention}.",color = Colours.standard)
        await sendmsg(self, ctx, None, embed, None, None, None, None)

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def remove(self, ctx, member: discord.Member, *, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
        if role in member.roles:
            await member.remove_roles(role)
        embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: {member.mention} has lost the role {role.mention}.",color = Colours.standard)
        await sendmsg(self, ctx, None, embed, None, None, None, None)


    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def rename(self, ctx,  role: discord.Role, new_name: str):
            if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
            await role.edit(name=new_name)
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: {role.mention} has been renamed to {new_name}.",color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)  

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def color(self, ctx: commands.Context, role: discord.Role, colour: discord.Colour):
        if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role.name)
        if not role:            
             return
        try:
            await role.edit(color=colour, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
        except discord.HTTPException:
                    embed = discord.Embed(description=f"> {Emotes.warning} {ctx.author.mention}: I do not have permissions to change the role color of **`{role.mention}`**")
                    await sendmsg(self, ctx, None, embed, None, None, None, None)		
        else:
                    embed = discord.Embed(description=f"> {Emotes.approve} {ctx.author.mention}: changed {role.mention}'s color to **`{colour}`**")
                    await sendmsg(self, ctx, None, embed, None, None, None, None)


    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def info(self, ctx, role: typing.Union[ discord.Role, str]):
        if isinstance(role, discord.Role):
            role=role
            perms = []
            content = discord.Embed(title=f"@{role.name} | #{role.id}")
            content.colour = role.color
            if isinstance(role.icon, discord.Asset):
                content.set_thumbnail(url=role.display_icon)
            elif isinstance(role.icon, str):
                content.title = f"{role.icon} @{role.name} | #{role.id}"
            for perm, allow in iter(role.permissions):
                if allow:
                    perms.append(f"`{perm.upper()}`")
            if role.managed:
                if role.tags.is_bot_managed():
                    manager = ctx.guild.get_member(role.tags.bot_id)
                elif role.tags.is_integration():
                    manager = ctx.guild.get_member(role.tags.integration_id)
                elif role.tags.is_premium_subscriber():
                    manager = "Server boosting"
                else:
                    manager = "UNKNOWN"
            content.add_field(name="Hex Code", value=str(role.color).upper())
            content.add_field(name="Member", value=len(role.members))
            content.add_field(name="Created", value=discord.utils.format_dt(role.created_at, style="R"))
            content.add_field(name="Hoisted", value=str(role.hoist))
            content.add_field(name="Mentionable", value=role.mentionable)
            content.add_field(name="Mention", value=role.mention)
        await sendmsg(self, ctx, None, content, None, None, None, None)

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def icon(self, ctx: commands.Context, emoji: Union[discord.PartialEmoji, str]=None, *, role: discord.Role=None):
      botuser = ctx.guild.get_member(self.bot.user.id)  
      if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
      if ctx.guild.premium_tier < 2:
        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: the server needs to have at least 7 boosts to change role icons")
        await sendmsg(self, ctx, None, embed, None, None, None, None)
        return   
      if role == None or emoji==None:
        embed = discord.Embed(description = f"> {Emotes.warning} {ctx.author.mention}: ;rolemenu icon :affectontop: @test",color = Colours.standard)
        await sendmsg(self, ctx, None, embed, None, None, None, None)
        return
      if role.position >= botuser.top_role.position:
        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: i can't edit a role that's higher than mine")
        await sendmsg(self, ctx, None, embed, None, None, None, None)
        return    
      if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner.id:
        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: i can't edit a role that's higher than yours")
        await sendmsg(self, ctx, None, embed, None, None, None, None)
        return     
      if isinstance(emoji, discord.PartialEmoji):  
       url = emoji.url  
       async with aiohttp.ClientSession() as ses: 
        async with ses.get(url) as r:
         try:
            if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await role.edit(display_icon=bytes, reason=f"role icon changed by {ctx.author}")
                embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: changed role icon for {role.mention}")
                await sendmsg(self, ctx, None, embed, None, None, None, None)
                return
         except discord.HTTPException:
            embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: i was unable to change the role icon")
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            return
      elif isinstance(emoji, str):      
        ordinal = ord(emoji)
        async with aiohttp.ClientSession() as cs:
          async with cs.get(f"https://twemoji.maxcdn.com/v/latest/72x72/{ordinal:x}.png") as r:
            try:
              if r.status in range(200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await role.edit(display_icon=bytes, reason=f"role icon changed by {ctx.author}")
                embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: changed role icon for {role.mention}")
                await sendmsg(self, ctx, None, embed, None, None, None, None) 
            except discord.HTTPException:
                embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.nono} {ctx.author.mention}: i was unable to change the role icon")
                await sendmsg(self, ctx, None, embed, None, None, None, None)

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def giveall(self, ctx: commands.Context, *, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role.name)
        if not role:            
             return
        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: adding {role.mention} to all members...")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
            if role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.put(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(1)

         await message.edit(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: added {role.mention} from all"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: unable to add {role.mention} to all - {e}"))

    @rolemenu.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def removeall(self, ctx: commands.Context, *, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role.name)
        if not role:            
             return
        embed = discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: removing {role.mention} to all members....")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
            if not role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.delete(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(1)

         await message.edit(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.approve} {ctx.author.mention}: removed {role.mention} from all"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colours.standard, description=f"> {Emotes.warning} {ctx.author.mention}: unable to {role.mention} to all - {e}")) 

async def setup(bot) -> None: 
    await bot.add_cog(roles(bot))          
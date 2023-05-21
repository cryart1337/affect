import discord, ordinal
import aiosqlite
from discord.ext import commands
from utility import Emotes, Colours
from cogs.events import sendmsg, noperms, blacklist

def get_parts(params):
    params=params.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

async def to_object(params):

    x={}
    fields=[]
    content=None
    view=discord.ui.View()

    for part in get_parts(params):
        
        if part.startswith('content:'):
            content=part[len('content:'):]
          
        if part.startswith('title:'):
            x['title']=part[len('title:'):]
        
        if part.startswith('description:'):
            x['description']=part[len('description:'):]

        if part.startswith('footer:'):
            x['footer']=part[len('footer:'):]

        if part.startswith('color:'):
            try:
                x['color']=int(part[len('color:'):].strip('#').strip(), 16)
            except:
                x['color']=Colours.standard

        if part.startswith('image:'):
            x['image']={'url': part[len('description:'):]}

        if part.startswith('thumbnail:'):
            x['thumbnail']={'url': part[len('thumbnail:'):]}
        
        if part.startswith('author:'):
            z=part[len('author:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            try:
                url=z[2] if z[2] else None
            except:
                url=None

            x['author']={'name': name}
            if icon_url:
                x['author']['icon_url']=icon_url
            if url:
                x['author']['url']=url

        if part.startswith('field:'):
            z=part[len('field:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                value=z[1] if z[1] else None
            except:
                value=None
            try:
                inline=z[2] if z[2] else True
            except:
                inline=True

            if isinstance(inline, str):
                if inline == 'true':
                    inline=True

                elif inline == 'false':
                    inline=False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z=part[len('footer:'):].split(' && ')
            try:
                text=z[0] if z[0] else None
            except:
                text=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            x['footer']={'text': text}
            if icon_url:
                x['footer']['icon_url']=icon_url
                
        if part.startswith('button:'):
            z=part[len('button:'):].split(' && ')
            try:
                label=z[0] if z[0] else None
            except:
                label='no label'
            try:
                url=z[1] if z[1] else None
            except:
                url='https://none.none'
            try:
                emoji=z[2] if z[2] else None
            except:
                emoji=None
                
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=label, url=url, emoji=emoji))
            
    if not x: embed=None
    else:
        x['fields']=fields
        embed=discord.Embed.from_dict(x)
    return content, embed, view


async def embed_replacement(user, params):

    if '{user}' in params:
        params=params.replace('{user}', user)
    if '{user.mention}' in params:
        params=params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params=params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params=params.replace('{user.avatar}', user.display_avatar.url)
    if '{user.joined_at}' in params:
        params=params.replace('{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R'))
    if '{user.created_at}' in params:
        params=params.replace('{user.created_at}', discord.utils.format_dt(user.created_at, style='R'))
    if '{user.discriminator}' in params:
        params=params.replace('{user.discriminator}', user.discriminator)
    if '{guild.name}' in params:
        params=params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params=params.replace('{guild.count}', str(user.guild.member_count))
    if '{guild.count.format}' in params:
        params=params.replace('{guild.count.format}', ordinal(len(user.guild.members)))
    if '{guild.id}' in params:
        params=params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params=params.replace('{guild.created_at}', discord.utils.format_dt(user.guild.created_at, style='R'))
    if '{guild.boost_count}' in params:
        params=params.replace('{guild.boost_count}', str(user.guild.premium_subscription_count))
    if '{guild.booster_count}' in params:
        params=params.replace('{guild.booster_count}', str(len(user.guild.premium_subscribers)))
    if '{guild.boost_count.format}' in params:
        params=params.replace('{guild.boost_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.booster_count.format}' in params:
        params=params.replace('{guild.booster_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.boost_tier}' in params:
        params=params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    if '{guild.icon}' in params:
        if user.guild.icon:
            params=params.replace('{guild.icon}', user.guild.icon.url)
        else:
            params=params.replace('{guild.icon}', '')
    return params

class autoresponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT response, trigger FROM autoresponderconfiglol WHERE guild = {}".format(ctx.guild.id))
                    data = await cursor.fetchall()
                    if data:
                        for table in data:
                            response = table[0]
                            trigger = table[1]
                            if ctx.author.bot:
                                pass
                            else:
                                if trigger.lower() in ctx.content.lower():
                                    x = await to_object(await embed_replacement(ctx.author, response))
                                    await ctx.channel.send(content=x[0], embed=x[1], view=x[2])
    
    @commands.group()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def autoresponder(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Command: autoresponder", description="sets an autoresponder the server\nto create an embeds or content type `;createembed`",color=Colours.standard, timestamp=ctx.message.created_at)
            e.add_field(name="category", value="config")
            e.add_field(name="Arguments", value="<subcommand> [trigger] [response]")
            e.add_field(name="permissions", value="manage_messages", inline=True)
            e.add_field(name="Command Usage",value="```Syntax: ;autoresponder add affect {embed}{content: ontop boss}$v\nSyntax: ;autoresponder clear\nSyntax: ;autoresponder delete affect\nSyntax: ;autoresponder show```", inline=False)
            await sendmsg(self, ctx, None, e, None, None, None, None)
            return
            
    @autoresponder.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def add(self, ctx, trigger, *, reaction):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("INSERT INTO autoresponderconfiglol VALUES (?, ?, ?)", (trigger, reaction, ctx.guild.id,))
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: Successfully created an **autoresponse** for `{trigger}`", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autoresponder.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def clear(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoresponderconfiglol WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: Successfully deleted **all** triggers", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @autoresponder.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def delete(self, ctx, *, msg):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM autoresponderconfiglol WHERE guild = ? AND trigger LIKE ?", (ctx.guild.id, msg,))
            embed = discord.Embed(description = f"> {Emotes.approve} {ctx.author.mention}: Successfully deleted the **autoresponse** for `{msg}`", color = Colours.standard)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)


    @autoresponder.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def show(self, ctx):
        if not ctx.author.guild_permissions.manage_guild: return await noperms(self, ctx, "manage_guild")
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT response, trigger FROM autoresponderconfiglol WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                num = 0
                auto = ""
                if data:
                    for table in data:
                        trigger = table[1]
                        response = table[0]
                        num += 1
                        auto += f"\n`{num}` {trigger} — {response}"
                    embed = discord.Embed(description = auto, color = Colours.standard)
                    embed.set_author(name = "list of autoresponses", icon_url = ctx.message.author.display_avatar)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
                else:
                    embed = discord.Embed(description = f"> {Emotes.warning} {ctx.message.author.mention}: No auto responder triggers have been set up", color = Colours.standard)
                    await sendmsg(self, ctx, None, embed, None, None, None, None)
        except Exception as e:
            print(e)
                                    
async def setup(bot) -> None:
    await bot.add_cog(autoresponder(bot))
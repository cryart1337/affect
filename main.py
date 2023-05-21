import discord, os, json, aiosqlite, time
from discord.ext import commands
from discord.gateway import DiscordWebSocket, _log
from cogs.voicemaster import vmbuttons

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
        token = configData["token"]

async def getprefix(bot, message):
    if not message.guild:
        return ";"
    selfprefix = ";"
    guildprefix = ";"
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM selfprefix WHERE user_id = {}".format(message.author.id))
        check = await cursor.fetchone()
        if check is not None:
            selfprefix = check[0]
        await cursor.execute("SELECT prefix, * FROM prefixes WHERE guild_id = {}".format(message.guild.id))
        res = await cursor.fetchone()
        if res is not None:
            guildprefix = res[0]
        elif res is None:
            guildprefix = ";"

    return guildprefix, selfprefix

class affect(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix=getprefix,
            case_insensitive=True,
            help_command=None,
            activity=discord.Activity(type=discord.ActivityType.streaming,name="development", url='https://www.twitch.tv/affectdiscordbot'),
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=True),
            strip_after_prefix=True,
            owner_ids=[1065294553659211806, 959055077946032229]
        )
        self.uptime = time.time()

    async def setup_hook(self):
        await db()
        self.add_view(vmbuttons())
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension("cogs." + file[:-3])
                print(f"Loaded cog: {file[:-3]}")

        await self.load_extension("jishaku")

bot = affect()

async def db():
    setattr(bot, "db", await aiosqlite.connect("main.db"))
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS selfprefix (pref TEXT, user_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id INTEGER, prefix TEXT)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS oldusernamess (username TEXT, discriminator INTEGER, time INTEGER, user INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS snipe (guild_id INTEGER, channel_id INTEGER, author TEXT, content TEXT, attachment TEXT, avatar TEXT)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS restore (guild_id INTEGER, user_id INTEGER, roles TEXT);")
        await cursor.execute("CREATE TABLE IF NOT EXISTS afk1 (user INTEGER, guild INTEGER, reason TEXT, time INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS antinuke (guild_id INTEGER, module TEXT, punishment TEXT)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS whitelist (guild_id INTEGER, user_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS autoresponderconfiglol (trigger TEXT, response TEXT, guild INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS autorole (role INTEGER, guild INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS chatfilter (trigger TEXT, guild INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS goodbye (guild INTEGER, message TEXT, channel INTEGER)") 
        await cursor.execute("CREATE TABLE IF NOT EXISTS imageonly (channel INTEGER, guild INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS lfmode (mode TEXT, user INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id INTEGER, username TEXT)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS lastfmcc (user_id INTEGER, command TEXT)")
        await cursor.execute('CREATE TABLE IF NOT EXISTS reaction_roles (role_id INTEGER, message_id INTEGER, emoji TEXT, PRIMARY KEY (role_id, message_id, emoji))')
        await cursor.execute("CREATE TABLE IF NOT EXISTS voicemaster (guild_id INTEGER, vc INTEGER, interface INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS vcs (user_id INTEGER, voice INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS welcome (guild INTEGER, message TEXT, channel INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS nodata (user INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS warns (guild_id INTEGER, user_id INTEGER, author_id INTEGER, reason TEXT)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS tracker (guild_id INTEGER, channel INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS joindm (guild INTEGER, message TEXT)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS setme (channel_id INTEGER, role_id INTEGER, guild_id INTEGER)") 
        await cursor.execute("CREATE TABLE IF NOT EXISTS jail (guild_id INTEGER, user_id INTEGER, roles TEXT)")
    await bot.db.commit()

bot.run(token)
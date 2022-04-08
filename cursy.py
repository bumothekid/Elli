# Imports
import nextcord
import sqlite3
import re
from time import time
from nextcord.ext import commands
from nextcord.ext.commands.errors import NotOwner
from os import listdir

def getPrefixFromDatabase(bot, message):
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute(f"SELECT prefix FROM guilds WHERE guild_id = '{message.guild.id}'")
    prefix = c.fetchone()
    if prefix is None:
        c.execute("INSERT INTO guilds (guild_id, prefix) VALUES (?, ?)", (message.guild.id, "-"))
        db.commit()
        return "-"
    return prefix

# Bot
bot = commands.Bot(command_prefix=getPrefixFromDatabase, intents=nextcord.Intents.all(), help_command=None)

# Extensions

extensions = [
    'commands.events',
    'commands.help',
    'commands.error',
    'commands.developer',
    'commands.welcome',
    'commands.reactionrole',
    'commands.giveaway',
    'commands.tempchannel',
    'commands.ticket',
    'commands.afk',
    'commands.bot'
]

@bot.event
async def on_ready():
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute(f"UPDATE cursy SET uptime = '{time()}'")
    db.commit()
    print('═════◢◤◈◥◣═════')
    print('Bot ist Online.')
    print(bot.user.name)
    print(bot.user.id)
    print('═════◥◣◈◢◤═════')
    await statusTask()

async def statusTask():
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name='ZS und Bumo'))

@bot.command()
async def load(ctx, ext):
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute("SELECT developer FROM cursy")
    devs = c.fetchone()[0]
    devlist = re.findall(r"[0-9]+", devs)

    if str(ctx.author.id) not in devlist:
        raise NotOwner

    extension = f"commands.{ext}"

    try:
        bot.load_extension(extension)

        await cogEmbed(ctx, success=True, text=f'{extension} wurde geladen.')
    except Exception as error:
        await cogEmbed(ctx, success=False, text=f'{extension} konnte nicht geladen werden\n`[{error}]`')

@bot.command()
async def unload(ctx, ext):
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute("SELECT developer FROM cursy")
    devs = c.fetchone()[0]
    devlist = re.findall(r"[0-9]+", devs)

    if str(ctx.author.id) not in devlist:
        raise NotOwner

    extension = f"commands.{ext}"

    try:
        bot.unload_extension(extension)

        await cogEmbed(ctx, success=True, text=f'{extension} wurde deaktiviert.')
    except Exception as error:
        await cogEmbed(ctx, success=False, text=f'{extension} konnte nicht deaktiviert werden\n`[{error}]`')

@bot.command()
async def reload(ctx, ext):
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute("SELECT developer FROM cursy")
    devs = c.fetchone()[0]
    devlist = re.findall(r"[0-9]+", devs)

    if str(ctx.author.id) not in devlist:
        raise NotOwner

    extension = f"commands.{ext}"

    try:
        if ext != "*":

            bot.reload_extension(name=extension)

            return await cogEmbed(ctx, success=True, text=f'{extension} wurde neu geladen.')

        for extension in extensions:
            bot.reload_extension(name=extension)
        
        await cogEmbed(ctx, success=True, text=f'{len(extensions)} Cog´s neu geladen.')
    except Exception as error:
        await cogEmbed(ctx, success=False, text=f'{extension} konnte nicht geladen werden\n`[{error}]`')

async def cogEmbed(ctx, success: bool, text: str):
    return await ctx.reply(embed=nextcord.Embed(description=text, color=nextcord.Color.green() if success else nextcord.Color.red()))

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            print(f'{extension} konnte nicht geladen werden.\n`[{error}]`')

bot.run("***REMOVED***")
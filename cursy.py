# Imports
import nextcord
import sqlite3
import re
from time import time
from nextcord.ext import commands
from nextcord.ext.commands.errors import NotOwner
from os import listdir

# Bot
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
bot.remove_command("help")

# Extensions

extensions = [
    'commands.help',
    'commands.error',
    'commands.developer',
    'commands.welcome',
    'commands.reactionrole',
    'commands.giveaway',
    'commands.tempchannel',
    'commands.ticket',
    'commands.bot'
]

# On Ready
@bot.event
async def on_ready():
    """
    When the bot is ready, print some stuff
    """
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

# Status
async def statusTask():
    # This is a status message.
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name='ZS und Bumo'))

# Load Extension
@bot.command()
async def load(interaction, ext):
    """
    It loads an extension
    
    :param interaction: The interaction object
    :param ext: The extension to load
    """
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute("SELECT developer FROM cursy")
    devs = c.fetchone()[0]
    devlist = re.findall(r"[0-9]+", devs)
    if str(interaction.author.id) not in devlist:
        raise NotOwner
    extension = f"commands.{ext}"
    try:
        bot.load_extension(extension)
        await interaction.reply(f'{extension} wurde geladen.')
    except Exception as error:
        await interaction.reply(f'{extension} konnte nicht geladen werden. [{error}]')

# Unload Extension
@bot.command()
async def unload(interaction, ext):
    """
    It loads an extension
    
    :param interaction: The command that was sent
    :param ext: The extension to unload
    """
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute("SELECT developer FROM cursy")
    devs = c.fetchone()[0]
    devlist = re.findall(r"[0-9]+", devs)
    if str(interaction.author.id) not in devlist:
        raise NotOwner
    extension = f"commands.{ext}"
    try:
        bot.unload_extension(extension)
        await interaction.reply(f'{extension} wurde deaktiviert.')
    except Exception as error:
        await interaction.reply(f'{extension} konnte nicht deaktiviert werden. [{error}]')

# Reload Extension
@bot.command()
async def reload(interaction, ext):
    """
    Reloads an extension
    
    :param interaction: The interaction object
    :param ext: The extension to reload
    :return: A string.
    """
    db = sqlite3.connect("database.db")
    c = db.cursor()
    c.execute("SELECT developer FROM cursy")
    devs = c.fetchone()[0]
    devlist = re.findall(r"[0-9]+", devs)
    if str(interaction.author.id) not in devlist:
        raise NotOwner
    extension = f"commands.{ext}"
    try:
        if ext != "*":
            bot.reload_extension(name=extension)
            await interaction.reply(f'{extension} wurde neu geladen.')
            return
        for extension in extensions:
            bot.reload_extension(name=extension)
        await interaction.reply(f"Es wurden {len(extensions)} Cog´s neu geladen.")
    except Exception as error:
        await interaction.reply(f'{extension} konnte nicht geladen werden. [{error}]')

# Start
if __name__ == '__main__':
# This is a loop. It loops through the extensions list and tries to load them.
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            print(f'{extension} konnte nicht geladen werden. [{error}]')

bot.run("***REMOVED***")
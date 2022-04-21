# Imports
import nextcord
from time import time
from nextcord.ext import commands
from nextcord.ext.commands.errors import NotOwner
from commands.utils.other import getPrefixFromDatabase, devCheck
from commands.utils.embeds import successEmbed, errorEmbed, devLogging
from commands.utils.database import update

bot = commands.Bot(command_prefix=getPrefixFromDatabase, intents=nextcord.Intents.all(), help_command=None)

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
    update(table="cursy", columns="uptime", values=[time()])

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
    if not devCheck(ctx.author.id):
        raise NotOwner

    try:
        bot.load_extension(ext if "commands." in ext else f"commands.{ext}")

        await devLogging(bot, ctx, f"{ctx.author} hat {ext} geladen.")
        await successEmbed(bot, ctx, f"{ext} wurde geladen.")
    except Exception as e:
        await errorEmbed(bot, ctx, f"{ext} konnte nicht geladen werden.\n```py\n{e}```")

@bot.command()
async def unload(ctx, ext):
    if not devCheck(ctx.author.id):
        raise NotOwner

    try:
        bot.unload_extension(ext if "commands." in ext else f"commands.{ext}")

        await devLogging(bot, ctx, f"{ctx.author} hat {ext} entladen.")
        await successEmbed(bot, ctx, f"{ext} wurde deaktiviert.")
    except Exception as error:
        await errorEmbed(bot, ctx, f"{ext} konnte nicht deaktiviert werden.\n```py\n{error}```")

@bot.command()
async def reload(ctx, ext):
    if not devCheck(ctx.author.id):
        raise NotOwner

    if ext in ["all", "alle", "*", "commands.*"]:
        for extension in extensions:
            try:
                bot.reload_extension(extension)
            except Exception as e:
                await errorEmbed(bot, ctx, f"{extension} konnte nicht geladen werden.\n```py\n{e}```")

        await devLogging(bot, ctx, f"{ctx.author} hat alle Cogs neu geladen.")
        return await successEmbed(bot, ctx, "Alle Cogs wurden neu geladen.")

    try:
        bot.reload_extension(ext)
        await devLogging(bot, ctx, f"{ctx.author} hat {ext} neu geladen.")
        await successEmbed(bot, ctx, f"{ext} wurde neu geladen.")
    except Exception as e:
        await errorEmbed(bot, ctx, f"{ext} konnte nicht geladen werden.\n```py\n{e}```")

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'{extension} konnte nicht geladen werden.\n`[{e}]`')

bot.run("***REMOVED***")
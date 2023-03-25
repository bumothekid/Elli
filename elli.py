# Imports
import os
import asyncio
import nextcord
from time import time
from dotenv import load_dotenv
from nextcord.ext import commands
from commands.utils.database import update
from nextcord.ext.commands.errors import NotOwner
from commands.utils.embeds import successEmbed, errorEmbed, devLogging
from commands.utils.other import getPrefixFromDatabase, devCheck, capString

bot = commands.Bot(command_prefix=getPrefixFromDatabase, intents=nextcord.Intents.all(), help_command=None, case_insensitive=True)

extensions = [
    'commands.events',
    'commands.help',
    'commands.error',
    'commands.developer',
    'commands.general',
    'commands.useful',
    'commands.fun',
    'commands.moderation',
    'commands.welcome',
    'commands.leave',
    'commands.levelsys',
    'commands.reactionrole',
    'commands.giveaway',
    'commands.tempchannel',
    'commands.ticket',
    'commands.afk',
    'commands.automod',
    'commands.autoroles'
]

@bot.event
async def on_ready():
    update(table="elli", columns="uptime", values=[time()])

    print('═════◢◤◈◥◣═════')
    print('Bot ist Online.')
    print(bot.user.name)
    print(bot.user.id)
    print('═════◥◣◈◢◤═════')

    await statusTask()

async def statusTask():
    while True:
        User = sum(len(s.members) for s in bot.guilds)
        await bot.change_presence(
            activity=nextcord.Activity(type=nextcord.ActivityType.streaming, name=f"💕-help | {User} User",
                                    url="https://www.twitch.tv/twitch")
        )
        await asyncio.sleep(100)
        servers = list(bot.guilds)
        await bot.change_presence(
            activity=nextcord.Activity(type=nextcord.ActivityType.streaming, name=f"💕-help | {len(servers)} Server",
                                    url="https://www.twitch.tv/twitch"))
        await asyncio.sleep(100)
        await bot.change_presence(
            activity=nextcord.Activity(type=nextcord.ActivityType.streaming, name="💕-help | -invite Invite",
                                    url="https://www.twitch.tv/twitch"))
        await asyncio.sleep(100)

@bot.command()
async def load(ctx, ext):
    if not devCheck(ctx.author.id):
        raise NotOwner

    rawExt = ext
    ext = capString(ext)

    try:
        bot.load_extension(rawExt if "commands." in ext else f"commands.{rawExt}")
        
        await bot.sync_all_application_commands()
        await devLogging(bot, ctx, f"{ctx.author} hat {ext} geladen.")
        await successEmbed(bot, ctx, f"{ext} wurde geladen.")
    except Exception as e:
        await errorEmbed(bot, ctx, f"{ext} konnte nicht geladen werden.**\n```py\n{e}```** ")

@bot.command()
async def unload(ctx, ext):
    if not devCheck(ctx.author.id):
        raise NotOwner
    
    rawExt = ext
    ext = capString(ext)

    try:
        bot.unload_extension(rawExt if "commands." in ext else f"commands.{rawExt}")

        await bot.sync_all_application_commands()
        await devLogging(bot, ctx, f"{ctx.author} hat {ext} entladen.")
        await successEmbed(bot, ctx, f"{ext} wurde deaktiviert.")
    except Exception as error:
        await errorEmbed(bot, ctx, f"{ext} konnte nicht deaktiviert werden.**\n```py\n{error}```** ")

@bot.command()
async def reload(ctx, ext):
    if not devCheck(ctx.author.id):
        raise NotOwner
    
    rawExt = ext
    ext = capString(ext)

    if rawExt in ["all", "alle", "*", "commands.*"]:
        for extension in extensions:
            try:
                bot.reload_extension(extension)
            except Exception as e:
                await errorEmbed(bot, ctx, f"{extension} konnte nicht geladen werden.**\n```py\n{e}```** ")

        await bot.sync_all_application_commands()
        await devLogging(bot, ctx, f"{ctx.author} hat alle Cogs neu geladen.")
        return await successEmbed(bot, ctx, "Alle Cogs wurden neu geladen.")

    try:
        bot.reload_extension(rawExt if "commands." in ext else f"commands.{rawExt}")

        await bot.sync_all_application_commands()
        await devLogging(bot, ctx, f"{ctx.author} hat {ext} neu geladen.")
        await successEmbed(bot, ctx, f"{ext} wurde neu geladen.")
    except Exception as e:
        await errorEmbed(bot, ctx, f"{ext} konnte nicht geladen werden.**\n```py\n{e}```** ")

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'{extension} konnte nicht geladen werden.\n`[{e}]`')

    load_dotenv()
    test_token = os.getenv("TEST_TOKEN")
    bot_token = os.getenv("TOKEN")
    test = os.getenv("TEST")

    bot.run(test_token if test == "True" else bot_token)
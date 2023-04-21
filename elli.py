# Imports
import os
import asyncio
import nextcord
from time import time
from dotenv import load_dotenv
from nextcord.ext import commands, tasks
from commands.utils.database import update
from nextcord.ext.commands.errors import NotOwner
from commands.utils.embeds import successEmbed, errorEmbed, devLogging
from commands.utils.other import getPrefixFromDatabase, devCheck, capString

intents = nextcord.Intents.default()
intents.guilds = True
intents.members = True
intents.moderation = True
intents.emojis_and_stickers = True
intents.invites = True
intents.voice_states = True
intents.guild_messages = True
intents.message_content = True
intents.guild_reactions = True

bot = commands.Bot(command_prefix=getPrefixFromDatabase, intents=intents, help_command=None, case_insensitive=True)

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
    'commands.autoroles',
    'commands.topgg'
]

@bot.event
async def on_ready():
    print('═════◢◤◈◥◣═════')
    print('Bot ist Online.')
    print(bot.user.name)
    print(bot.user.id)
    print('═════◥◣◈◢◤═════')

@tasks.loop(seconds=100)
async def statusTask():
    await bot.wait_until_ready()
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
        devLogging(bot, ctx, f"{ctx.author} loaded {ext}.")
        await successEmbed(bot, ctx, f"{ext} loaded.")
    except Exception as e:
        await errorEmbed(bot, ctx, f"{ext} couldn't be loaded.**\n```py\n{e}```** ")

@bot.command()
async def unload(ctx, ext):
    if not devCheck(ctx.author.id):
        raise NotOwner
    
    rawExt = ext
    ext = capString(ext)

    try:
        bot.unload_extension(rawExt if "commands." in ext else f"commands.{rawExt}")

        await bot.sync_all_application_commands()
        devLogging(bot, ctx, f"{ctx.author} unloaded {ext}.")
        await successEmbed(bot, ctx, f"{ext} has been deactivated.")
    except Exception as error:
        await errorEmbed(bot, ctx, f"{ext} couldn't be deactivated.**\n```py\n{error}```** ")

@bot.command()
async def reload(ctx, ext):
    if not devCheck(ctx.author.id):
        raise NotOwner
    
    rawExt = ext
    ext = capString(ext)

    if rawExt in ["all", "*", "commands.*"]:
        for extension in extensions:
            try:
                bot.reload_extension(extension)
            except Exception as e:
                await errorEmbed(bot, ctx, f"{extension} couldn't be loaded.**\n```py\n{e}```** ")

        await bot.sync_all_application_commands()
        devLogging(bot, ctx, f"{ctx.author} reloaded all cogs.")
        return await successEmbed(bot, ctx, "All cogs have been reloaded.")

    try:
        bot.reload_extension(rawExt if "commands." in ext else f"commands.{rawExt}")

        await bot.sync_all_application_commands()
        devLogging(bot, ctx, f"{ctx.author} reloaded {ext}.")
        await successEmbed(bot, ctx, f"{ext} has been reloaded.")
    except Exception as e:
        await errorEmbed(bot, ctx, f"{ext} couldn't be loaded.**\n```py\n{e}```** ")

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"{extension} couldn't be loaded.\n`[{e}]`")

    load_dotenv()
    test_token = os.getenv("TEST_TOKEN")
    bot_token = os.getenv("TOKEN")
    test = os.getenv("TEST")

    statusTask.start()
    update(table="elli", columns="uptime", values=[time()])
    bot.run(test_token if test == "True" else bot_token)
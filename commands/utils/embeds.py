import os
import json
import asyncio
import contextlib
import nextcord
from nextcord import ui
from nextcord.ext.commands.bot import Bot
from .models.EmbedField import EmbedField
from .database import readOne, insert, update

botLoggingChannelID = 1087069858455375953

async def infoEmbed(
    bot,
    ctx: nextcord.Interaction | nextcord.TextChannel | nextcord.message.Message | nextcord.ext.commands.context.Context | nextcord.Member,
    text: str,
    content: str = None,
    color: nextcord.Color = nextcord.Color.blurple(),
    fields: list[dict] | list[EmbedField] = None,
    footer: dict = None,
    view: ui.View = None,
    file: nextcord.File = None,
    delete_after: int = None,
    thumbnail: str = None,
    image: str = None,
    ephemeral: bool = False
    ) -> nextcord.Message:
    """ 
    Creates and sends an information embed
    This is used when a information is shown

    Parameters
    -----------
    bot: :class:`nextcord.ext.commands.Bot or nextcord.Interaction or nextcord.TextChannel or nextcord.Message or nextcord.ext.commands.Context or nextcord.Member`
        The bot instance

    ctx: :class:`nextcord.Interaction`
        The interaction to reply to or channel if you want to send the embed to an specific channel

    text: :class:`str`
        The text to embed

    content: :class:`str`
        Optional content to send with the embed

    color: :class:`nextcord.Color`
        Optional color to use for the embed

    fields: :class:`list[dict] or list[EmbedField]`
        Optional fields with a name and a value

    footer: :class:`dict`
        Optional text and icon_url to use for the footer

    view: :class:`nextcord.ui.View`
        Optional view to use for the embed

    file: :class:`nextcord.File`
        Optional file to send with the embed

    delete_after: :class:`int`
        Optional time in seconds to delete the embed after it was sent
        Only works if the embed is sent to a channel
    
    thumbnail: :class:`str`
        Optional thumbnail to use for the embed
    
    image: :class:`str`
        Optional image to use for the embed
    """
    if type(bot) is not Bot:
        try:
            bot = bot.bot
        except Exception:
            return ValueError("Bot is not a bot or self")

    if delete_after is not None:
        if not isinstance(delete_after, int):
            raise ValueError("delete_after is not an int")

    infoEmbed = nextcord.Embed(
        description=text, 
        color=color
    )

    if fields is not None:
        if not isinstance(fields, list):
            raise ValueError("fields is not a list")
        

        for field in fields:
            if isinstance(field, EmbedField):
                infoEmbed.add_field(
                    name=field.name,
                    value=field.value,
                    inline=field.inline
                )
            elif isinstance(field, dict):
                infoEmbed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )
            else:
                raise ValueError("Field is not a EmbedField or dict")


    if footer is not None:
        try:
            infoEmbed.set_footer(text=footer["text"], icon_url=footer["icon_url"])
        except KeyError:
            print("There was an KeyError while setting footer")
        
    if thumbnail is not None:
        if not isinstance(thumbnail, str):
            raise ValueError("thumbnail is not a str")
        infoEmbed.set_thumbnail(url=thumbnail)

    if image is not None:
        if not isinstance(image, str):
            raise ValueError("image is not a str")

        infoEmbed.set_image(url=image)
    
    try:
        match type(ctx):
            case nextcord.Interaction:
                if file is None:
                    message = await ctx.response.send_message(content=content, embed=infoEmbed, delete_after=delete_after, ephemeral=ephemeral)

                else:
                    message = await ctx.response.send_message(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after, ephemeral=ephemeral)

                return message
            case nextcord.ext.commands.context.Context:
                message = await ctx.reply(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after)
                return message
            case nextcord.message.Message:
                message = await ctx.reply(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after)
                return message
            case nextcord.TextChannel:
                message = await ctx.send(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after)
                return message
            case nextcord.Member:
                dm = await ctx.create_dm()
                await dm.send(content=content, embed=infoEmbed, view=view, file=file)
            case _:
                print(type(ctx))
                print("Error: Unknown interaction")
    except Exception:
        await permissionError(bot, ctx)

async def successEmbed(
    bot,
    ctx: nextcord.Interaction | nextcord.TextChannel | nextcord.message.Message | nextcord.ext.commands.context.Context | nextcord.Member,
    text: str,
    content: str = None,
    color = nextcord.Color.green(),
    fields: list[dict] | list[EmbedField] = None,
    footer: dict = None,
    view: ui.View = None,
    file: nextcord.File = None,
    delete_after: int = None,
    thumbnail: str = None,
    image: str = None,
    ephemeral: bool = False
    ) -> nextcord.Message:
    """ 
    Creates and sends an successed embed
    This is used when a something succeeds

    Parameters
    -----------
    bot: :class:`nextcord.ext.commands.Bot or nextcord.Interaction or nextcord.TextChannel or nextcord.Message or nextcord.ext.commands.Context or nextcord.Member`
        The bot instance

    ctx :class:`nextcord.Interaction or nextcord.TextChannel`
        The interaction to reply to or channel if you want to send the embed to an specific channel

    text: :class:`str`
        The text to embed

    content: :class:`str`
        Optional content to send with the embed

    color: :class:`nextcord.Color`
        Optional color to use for the embed

    fields: :class:`list[dict] or list[EmbedField]`
        Optional fields with a name and a value

    footer: :class:`dict`
        Optional text and icon_url to use for the footer

    view: :class:`nextcord.ui.View`
        Optional view to use for the embed

    file: :class:`nextcord.File`
        Optional file to send with the embed

    delete_after: :class:`int`
        Optional time in seconds to delete the embed after it was sent
        Only works if the embed is sent to a channel

    thumbnail: :class:`str`
        Optional thumbnail to use for the embed

    image: :class:`str`
        Optional image to use for the embed
    """
    if type(bot) is not Bot:
        try:
            bot = bot.bot
        except Exception:
            return ValueError("Bot is not a bot or self")

    if delete_after is not None:
        if not isinstance(delete_after, int):
            raise ValueError("delete_after is not an int")

    successEmbed = nextcord.Embed(
        description=text,
        color=color
    )

    if fields is not None:
        if not isinstance(fields, list):
            raise ValueError("fields is not a list")
        

        for field in fields:
            if isinstance(field, EmbedField):
                successEmbed.add_field(
                    name=field.name,
                    value=field.value,
                    inline=field.inline
                )
            elif isinstance(field, dict):
                successEmbed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )
            else:
                raise ValueError("Field is not a EmbedField or dict")


    if footer is not None:
        successEmbed.set_footer(text=footer["text"], icon_url=footer["icon_url"])

    if thumbnail is not None:
        if not isinstance(thumbnail, str):
            raise ValueError("thumbnail is not a str")
        successEmbed.set_thumbnail(url=thumbnail)

    if image is not None:
        if not isinstance(image, str):
            raise ValueError("image is not a str")

        successEmbed.set_image(url=image)

    try:
        match type(ctx):
            case nextcord.Interaction:
                if file is None:
                    message = await ctx.response.send_message(content=content, embed=successEmbed, delete_after=delete_after, ephemeral=ephemeral)

                else:
                    message = await ctx.response.send_message(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after, ephemeral=ephemeral)

                return message
            case nextcord.ext.commands.context.Context:
                message = await ctx.reply(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after)
                return message
            case nextcord.message.Message:
                message = await ctx.reply(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after)
                return message
            case nextcord.TextChannel:
                message = await ctx.send(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after)
                return message
            case nextcord.Member:
                dm = await ctx.create_dm()
                await dm.send(content=content, embed=successEmbed, view=view, file=file)
            case _:
                print(type(ctx))
                print("Error: Unknown interaction")
    except Exception:
        await permissionError(bot, ctx)

async def errorEmbed(bot, ctx: nextcord.Interaction | nextcord.message.Message | nextcord.TextChannel | nextcord.ext.commands.context.Context | nextcord.Member, text: str, file: nextcord.File = None):
    """ 
    Creates and sends an error embed
    This is used when something is wrong and throws an exception

    Parameters
    -----------
    bot: :class:`nextcord.ext.commands.Bot or nextcord.Interaction or nextcord.TextChannel or nextcord.Message or nextcord.ext.commands.Context or nextcord.Member`
        The bot instance

    ctx: :class:`nextcord.Interaction`
        The interaction to reply to or channel if you want to send the embed to an specific channel

    text: :class:`str`
        The text to embed

    file: :class:`nextcord.File`
        Optional file to send with the embed

    """
    if type(bot) is not Bot:
        try:
            bot = bot.bot
        except Exception:
            return ValueError("Bot is not a bot or self")

    errorEmbed = nextcord.Embed(
        description=f"> **{text}**",
        color=nextcord.Color.red()
    )

    try:
        match type(ctx):
            case nextcord.Interaction:
                if file is None:
                    message = await ctx.response.send_message(embed=errorEmbed)

                else:
                    message = await ctx.response.send_message(embed=errorEmbed, file=file)

                return message
            case nextcord.ext.commands.context.Context:
                await ctx.reply(embed=errorEmbed, file=file)
            case nextcord.message.Message:
                await ctx.reply(embed=errorEmbed, file=file)
            case nextcord.TextChannel:
                await ctx.send(embed=errorEmbed, file=file)
            case nextcord.Member:
                dm = await ctx.create_dm()
                await dm.send(embed=errorEmbed, file=file)
            case _:
                print(type(ctx))
                print("Error: Unknown interaction")
    except Exception:
        await permissionError(bot, ctx)

def errorLogging(bot, ctx: nextcord.Interaction, error: str):
    """
    Creates and sends an error embed for critical errors into the bot logging channel
    This is called when an error occurs and the bot can't handle it
    """
    
    if type(bot) is not Bot: return print("Type error: Bot is not a bot")

    channel = bot.get_channel(botLoggingChannelID)
    errorEmbed = nextcord.Embed(
        description=f"> **An error occurred while executing a command**\n\n> **<:Globe:1087448923834163342> Guild:** `{ctx.guild}`\n> **<:Reply:1087438925632643082> Guild ID:** `{ctx.guild.id}`\n> **<:Clyde:1087435842785640448> Command:** `{ctx.message.content}`\n> **<:Reply:1087438925632643082> Command Executer:** `{ctx.author}`\n> **<:Error:1087445963280486430> Error:**\n```py\n{error}```",
        color=nextcord.Color.red()
    )

    asyncio.run_coroutine_threadsafe(channel.send(embed=errorEmbed), bot.loop)
    
def localizationError(bot, error: str, *args):
    """
    Creates and sends an error embed for language errors into the bot logging channel
    This is called when an error occurs while translating or formatting the text
    """
    
    if type(bot) is not Bot: return print("Type error: Bot is not a bot")
    
    args = [str(arg.__class__.__name__) for arg in args]

    channel = bot.get_channel(botLoggingChannelID)
    errorEmbed = nextcord.Embed(
        description=f"> **An error occoured while trying to localize string**\n\n> <:Clyde:1087435842785640448> Passed Arguments:\n> <:Reply:1087438925632643082> `{', '.join(args) if args else 'None'}`\n> **<:LanguageError:1099004614361219113> Error:**\n> <:Reply:1087438925632643082> `{error}`",
        color=nextcord.Color.from_rgb(234, 145, 53),
    )

    asyncio.run_coroutine_threadsafe(channel.send(embed=errorEmbed), bot.loop)

def devLogging(bot, ctx: nextcord.Interaction, text: str):
    """
    Creates and sends an embed into the bot logging channel
    This is called when a developer command is used
    """
    
    if type(bot) is not Bot: return print("Type error: Bot is not a bot")
        
    channel = bot.get_channel(botLoggingChannelID)
    embed = nextcord.Embed(
        description=f"> **A developer command was used**\n\n> **<:Globe:1087448923834163342> Guild:** `{ctx.guild}`\n> **<:Reply:1087438925632643082> Guild ID:** `{ctx.guild.id}`\n> **<:Clyde:1087435842785640448> Command:** `{ctx.message.content}`\n> **<:Reply:1087438925632643082> Command Executer:** `{ctx.author}`\n> **<:Tick:1087458362410684476> Action:**\n> <:Reply:1087438925632643082> `{text}`",
        color=nextcord.Color.blurple()
    )

    asyncio.run_coroutine_threadsafe(channel.send(embed=embed), bot.loop)

async def permissionError(bot, ctx: nextcord.Interaction):
    if type(bot) is not Bot:
        try:
            bot = bot.bot
        except Exception:
            return print("Error: Bot is not a bot or self")

    emote = bot.get_emoji(1087445963280486430)
    
    languageStrings = getLanguageStrings("error")
    guildLocale = getGuildLanguage(ctx.guild.id)

    permissionEmbed = nextcord.Embed(
        description=f"> **{getLocale(bot, languageStrings, guildLocale, 'forbiddenError')}**",
        color=nextcord.Color.red()
    )
    
    # Try adding a reaction to the message if possible else ignore
    with contextlib.suppress(Exception):
        match type(ctx):
            case nextcord.Interaction:
                pass
            case nextcord.ext.commands.context.Context:
                await ctx.message.add_reaction(emote)
            case nextcord.message.Message:
                await ctx.add_reaction(emote)
            case _:
                print(type(ctx))
                print("Error: Unknown interaction")
                
    
                
    if isinstance(ctx, nextcord.Interaction):
        await ctx.user.create_dm()
        await ctx.user.dm_channel.send(embed=permissionEmbed)
        return
    
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(embed=permissionEmbed)
    
    
# Todo: Better solution for this; This is a workaround and terrible

def getGuildLanguage(guild_id) -> str:
    result = readOne("language", "guilds", "guild_id", guild_id)

    if result is None:
        insert("guilds", "guild_id, prefix, language", [guild_id, "-", "en"])
        return "en"
    
    if result[0] is None:
        update("guilds", "language", "guild_id", ["en", guild_id])
        return "en"
    
    return result[0]

def getLanguageStrings(cog: str):
    languageStrings = {}

    for file in os.listdir(f"./language/{cog}"):
        if file.endswith(".json"):
            with open(f"./language/{cog}/{file}", "r", encoding="utf-8") as f:
                languageStrings[file.replace(".json", "")] = json.load(f)
            
    return languageStrings

def getLocale(bot: Bot, languageStrings: dict, language: str, string: str, *args):
    if language not in languageStrings:
        return f"Missing language {language}"

    if string not in languageStrings[language]:
        localizationError(bot, f"Missing string {string} in language {language}")
        
        return f"Missing string {string} in language {language}"
    
    try:
        return languageStrings[language][string].format(*args)
    except IndexError as e:
        missingArgs = e.args[0].split("index ")[1].split(" out of range")[0]
        
        localizationError(bot, f"Missing argument {missingArgs} in string {string} for language {language}.")
        return languageStrings[language][string]
    except KeyError as e:
        missingArgs = e.args[0]
        
        localizationError(bot, f"Missing argument {missingArgs} in string {string} for language {language}.")
        return languageStrings[language][string]
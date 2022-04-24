import contextlib
import nextcord
from nextcord import ui
from nextcord.ext.commands.bot import Bot
from .models.EmbedField import EmbedField

botLoggingChannelID = 957444324080115762

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
    thumbnail: str = None
    ):
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
    
    print("Setting thumbnail")

    # try:
    match type(ctx):
        case nextcord.Interaction:
            print("Sending embed to interaction")
            await ctx.reply(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after)
        case nextcord.ext.commands.context.Context:
            print("Setting context")
            await ctx.reply(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after)
        case nextcord.message.Message:
            await ctx.reply(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after)
        case nextcord.TextChannel:
            await ctx.send(content=content, embed=infoEmbed, view=view, file=file, delete_after=delete_after)
        case nextcord.Member:
            dm = await ctx.create_dm()
            await dm.send(content=content, embed=infoEmbed, view=view, file=file)
        case _:
            print(type(ctx))
            print("Error: Unknown interaction")
    # except Exception:
    #     await permissionError(bot, ctx)

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
    thumbnail: str = None
    ):
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

    try:
        match type(ctx):
            case nextcord.Interaction:
                await ctx.reply(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after)
            case nextcord.ext.commands.context.Context:
                await ctx.reply(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after)
            case nextcord.message.Message:
                await ctx.reply(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after)
            case nextcord.TextChannel:
                await ctx.send(content=content, embed=successEmbed, view=view, file=file, delete_after=delete_after)
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
                await ctx.reply(embed=errorEmbed, file=file)
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

async def errorLogging(bot, ctx: nextcord.Interaction, error: str):
    """
    Creates and sends an error embed for critical errors into the bot logging channel
    This is called when an error occurs

    Parameters
    -----------
    bot: :class:`nextcord.ext.commands.bot.Bot`
        The bot instance
    ctx: :class:`nextcord.Interaction`
        The interaction where the error occurred
    error: :class:`str`
        The error message that occurred
    """
    if type(bot) is not Bot:
        try:
            bot = bot.bot
        except Exception:
            return print("Error: Bot is not a bot or self")

    channel = bot.get_channel(botLoggingChannelID)
    errorEmbed = nextcord.Embed(
        color=nextcord.Color.red()
    )

    errorEmbed.add_field(name="<:icon_globe:960643612872417280> Guild", value=f"```ini\n{ctx.guild}```", inline=False)
    errorEmbed.add_field(name="<:icon_clide:960643699279265843> Command", value=f"```ini\n{ctx.message.content}```", inline=False)
    errorEmbed.add_field(name="<:icon_error_red:962068826311254177> Error", value=f"```python\n{error}```", inline=False)

    await channel.send(embed=errorEmbed)

async def devLogging(bot, ctx: nextcord.Interaction, text: str):
    if type(bot) is not Bot:
        try:
            bot = bot.bot
        except Exception:
            return print("Error: Bot is not a bot or self")
    channel = bot.get_channel(botLoggingChannelID)
    embed = nextcord.Embed(
        description=f"**{ctx.author} hat ein Befehl ausgeführt**",
        color=nextcord.Color.blurple()
    )

    embed.add_field(name="<:icon_globe:960643612872417280> Guild", value=f"```ini\n{ctx.guild}```", inline=False)
    embed.add_field(name="<:icon_clide:960643699279265843> Command", value=f"```ini\n{ctx.message.content}```", inline=False)
    embed.add_field(name="<:icon_tick:962067144877695016> Action", value=f"```css\n{text}```", inline=False)

    await channel.send(embed=embed)

async def permissionError(bot, ctx: nextcord.Interaction):
    with contextlib.suppress(Exception):
        if type(bot) is not Bot:
            try:
                bot = bot.bot
            except Exception:
                return print("Error: Bot is not a bot or self")

        emote = bot.get_emoji(962068826311254177)

        permissionEmbed = nextcord.Embed(
            description="> **Der Bot hat nicht genug Berechtigungen um in diesen Kanal zu schreiben.**",
            color=nextcord.Color.red()
        )

        await ctx.add_reaction(emote)
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(embed=permissionEmbed)

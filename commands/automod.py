import contextlib
from nextcord.ext import commands
from nextcord.ext.commands import Cog

from .utils.other import checkLink, getPrefixFromDatabase
from .utils.embeds import infoEmbed, errorEmbed, successEmbed
from .utils.database import delete, insert, readOne, readAll, update
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale

languageStrings = {}
class Automod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="badword", aliases=["bad-word", "bad_word", "wordblacklist", "word_blacklist", "word-blacklist", "badwords"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _badword(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne("prefix", "guilds", "guild_id", [ctx.guild.id])[0]
        
        await infoEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "badwordDescription", prefix))

    @_badword.command(name="add", aliases=["a"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _add(self, ctx, word):
        guildLocale = getGuildLanguage(ctx.guild.id)
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word.lower()])

        if exists is not None:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "badwordAlreadyExists", word))
        
        insert("badwords", "guild_id, word", [ctx.guild.id, word.lower()])
        
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "badwordAdded", word))

    @_badword.command(name="remove", aliases=["del", "delete"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _remove(self, ctx, word):
        guildLocale = getGuildLanguage(ctx.guild.id)
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word.lower()])

        if exists is None:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "badwordDoesntExist", word))
        
        delete("badwords", "guild_id word", [ctx.guild.id, word.lower()])
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "badwordRemoved", word))

    @_badword.command(name="list", aliases=["show"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _list(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        words = readAll("word", "badwords", "guild_id", [ctx.guild.id])

        if not words:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "badwordNoWords"))

        string = "".join(f"{word[0]}\n" for word in words)

        await infoEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "badwordList", string))

    @commands.group(name="ghostping", aliases=["ghost-ping", "ghost_ping"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _ghostping(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:Ghostping:1087448502323384330> Anti-Ghostpings**\n\n> `-ghostping on`\n> `-ghostping off`")
    
    @_ghostping.command(name="on", aliases=["activate", "activ"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _on(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if checkGhostOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "ghostpingAlreadyOn"))

        update("ghostping", "enabled", "guild_id", [1, ctx.guild.id])
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "ghostpingOn"))

    @_ghostping.command(name="off", aliases=["deactivate"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _off(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        if not checkGhostOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "ghostpingAlreadyOff"))

        update("ghostping", "enabled", "guild_id", [0, ctx.guild.id])
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "ghostpingOff"))

    @commands.group(name="linkblocker", aliases=["antilink", "anti-link", "link"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _linkblocker(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:Automod:1087440612430717068> Link Blocker**\n\n> `-linkblocker on`\n> `-linkblocker off`")

    @_linkblocker.command(name="on", aliases=["activate", "activ"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _on2(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if checkLinkOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "linkblockerAlreadyOn"))

        update("linkblocker", "enabled", "guild_id", [1, ctx.guild.id])
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "linkblockerOn"))

    @_linkblocker.command(name="off", aliases=["deactivate"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _off2(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if not checkLinkOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "linkblockerAlreadyOff"))

        update("linkblocker", "enabled", "guild_id", [0, ctx.guild.id])
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings ,guildLocale, "linkblockerOff"))

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if message.author.guild_permissions.administrator:
            return
        
        guildLocale = getGuildLanguage(message.guild.id)

        if checkLink(message.content.lower()):
            if not checkLinkOn(message.guild.id):
                return

            await infoEmbed(self.bot, message.channel, getLocale(self.bot, languageStrings , guildLocale, "linkblockerMessage"), delete_after=10)

            with contextlib.suppress(Exception):
                return await message.delete()
        
        if message.content.startswith(getPrefixFromDatabase(self.bot, message)):
            return

        words = readAll("word", "badwords", "guild_id", [message.guild.id])

        if all(word[0].lower() not in message.content.lower() for word in words):
            return
        
        await infoEmbed(self.bot, message.channel, getLocale(self.bot, languageStrings , guildLocale, "badwordMessage"), delete_after=10)
        with contextlib.suppress(Exception):
            await message.delete()

    @Cog.listener()
    async def on_raw_message_edit(self, payload):
        if not payload.guild_id:
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return

        if message.author.bot:
            return

        with contextlib.suppress(Exception):
            if self.bot.get_guild(payload.guild_id).get_member(payload.user_id).guild_permissions.administrator:
                return
        
        guildLocale = getGuildLanguage(message.guild.id)

        if checkLink(message.content.lower()):
            if not checkLinkOn(message.guild.id):
                return

            await infoEmbed(self.bot, message.channel, getLocale(self.bot, languageStrings , guildLocale, "linkblockerMessage"), delete_after=10)

            with contextlib.suppress(Exception):
                return await message.delete()

        words = readAll("word", "badwords", "guild_id", [message.guild.id])
        
        if any(word[0].lower() in message.content.lower() for word in words):
            await infoEmbed(self.bot, message.channel, getLocale(self.bot, languageStrings , guildLocale, "badwordMessage"), delete_after=10)
            with contextlib.suppress(Exception):
                await message.delete()

    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild:
            return
        
        if not message.mentions:
            return

        if not checkGhostOn(message.guild.id):
            return
        
        guildLocale = getGuildLanguage(message.guild.id)
        
        users = ""
        for i, member in enumerate(message.mentions):
            if i == 0: users += f"{member}"; continue
            users += f", {member}"
        
        await infoEmbed(self.bot, message.channel, getLocale(self.bot, languageStrings , guildLocale, "ghostpingMessage", message.author.mention, users))

def checkGhostOn(guildid: int) -> bool:
    enabled = readOne("enabled", "ghostping", "guild_id", [guildid])

    if enabled is None:
        insert("ghostping", "guild_id, enabled", [guildid, 0])
        return False
    
    return enabled[0] == 1

def checkLinkOn(guildid: int) -> bool:
    enabled = readOne("enabled", "linkblocker", "guild_id", [guildid])

    if enabled is None:
        insert("linkblocker", "guild_id, enabled", [guildid, 0])
        return False

    return enabled[0] == 1

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("automod")
    bot.add_cog(Automod(bot))
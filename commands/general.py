import psutil
import platform
import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time
from .utils.language import getGuildLanguage, updateGuildLanguage, getLanguageStrings, getLocale
from .utils.embeds import errorEmbed, successEmbed, infoEmbed
from .utils.database import readOne, insert, update

languageStrings = {}
class General(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="botinfo", aliases=['bot', 'info', 'stats'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _botinfo(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        version, uptime = readOne(columns="version, uptime", table="elli")
        timeUp = time() - float(uptime)
        days = timeUp / 86400
        hours = (timeUp / 3600) % 24
        minutes = (timeUp / 60) % 60

        await infoEmbed(
            self,
            ctx,
            getLocale(self.bot, languageStrings, guildLocale, "botinfoDescription", self.bot.user.name, len(self.bot.guilds), sum(len(s.members) for s in self.bot.guilds), round(self.bot.latency * 1000), psutil.cpu_percent(), round(psutil.virtual_memory().percent), round(days), round(hours), round(minutes), version, nextcord.__version__, platform.python_version(), platform.system(), platform.release(), platform.machine(), platform.processor(), platform.version(), platform.uname().node, platform.uname().machine, platform.uname().processor, platform.uname().system, platform.uname().version, platform.uname().release, platform.uname().node, platform.uname().machine, platform.uname().processor, platform.uname().system, platform.uname().version, platform.uname().release),
            footer={"text": getLocale(self.bot, languageStrings, guildLocale, "botinfoFooter", self.bot.user.name), "icon_url":"https://avatars.githubusercontent.com/u/89693200?s=280&v=4"},
            thumbnail=self.bot.user.display_avatar.url)
        
    @commands.command(name="prefix", aliases=['setprefix'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def _prefix(self, ctx, prefix):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if "<:" in prefix or "<a:" in prefix or "<@" in prefix or "<#" in prefix:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "noMentionsOrEmotesInPrefix"))
        
        if len(prefix) > 4:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "prefixTooLong"))
        
        if "`" in prefix:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "noBackticksInPrefix"))

        oldPrefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])

        if oldPrefix is None:
            insert(table="guilds", columns="guild_id, prefix", values=[ctx.guild.id, prefix])
            return await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "prefixSet", prefix, "-"))

        if prefix == oldPrefix[0]:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "prefixSameAsOld", oldPrefix[0]))

        update(table="guilds", columns="prefix", where="guild_id", values=[prefix, ctx.guild.id])

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "prefixSet", prefix, oldPrefix[0]))
        
    @nextcord.slash_command(name="prefix", description="Set the prefix for this guild.", description_localizations={nextcord.Locale.de: "Setze die Prefix für diesen Server."}, default_member_permissions=nextcord.Permissions(manage_guild=True))
    async def _prefixSlash(self, interaction, prefix: str):
        guildLocale = getGuildLanguage(interaction.guild.id)

        if "<:" in prefix or "<a:" in prefix or "<@" in prefix or "<#" in prefix:
            return await errorEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "noMentionsOrEmotesInPrefix"))
        
        if len(prefix) > 4:
            return await errorEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "prefixTooLong"))
        
        if "`" in prefix:
            return await errorEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "noBackticksInPrefix"))

        oldPrefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[interaction.guild.id])

        if oldPrefix is None:
            insert(table="guilds", columns="guild_id, prefix", values=[interaction.guild.id, prefix])
            return await successEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "prefixSet", prefix, "-"))

        if prefix == oldPrefix[0]:
            return await errorEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "prefixSameAsOld", oldPrefix[0]))

        update(table="guilds", columns="prefix", where="guild_id", values=[prefix, interaction.guild.id])

        await successEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "prefixSet", prefix, oldPrefix[0]))

    @commands.command(name="language", aliases=['setlanguage', 'lang', 'setlang'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def _language(self, ctx, language):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if language not in ["de", "en"]:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "onlyAvailableLanguages", language, "de (german), en (english)"))

        oldLanguage = getGuildLanguage(ctx.guild.id)

        if language == oldLanguage:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "languageSameAsOld", oldLanguage))

        updateGuildLanguage(ctx.guild.id, language)

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, language, "languageSet", language, oldLanguage))
        
    @nextcord.slash_command(name="language", description="Set the language for this guild.", description_localizations={nextcord.Locale.de: "Setze die Sprache für diesen Server."}, default_member_permissions=nextcord.Permissions(manage_guild=True))
    async def _languageSlash(self, interaction,
        
        language: str = nextcord.SlashOption(description="The language to set.", description_localizations={nextcord.Locale.de: "Die Sprache, die gesetzt werden soll."},
            choices={"English": "en", "German": "de"}
        )):
        guildLocale = getGuildLanguage(interaction.guild.id)

        if language not in ["de", "en"]:
            return await errorEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "onlyAvailableLanguages", language, "de (german), en (english)"))

        oldLanguage = getGuildLanguage(interaction.guild.id)

        if language == oldLanguage:
            return await errorEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "languageSameAsOld", oldLanguage))

        updateGuildLanguage(interaction.guild.id, language)

        await successEmbed(self, interaction, getLocale(self.bot, languageStrings, language, "languageSet", language, oldLanguage))
        

    @commands.command(name="invite")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _invite(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)

        await infoEmbed(
            self,
            ctx,
            getLocale(self.bot, languageStrings, guildLocale, "inviteDescription", self.bot.user.id),
        )
        
    @nextcord.slash_command(name="invite", description="Get the invite link for this bot.", description_localizations={nextcord.Locale.de: "Erhalte den Einladungslink für diesen Bot."})
    async def _inviteSlash(self, interaction):
        guildLocale = getGuildLanguage(interaction.guild.id)

        await infoEmbed(
            self,
            interaction,
            getLocale(self.bot, languageStrings, guildLocale, "inviteDescription", self.bot.user.id),
        )
    
    @commands.command(name="support")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _support(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**<:Commands:1087442278118871140> Support**\n\n> **Support:** [`🔗` Support](https://discord.gg/FWPExbfCTa)"
        )
        
    @nextcord.slash_command(name="support", description="Get the support server for this bot.", description_localizations={nextcord.Locale.de: "Erhalte den Supportserver für diesen Bot."})
    async def _supportSlash(self, interaction):
        await infoEmbed(
            self,
            interaction,
            f"**<:Commands:1087442278118871140> Support**\n\n> **Support:** [`🔗` Support](https://discord.gg/FWPExbfCTa)"
        )
    
    @commands.command(name="vote")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _vote(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**<:Commands:1087442278118871140> Vote**\n\n> **Vote:** [`🔗` Vote](https://top.gg/bot/763778168825053254/vote)"
        )
        
    @nextcord.slash_command(name="vote", description="Get the vote link for this bot.", description_localizations={nextcord.Locale.de: "Erhalte den Vote-Link für diesen Bot."})
    async def _voteSlash(self, interaction):
        await infoEmbed(
            self,
            interaction,
            f"**<:Commands:1087442278118871140> Vote**\n\n> **Vote:** [`🔗` Vote](https://top.gg/bot/763778168825053254/vote)"
        )
        
    @commands.command(name="privacy", aliases=['tos', 'terms', 'termsandconditions', 'datenschutz', 'datenschutzerklärung'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _privacy(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        await infoEmbed(
            self,
            ctx,
            getLocale(self.bot, languageStrings, guildLocale, "privacyDescription"),
        )
    
    @nextcord.slash_command(name="privacy", description="Get the privacy policy for this bot.", description_localizations={nextcord.Locale.de: "Erhalte die Datenschutzerklärung für diesen Bot."})
    async def _privacySlash(self, interaction):
        guildLocale = getGuildLanguage(interaction.guild.id)
        
        await infoEmbed(
            self,
            interaction,
            getLocale(self.bot, languageStrings, guildLocale, "privacyDescription"),
        )

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("general")
    bot.add_cog(General(bot))
import psutil
import platform
import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time
from .utils.language import getGuildLanguage, updateGuildLanguage, getLanguageStrings, getLocale
from .utils.embeds import errorEmbed, successEmbed, infoEmbed
from .utils.database import readOne, insert, update

class General(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="botinfo", aliases=['bot', 'info', 'stats'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _botinfo(self, ctx):
        version, uptime = readOne(columns="version, uptime", table="elli")
        timeUp = time() - float(uptime)
        days = timeUp / 86400
        hours = (timeUp / 3600) % 24
        minutes = (timeUp / 60) % 60

        await infoEmbed(
            self,
            ctx,
            f"**<:Statistics:1087458133569445970> {self.bot.user.name}'s aktuelle Statistiken**\n\n> **<:Globe:1087448923834163342> Server:** `{len(self.bot.guilds)}`\n> **<:Member:1087452536295927808> User:** `{sum(len(s.members) for s in self.bot.guilds)}`\n> **<:Server:1087457941348700251> Latenz:** `{round(self.bot.latency * 1000)}ms`\n\n> **<:Clyde:1087435842785640448> CPU:** `{psutil.cpu_percent()}%`\n> **<:Folder:1087447065061240896> RAM:** `{round(psutil.virtual_memory().percent)}%`\n> **<:Stopwatch:1087458252750590073> Uptime:** `{round(days)}d {round(hours)}h {round(minutes)}m`\n\n> **<:Developer:1087444095363989564> Version:** `{version}`\n> **<:Nextcord:1087456587003740210> Nextcord:** `{nextcord.__version__}`\n> **<:Python:1087457407220850788> Python:** `{platform.python_version()}`",
            footer={"text": f"{self.bot.user.name} Bot | Powered by Nextcord", "icon_url":"https://avatars.githubusercontent.com/u/89693200?s=280&v=4"},
            thumbnail=self.bot.user.display_avatar.url)
        
    @commands.command(name="prefix", aliases=['setprefix'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def _prefix(self, ctx, prefix):
        if "<:" in prefix or "<a:" in prefix or "<@" in prefix or "<#" in prefix:
            return await errorEmbed(self, ctx, "Es dürfen keine Markierungen oder Emotes in der Prefix sein.")
        if len(prefix) > 4:
            return await errorEmbed(self, ctx, "Die Prefix darf nicht länger als 4 Zeichen lang sein.")
        if "`" in prefix:
            return await errorEmbed(self, ctx, "Die Prefix darf kein ` enthalten.")

        oldPrefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])

        if oldPrefix is None:
            insert(table="guilds", columns="guild_id, prefix", values=[ctx.guild.id, prefix])
            return await successEmbed(self, ctx, f"**<:Commands:1087442278118871140>  Prefix gesetzt**\n\n> **Prefix:** `{prefix}`\n> **Alte Prefix:** `-`")

        if prefix == oldPrefix[0]:
            return await errorEmbed(ctx, f"Die Prefix darf nicht die selbe wie de alte sein `{oldPrefix[0]}`.")

        update(table="guilds", columns="prefix", where="guild_id", values=[prefix, ctx.guild.id])

        await successEmbed(self, ctx, f"**<:Commands:1087442278118871140> Prefix gesetzt**\n\n> **Prefix:** `{prefix}`\n> **Alte Prefix:** `{oldPrefix[0]}`")

    @commands.command(name="language", aliases=['setlanguage', 'lang', 'setlang'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def _language(self, ctx, language):
        if language not in ["de", "en"]:
            return await errorEmbed(self, ctx, "The only available languages are `de` (german) and `en` (english).")

        oldLanguage = getGuildLanguage(ctx.guild.id)

        if language == oldLanguage:
            return await errorEmbed(self, ctx, f"The language can't be the same as the old one `{oldLanguage[0]}`.")

        updateGuildLanguage(ctx.guild.id, language)

        await successEmbed(self, ctx, f"**<:Commands:1087442278118871140> Sprache set**\n\n> **Language:** `{language}`\n> **Old Language:** `{oldLanguage}`")

    @commands.command(name="invite")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _invite(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**<:Commands:1087442278118871140> Invite**\n\n> **Empfohlen:** [`🔗` Invite](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=279138790647)\n> **Admin:** [`🔗` Invite](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8)"
        )
    
    @commands.command(name="support")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _support(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**<:Commands:1087442278118871140> Support**\n\n> **Support:** [`🔗` Support](https://discord.gg/FWPExbfCTa)"
        )
    
    @commands.command(name="vote")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _vote(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**<:Commands:1087442278118871140> Vote**\n\n> **Vote:** `Hier scheint wohl noch etwas zu fehlen.`"
        )

def setup(bot):
    bot.add_cog(General(bot))
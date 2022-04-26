import psutil
import platform
import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time
from .utils.embeds import errorEmbed, successEmbed, infoEmbed
from .utils.database import readOne, insert, update

class general(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="botinfo", aliases=['bot', 'info', 'stats'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _botinfo(self, ctx):
        version, uptime = readOne(columns="version, uptime", table="cursy")
        timeUp = time() - float(uptime)
        days = timeUp / 86400
        hours = (timeUp / 3600) % 24
        minutes = (timeUp / 60) % 60

        await infoEmbed(
            self,
            ctx,
            f"**<:icon_stats:966088119378141194> {self.bot.user.name}'s aktuelle Statistiken**\n\n> **<:icon_globe:960643612872417280> Server:** `{len(self.bot.guilds)}`\n> **<:icon_member:960643575366955079> User:** `{sum(len(s.members) for s in self.bot.guilds)}`\n> **<:icon_server:960643654492491786> Latenz:** `{round(self.bot.latency * 1000)}ms`\n\n> **<:icon_clide:960643699279265843> CPU:** `{psutil.cpu_percent()}%`\n> **<:icon_folder:962093232701988925> RAM:** `{round(psutil.virtual_memory().percent)}%`\n> **<:icon_stopwatch:959548515799953488> Uptime:** `{round(days)}d {round(hours)}h {round(minutes)}m`\n\n> **<:icon_developer:960643728140284004> Version:** `{version}`\n> **<:icon_nextcord:960645392075210862> Nextcord:** `{nextcord.__version__}`\n> **<:icon_python:960645429257699398> Python:** `{platform.python_version()}`",
            footer={"text": f"{self.bot.user.name} Bot | Powered by Nextcord", "icon_url":"https://avatars.githubusercontent.com/u/89693200?s=280&v=4"})
        
    @commands.command(name="prefix", aliases=['setprefix'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def _prefix(self, ctx, prefix):
        if "<:" in prefix or "<a:" in prefix or "<@" in prefix or "<#" in prefix:
            return await errorEmbed(self, ctx, "Es dürfen keine Markierungen oder Emotes in der Prefix sein.")
        if len(prefix) > 4:
            return await errorEmbed(self, ctx, "Die Prefix darf nicht länger als 4 Zeichen lang sein.")

        oldPrefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])

        if oldPrefix is None:
            insert(table="guilds", columns="guild_id, prefix", values=[ctx.guild.id, prefix])
            return await successEmbed(self, ctx, f"**<:icon_commands:966028792890003547>  Prefix gesetzt**\n\n> **Prefix:** `{prefix}`\n> **Alte Prefix:** `-`")

        if prefix == oldPrefix[0]:
            return await errorEmbed(ctx, f"Die Prefix darf nicht die selbe wie de alte sein `{oldPrefix[0]}`.")

        update(table="guilds", columns="prefix", where="guild_id", values=[prefix, ctx.guild.id])

        await successEmbed(self, ctx, f"**<:icon_commands:966028792890003547> Prefix gesetzt**\n\n> **Prefix:** `{prefix}`\n> **Alte Prefix:** `{oldPrefix[0]}`")

    @commands.command(name="invite")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _invite(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**<:icon_invite:966028792890003547> Invite**\n\n> **Invite:** `Hier scheint wohl noch etwas zu fehlen.`"
        )
    
    @commands.command(name="support")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _support(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**<:icon_support:966028792890003547> Support**\n\n> **Support:** `Hier scheint wohl noch etwas zu fehlen.`"
        )

def setup(bot):
    bot.add_cog(general(bot))
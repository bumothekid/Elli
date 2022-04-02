import nextcord
import sqlite3
import psutil
import platform
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time

class botInfo(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="botinfo", aliases=['bot', 'info', 'stats'])
    async def _botinfo(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT uptime FROM cursy")
        uptime = c.fetchone()[0]
        c.execute("SELECT version FROM cursy")
        version = c.fetchone()[0]
        timeUp = time() - float(uptime)
        days = timeUp / 86400
        hours = (timeUp / 3600) % 24
        minutes = (timeUp / 60) % 60
        seconds = timeUp % 60
        embed=nextcord.Embed(
            color=nextcord.Color.blurple()
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
        embed.add_field(name="<:Servers:959546817324916796> Server", value=f"`{len(self.bot.guilds)}` Server", inline=True)
        embed.add_field(name="<:Member:959547196762632212> User", value=f"`{sum(len(s.members) for s in self.bot.guilds)}` User", inline=True)
        embed.add_field(name="<:Channels:959547002335682600> Channel", value=f"`{sum(1 for g in self.bot.guilds for _ in g.channels)}` Channel", inline=True)
        embed.add_field(name="<a:Loading:959548386594390036> Latency", value=f"`{round(self.bot.latency * 1000)}`ms")
        embed.add_field(name="<:Uptime:959548515799953488> Uptime", value=f"`{days:.0f}`d `{hours:.0f}`h `{minutes:.0f}`m")
        embed.add_field(name="<:Server:959548564231565393> CPU", value=f"`{psutil.cpu_percent()}`%")
        embed.add_field(name="<:Version:959548722147110942> Version", value=f"`{version}` Version", inline=True)
        embed.add_field(name="<:Nextcord:959549287870627900> Nextcord", value=f"`{nextcord.__version__}` Version", inline=True)
        embed.add_field(name="<:python:959534353283678298> Python", value=f"`{platform.python_version()}` Version", inline=True)
        embed.set_footer(text="Cursy Bot | Powered by Nextcord", icon_url="https://avatars.githubusercontent.com/u/89693200?s=280&v=4")
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(botInfo(bot))
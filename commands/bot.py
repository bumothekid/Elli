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
    @commands.cooldown(2, 20, commands.BucketType.user)
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

        embed=nextcord.Embed(
            description=f"**{self.bot.user.name}'s current Stats**\n\n> **<:icon_globe:960643612872417280> Guilds:** `{len(self.bot.guilds)}`\n> **<:icon_member:960643575366955079> Users:** `{sum(len(s.members) for s in self.bot.guilds)}`\n> **<:icon_server:960643654492491786> Latency:** `{round(self.bot.latency * 1000)}ms`\n\n> **<:icon_clide:960643699279265843> CPU:** `{psutil.cpu_percent()}%`\n> **<:icon_folder:962093232701988925> RAM:** `{round(psutil.virtual_memory().percent)}%`\n> **<:icon_stopwatch:959548515799953488> Uptime:** `{round(days)}d {round(hours)}h {round(minutes)}m`\n\n> **<:icon_developer:960643728140284004> Version:** `{version}`\n> **<:icon_nextcord:960645392075210862> Nextcord:** `{nextcord.__version__}`\n> **<:icon_python:960645429257699398> Python:** `{platform.python_version()}`",
            color=nextcord.Color.blurple()
        )
        embed.set_footer(text="Cursy Bot | Powered by Nextcord", icon_url="https://avatars.githubusercontent.com/u/89693200?s=280&v=4")
        
        await ctx.reply(embed=embed)

    @commands.command(name="prefix", aliases=['setprefix'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def _prefix(self, ctx, prefix):
        if len(prefix) > 4:
            await ctx.reply("Prefix nicht länger als 4 zeichen lang.")
            return

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (ctx.guild.id,))
        oldPrefix = c.fetchone()

        if oldPrefix is None:
            c.execute("INSERT INTO guilds(guild_id, prefix) VALUES (?, ?)", (ctx.guild.id, prefix)),
            db.commit()

            return await ctx.reply(f"Prefix wurde erfolgreich gesetzt auf gesetzt `{prefix}`")

        if prefix == oldPrefix[0]:
            await ctx.reply(f"Die prefix darf nicht die selbe wie die alte sein `{oldPrefix[0]}`")
            return

        c.execute("UPDATE guilds SET prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        db.commit()

        await ctx.reply(f"Prefix wurde erfolgreich gesetzt auf gesetzt `{prefix}`")

    @Cog.listener()
    async def on_guild_join(self, guild):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (guild.id,))
        prefix = c.fetchone()

        if prefix is None:
            c.execute("INSERT INTO guilds(guild_id, prefix) VALUES (?, ?)", (guild.id, "-"))
            db.commit()


def setup(bot):
    bot.add_cog(botInfo(bot))
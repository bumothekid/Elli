# Import
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
import sqlite3
import re

class deveveloper(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="dev", invoke_without_command=True)
    async def _dev(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)

        if str(ctx.author.id) not in devlist:
            raise commands.NotOwner

        embed = nextcord.Embed(
            description="**<:icon_developer:960643728140284004> Developer Commands**\n\n> `-dev add <user>` | Füge einen Developer hinzu\n> `-dev remove <user>` | Entferne einen Developer\n> `-dev show` | Zeigt dir alle Developer\n> `-dev version <version>` | Setzt die neue Version\n> `-load <file>` | Lädt ein Modul\n> `-unload <file>`| Entlädt ein Modul\n> `-reload <file>` | Lädt ein Modul neu\n",
            color=nextcord.Color.blurple()
        )

        await ctx.reply(embed=embed)

    @_dev.command(name="add")
    async def _add(self, ctx, user: nextcord.User):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)

        if str(ctx.author.id) not in devlist:
            raise commands.NotOwner

        if str(user.id) in devlist:
            return await devEmbed(ctx, False, f"{user.mention} ist bereits als developer registriert.")

        if user.system == True or user.bot == True:
            return await devEmbed(ctx, False, "Du kannst keinen Bot als developer registrieren.")

        devs_new = f"{devs}, {user.id}"
        c.execute("UPDATE cursy SET developer = ?", [devs_new])

        await devEmbed(ctx, True, text=f"{user.mention} wurde als developer registriert")
        await devLogging(self.bot, ctx, f"{user.mention} wurde von {ctx.author} als developer registriert")
        db.commit()

    @_dev.command(name="remove")
    async def _remove(self, ctx, user: nextcord.User):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)

        if str(ctx.author.id) not in devlist:
            raise commands.NotOwner

        if str(user.id) not in devlist:
            return await devEmbed(ctx, False, f"{user.mention} ist nicht als developer registriert.")

        devs_new = str(devs.replace(f", {user.id}", ""))
        c.execute("UPDATE cursy SET developer = ?", [devs_new])

        await devEmbed(ctx, True, f"{user.mention} wurde als developer entfernt")
        await devLogging(bot=self.bot, ctx=ctx, text=f"{user} wurde von {ctx.author} als Developer entfernt.")
        db.commit()
    
    @_dev.command(name="show", aliases=["list"])
    async def show(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)

        if str(ctx.author.id) not in devlist:
            raise commands.NotOwner

        lists = ''

        for dev in devlist:
            user = self.bot.get_user(int(dev))
            lists += f'<:icon_developer:960643728140284004> | {user}\n'

        await devEmbed(ctx, True, lists)

    @_dev.command(name="version")
    async def version(self, ctx, *, version):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)

        if str(ctx.author.id) not in devlist:
            raise commands.NotOwner

        c.execute("SELECT version FROM cursy")
        vers = c.fetchone()[0]
        c.execute("UPDATE cursy SET version = ?", [version])

        await devEmbed(ctx, True, f"Cursy wurde auf die {version} Version geupdated.\n> **Alte Version:** {vers}")
        await devLogging(bot=self.bot, ctx=ctx, text=f"{ctx.author} hat die Bot Version von {vers} auf {version} gesetzt.")
        db.commit()
        
async def devEmbed(ctx, success: bool, text: str):
    return await ctx.reply(embed=nextcord.Embed(description=text, color=nextcord.Color.green() if success else nextcord.Color.red()))
        
async def devLogging(bot, ctx, text: str):
    channel = bot.get_channel(957444324080115762)

    embed = nextcord.Embed(
        description=f"**{ctx.author} hat ein Befehl ausgeführt**",
        color=nextcord.Color.blurple()
    )

    embed.add_field(name="<:icon_globe:960643612872417280> Guild", value=f"```ini\n{ctx.guild}```", inline=False)
    embed.add_field(name="<:icon_clide:960643699279265843> Command", value=f"```ini\n{ctx.message.content}```", inline=False)
    embed.add_field(name="<:icon_tick:962067144877695016> Action", value=f"```css\n{text}```", inline=False)

    await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(deveveloper(bot))
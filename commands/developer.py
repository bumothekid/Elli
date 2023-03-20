# Import
import nextcord
import re
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.other import devCheck
from .utils.embeds import infoEmbed, successEmbed, errorEmbed, devLogging
from .utils.database import readOne, update

class deveveloper(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="dev", invoke_without_command=True)
    async def _dev(self, ctx):
        if not devCheck(ctx.author.id):
            raise commands.NotOwner

        await infoEmbed(self, ctx, "**<:Developer:1087444095363989564> Developer Commands**\n\n> `-dev add <user>` | Füge einen Developer hinzu\n> `-dev remove <user>` | Entferne einen Developer\n> `-dev show` | Zeigt dir alle Developer\n> `-dev version <version>` | Setzt die neue Version\n> `-load <file>` | Lädt ein Modul\n> `-unload <file>`| Entlädt ein Modul\n> `-reload <file>` | Lädt ein Modul neu\n")

    @_dev.command(name="add")
    async def _add(self, ctx, user: nextcord.User):
        if not devCheck(ctx.author.id):
            raise commands.NotOwner

        devs = readOne(columns="developer", table="elli")
        devlist = re.findall(r"[0-9]+", devs[0])

        if str(user.id) in devlist:
            return await errorEmbed(self, ctx, f"{user.mention} ist bereits als Developer regestriert.")

        if user.system == True or user.bot == True:
            return await errorEmbed(self, ctx, "Du kannst keine Bots als Developer regestrieren.")

        devs_new = f"{devs[0]}, {user.id}"
        update(table="elli", columns="developer", values=[devs_new])

        await successEmbed(self, ctx, f"{user.mention} wurde als Developer regestriert.")
        await devLogging(self, ctx, f"{user} wurde von {ctx.author} als developer registriert")

    @_dev.command(name="remove")
    async def _remove(self, ctx, user: nextcord.User):
        if not devCheck(ctx.author.id):
            raise commands.NotOwner

        devs = readOne(columns="developer", table="elli")
        devlist = re.findall(r"[0-9]+", devs[0])

        if str(user.id) not in devlist:
            return await errorEmbed(self, ctx, f"{user.mention} ist nicht als Developer registriert.")

        devs_new = str(devs[0].replace(f", {user.id}", ""))
        update(table="elli", columns="developer", values=[devs_new])

        await successEmbed(self, ctx, f"{user.mention} wurde als Developer entfernt.")
        await devLogging(self, ctx, f"{user} wurde von {ctx.author} als Developer entfernt.")
    
    @_dev.command(name="show", aliases=["list"])
    async def show(self, ctx):
        if not devCheck(ctx.author.id):
            raise commands.NotOwner

        devs = readOne(columns="developer", table="elli")
        devlist = re.findall(r"[0-9]+", devs[0])
        lists = ''

        for dev in devlist:
            user = self.bot.get_user(int(dev))
            lists += f'<:Developer:1087444095363989564> | {user}\n'

        await infoEmbed(self, ctx, lists)

    @_dev.command(name="version")
    async def version(self, ctx, *, version):
        if not devCheck(ctx.author.id):
            raise commands.NotOwner

        vers = readOne(columns="version", table="elli")

        update(table="elli", columns="version", values=[version])


        await successEmbed(self, ctx, f"{self.bot.user.name} wurde auf die `{version}` Version gesetzt.\n> **Alte Version:** `{vers[0]}`")
        await devLogging(self, ctx, f"{ctx.author} hat die Bot Version von {vers[0]} auf {version} gesetzt.")

def setup(bot):
    bot.add_cog(deveveloper(bot))
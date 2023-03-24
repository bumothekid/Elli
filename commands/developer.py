# Import
import time
import nextcord
import re
import platform
import psutil
from nextcord.ext.commands import Cog
from nextcord.ext import commands, tasks
from .utils.other import devCheck
from .utils.embeds import infoEmbed, successEmbed, errorEmbed, devLogging
from .utils.database import readOne, update

class Developer(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.updateStatsLoop.start()

    @commands.group(name="dev", invoke_without_command=True)
    async def _dev(self, ctx):
        if not devCheck(ctx.author.id):
            raise commands.NotOwner

        await infoEmbed(self, ctx, "**<:Developer:1087444095363989564> Developer Commands**\n\n> `-dev add <user>` | Füge einen Developer hinzu\n> `-dev remove <user>` | Entferne einen Developer\n> `-dev show` | Zeigt dir alle Developer\n> `-dev version <version>` | Setzt die neue Version\n> `-dev setStatsChannel <#channel>` | Setzt einen neuen Stats Channel\n> `-load <file>` | Lädt ein Modul\n> `-unload <file>`| Entlädt ein Modul\n> `-reload <file>` | Lädt ein Modul neu\n")

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


    @_dev.command(name="setStatsChannel")
    async def setStatsChannel(self, ctx, channel: nextcord.TextChannel):
        if not devCheck(ctx.author.id):
            raise commands.NotOwner

        uptime = readOne("uptime", "elli")[0]
        timeUp = time.time() - float(uptime)
        days = timeUp / 86400
        hours = (timeUp / 3600) % 24
        minutes = (timeUp / 60) % 60

        version = readOne("version", "elli")[0]

        embed = nextcord.Embed(color=nextcord.Color.blurple())
        embed.set_author(name="Elli", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="<:Globe:1087448923834163342> Server", value=f"`{len(self.bot.guilds)}` Server", inline=True)
        embed.add_field(name="<:Member:1087452536295927808> User", value=f"`{sum(len(s.members) for s in self.bot.guilds)}` User", inline=True)
        embed.add_field(name="<:Server:1087457941348700251> Latenz", value=f"`{round(self.bot.latency * 1000)}`ms")
        embed.add_field(name="<:Stopwatch:1087458252750590073> Uptime", value=f"`{days:.0f}`d `{hours:.0f}`h `{minutes:.0f}`m")
        embed.add_field(name="<:Folder:1087447065061240896> RAM", value=f"`{psutil.virtual_memory().percent}`%")
        embed.add_field(name="<:Clyde:1087435842785640448> CPU", value=f"`{psutil.cpu_percent()}`%")
        embed.add_field(name="<:Upvote:1088502844564447266> Vote", value="Vote for me: [Vote]() *Soon!*", inline=True)
        embed.add_field(name="<:Invite:1088502838331715624> Invite", value=f"Invite me: [Invite](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=279138790647)", inline=True)
        embed.add_field(name="<a:Donate:1088502831457243196> Donate", value="Donate for me: [Donate]() *Soon!*", inline=True)
        embed.add_field(name="<:Developer:1087444095363989564> Version", value=f"`{version}` Version", inline=True)
        embed.add_field(name="<:Nextcord:1087456587003740210> Nextcord", value=f"`{nextcord.__version__}` Version", inline=True)
        embed.add_field(name="<:Python:1087457407220850788> Python", value=f"`{platform.python_version()}` Version", inline=True)

        embed.set_footer(text="Elli Bot | Powered by Nextcord - This stats update every 5 minutes.", icon_url="https://avatars.githubusercontent.com/u/89693200?s=280&v=4")

        msg = await channel.send(embed=embed)

        update("elli", "statsChannel", values=f"{channel.id}, {msg.id}")

    @tasks.loop(minutes=5)
    async def updateStatsLoop(self):
        await self.bot.wait_until_ready()
        result = readOne("statsChannel", "elli")

        if result is None or result[0] is None:
            return

        channelID, messageID = result[0].split(", ")

        channel = self.bot.get_channel(int(channelID))
        message = await channel.fetch_message(int(messageID))

        uptime = readOne("uptime", "elli")[0]
        timeUp = time.time() - float(uptime)
        days = timeUp / 86400
        hours = (timeUp / 3600) % 24
        minutes = (timeUp / 60) % 60

        version = readOne("version", "elli")[0]

        embed = nextcord.Embed(color=nextcord.Color.blurple())
        embed.set_author(name="Elli", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="<:Globe:1087448923834163342> Server", value=f"`{len(self.bot.guilds)}` Server", inline=True)
        embed.add_field(name="<:Member:1087452536295927808> User", value=f"`{sum(len(s.members) for s in self.bot.guilds)}` User", inline=True)
        embed.add_field(name="<:Server:1087457941348700251> Latenz", value=f"`{round(self.bot.latency * 1000)}`ms")
        embed.add_field(name="<:Stopwatch:1087458252750590073> Uptime", value=f"`{days:.0f}`d `{hours:.0f}`h `{minutes:.0f}`m")
        embed.add_field(name="<:Folder:1087447065061240896> RAM", value=f"`{psutil.virtual_memory().percent}`%")
        embed.add_field(name="<:Clyde:1087435842785640448> CPU", value=f"`{psutil.cpu_percent()}`%")
        embed.add_field(name="<:Upvote:1088502844564447266> Vote", value="Vote for me: [Vote]() *Soon!*", inline=True)
        embed.add_field(name="<:Invite:1088502838331715624> Invite", value=f"Invite me: [Invite](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=279138790647)", inline=True)
        embed.add_field(name="<a:Donate:1088502831457243196> Donate", value="Donate for me: [Donate]() *Soon!*", inline=True)
        embed.add_field(name="<:Developer:1087444095363989564> Version", value=f"`{version}` Version", inline=True)
        embed.add_field(name="<:Nextcord:1087456587003740210> Nextcord", value=f"`{nextcord.__version__}` Version", inline=True)
        embed.add_field(name="<:Python:1087457407220850788> Python", value=f"`{platform.python_version()}` Version", inline=True)

        embed.set_footer(text="Elli Bot | Powered by Nextcord - This stats update every 5 minutes.", icon_url="https://avatars.githubusercontent.com/u/89693200?s=280&v=4")

        await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(Developer(bot))
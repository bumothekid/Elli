# Import
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .loggingHelper import developerLogging
import sqlite3
import re

class deveveloper(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.developerLoggingChannel = self.bot.get_channel(957444324080115762)

    @commands.group(name="dev", invoke_without_command=True)
    async def _dev(self, interaction):
        """
        This function is called when the user types in the command "dev"
        
        :param interaction: The interaction object that triggered this command
        """
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)
        if str(interaction.author.id) not in devlist:
            embed = nextcord.Embed(
                description="Du bist kein developer!",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        embed = nextcord.Embed(
            color=0x7EF54C
        )

        embed.add_field(name="<:developer:957434132051394580> Developer", value="`!dev add <user>` | Füge einen Developer hinzu\n`!dev remove <user>` | Entferne einen Developer\n`!dev show` | Zeigt dir alle Developer\n`!dev version <version>` | Setzt die neue Version\n`!load <file>` | Lädt ein Modul\n`!unload <file>`| Entlädt ein Modul\n`!reload <file>` | Lädt ein Modul neu\n", inline=True)
        await interaction.reply(embed=embed)

    @_dev.command(name="add")
    async def _add(self, interaction, user: nextcord.User):
        """
        It adds a user to the list of developers
        
        :param interaction: The interaction object that started this command
        :param user: The user that the interaction is being executed on
        :type user: nextcord.User
        :return: A string.
        """
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)
        if str(interaction.author.id) not in devlist:
            embed = nextcord.Embed(
                description="Du bist kein developer!",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        if str(user.id) in devlist:
            embed = nextcord.Embed(
                description=f"{user.mention} ist bereits als developer registriert.",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        if user.system == True or user.bot == True:
            embed = nextcord.Embed(
                description="Du kannst nicht einen Bot als developer registrieren.",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        devs_new = f"{devs}, {user.id}"
        c.execute("UPDATE cursy SET developer = ?", [devs_new])
        embed = nextcord.Embed(
            description=f"{user.mention} wurde als developer egestriert.",
            color=0x7EF54C
        )
        await interaction.reply(embed=embed)
        embed = await developerLogging(interaction=interaction, text=f"{interaction.author} hat {user} als Developer regestriert.")
        await self.developerLoggingChannel.send(embed=embed)
        db.commit()

    @_dev.command(name="remove")
    async def _remove(self, interaction, user: nextcord.User):
        """
        It removes a user from the developer list
        
        :param interaction: The interaction object that started this command
        :param user: The user that the command was used on
        :type user: nextcord.User
        :return: A string
        """
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)
        if str(interaction.author.id) not in devlist:
            embed = nextcord.Embed(
                description="Du bist kein developer!",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        if str(user.id) not in devlist:
            embed = nextcord.Embed(
                description=f"{user.mention} ist nicht als eveloper registriert.",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        devs_new = str(devs.replace(f", {user.id}", ""))
        c.execute("UPDATE cursy SET developer = ?", [devs_new])
        embed = nextcord.Embed(
            description=f"{user.mention} wurde als Developer entfernt.",
            color=0x7EF54C
        )
        await interaction.reply(embed=embed)
        embed = await developerLogging(interaction=interaction, text=f"{interaction.author} hat {user} als Developer entfernt.")
        await self.developerLoggingChannel.send(embed=embed)
        db.commit()
    
    @_dev.command(name="show")
    async def show(self, interaction):
        """
        It shows the developers of the bot
        
        :param interaction: The interaction object that called this command
        """
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)
        if str(interaction.author.id) not in devlist:
            embed = nextcord.Embed(
                description="Du bist kein developer!",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        lists = ''
        for dev in devlist:
            user = self.bot.get_user(int(dev))
            lists += f'<:developer:957434132051394580> | {user}\n'
        embed = nextcord.Embed(
            description=lists,
            color=0x1494DE
        )
        await interaction.reply(embed=embed)

    @_dev.command(name="version")
    async def version(self, interaction, *, version):
        """
        This function is used to update the version of the bot
        
        :param interaction: The interaction object that the command was run on
        :param version: The version of the command
        :return: A string.
        """
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT developer FROM cursy")
        devs = c.fetchone()[0]
        devlist = re.findall(r"[0-9]+", devs)
        if str(interaction.author.id) not in devlist:
            embed = nextcord.Embed(
                description="Du bist kein developer!",
                color=0xE63222
            )
            await interaction.reply(embed=embed)
            return
        c.execute("SELECT version FROM cursy")
        vers = c.fetchone()[0]
        c.execute("UPDATE cursy SET version = ?", [version])
        embed = nextcord.Embed(
            description=f"Cursy wurde auf die {version} Version geupdated.\nAlte Version: {vers}",
            color=0x1494DE
        )
        await interaction.reply(embed=embed)
        embed = await developerLogging(interaction=interaction, text=f"{interaction.author} hat die Bot Version von {vers} auf {version} gesetzt.")
        await self.developerLoggingChannel.send(embed=embed)
        db.commit()
        
        
          
def setup(bot):
    bot.add_cog(deveveloper(bot))
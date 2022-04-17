import sqlite3
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.utils import safeDict

class welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="welcome", aliases=["wel"], invoke_without_command=True)
    async def _welcome(self, ctx):
        # TODO: Add pictures commands to overview command
        embed = nextcord.Embed(
            description="**<:icon_member_joined:965033605707481128> Willkommensnachrichten**\n\n`-welcome channel set <#channel>`\n`-welcome channel remove <#channel>`\n`-welcome message <message>`\n\n> Variablen für die Willkommensnachricht `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{guild_name}`, `{guild_membercount}`\n> Du kannst eine Willkommensnachricht mit mehreren Zeilen erstellen mit `\\n`",
            color=nextcord.Color.blurple()
        )

        await ctx.reply(embed=embed)

    @_welcome.group(name="channel", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _channel(self, ctx):
        embed = nextcord.Embed(
            description="**Es fehlt ein benötigtes Argument.**",
            color=nextcord.Color.dark_red()
        )

        await ctx.reply(embed=embed)

    @_channel.command(name="set", aliases=["add", "update"])
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT channel_id FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        channel_id = c.fetchone()

        if channel_id is not None:
            c.execute("UPDATE welcome SET channel_id = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
            db.commit()

            embed = nextcord.Embed(
                description=f"**<:icon_member_joined:965033605707481128> Willkommenskanal aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Willkommen auf guild_name, user_mention!",
                color=nextcord.Color.dark_green()
            )

            return await ctx.reply(embed=embed)

        c.execute("INSERT INTO welcome(guild_id, channel_id, message, picture) VALUES(?,?,?, NULL)", [ctx.guild.id, channel.id, "Willkommen auf guild_name, user_mention!"])
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:icon_member_joined:965033605707481128> Willkommenskanal gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Willkommen auf guild_name, user_mention!",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_channel.command(name="remove", aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    async def _remove(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT channel_id FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        channel = c.fetchone()

        if channel is None:
            embed = nextcord.Embed(
                description="**Es ist kein Willkommenskanal gesetzt**",
                color=nextcord.Color.dark_red()
            )

            return ctx.reply(embed=embed)

        c.execute("UPDATE welcome SET channel_id = NULL WHERE guild_id = ?", [ctx.guild.id])
        db.commit()

        embed = nextcord.Embed(
            description="**<:icon_member_joined:965033605707481128> Willkommenskanal zurückgesetzt**",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)
    
    @_welcome.command(name="message", aliases=["text"])
    @commands.has_permissions(manage_guild=True)
    async def _message(self, ctx, *, message):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        welcome = c.fetchone()

        if welcome is None or welcome[1] is None:
            embed = nextcord.Embed(
                description="**Es ist kein Willkommenskanal gesetzt**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        c.execute("UPDATE welcome SET message = ? WHERE guild_id = ?", [message, ctx.guild.id])
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:icon_member_joined:965033605707481128> Willkommensnachricht gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(welcome[1]).id}/)\n> **Nachricht:** {message}",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)
    
    @Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM welcome WHERE guild_id = ?", [member.guild.id])
        welcome = c.fetchone()

        if welcome is None or welcome[1] is None:
            return
    
        channel = self.bot.get_channel(welcome[1])
        message = welcome[2].replace("\\n", "\n").format_map(safeDict(user_mention=member.mention, user_name=member.name, user_discriminator=member.discriminator, guild_name=member.guild, guild_membercount=member.guild.member_count))

        await channel.send(message)

def setup(bot):
    bot.add_cog(welcome(bot))

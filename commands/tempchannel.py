import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
import sqlite3

class tempchannel(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="tempchannel", invoke_without_command=True, aliases=['temp'])
    async def _tempchannel(self, ctx):
        embed = nextcord.Embed(
            description="** `⏳`Tempchannel Commands**\n\n> `!tempchannel set <channel>`\n> `!tempchannel remove <channel>`\n> `!tempchannel name <name>`\n> `!tempchannel list`",
            color=nextcord.Color.blurple()
        )
        await ctx.reply(embed=embed)

    @_tempchannel.command(name="add", aliases=['create', 'set'])
    @commands.has_permissions(manage_guild=True)
    async def _add(self, ctx, channel: nextcord.VoiceChannel):
        if channel not in ctx.guild.voice_channels:
            raise commands.ChannelNotFound(channel)
        
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM tempchannel WHERE guild_id = '{ctx.guild.id}'")
        tempchannel = c.fetchone()

        if tempchannel is not None:
            c.execute(f"UPDATE tempchannel SET channel_id = '{channel.id}' WHERE guild_id = '{ctx.guild.id}'")
            db.commit()

            embed = nextcord.Embed(
                description=f"** `⏳`Tempchannel aktualisiert**\n\n> **Channel:** `{channel.name}`\n> **Name:** `{tempchannel[2]}`",
                color=nextcord.Color.dark_green()
            )

            return await ctx.reply(embed=embed)

        c.execute("INSERT INTO tempchannel(guild_id, channel_id, name) VALUES(?, ?, ?)", [ctx.guild.id, channel.id, "⏳ {user}"])
        db.commit()
    
        name = "{user}"

        embed = nextcord.Embed(
            description=f"** `⏳`Tempchannel erstellt**\n\n> **Channel:** `{channel.name}`\n> **Name:** `⏳ {name}`",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_tempchannel.command(name="remove", aliases=['delete', 'del'])
    @commands.has_permissions(manage_guild=True)
    async def _remove(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM tempchannel WHERE guild_id = '{ctx.guild.id}'")
        tempchannel = c.fetchone()

        if tempchannel is None:
            embed = nextcord.Embed(
                description="**Es existiert noch kein Tempchannel auf diesem Server**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        c.execute(f"UPDATE tempchannel SET channel_id=NULL WHERE guild_id = '{ctx.guild.id}'")
        db.commit()

        embed = nextcord.Embed(
            description=f"** `⏳`Tempchannel gelöscht**\n\n> **Channel:** `{tempchannel[1]}`\n> **Name:** `{tempchannel[2]}`",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)




def setup(bot):
    bot.add_cog(tempchannel(bot))
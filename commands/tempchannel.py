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
            description="** `⏳`Tempchannel Commands**\n\n> `!tempchannel set <channel>`\n> `!tempchannel remove`\n> `!tempchannel name <name> `\n\n> Variablen für den Namen: `{user}`, `{anzahl}`",
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
        c.execute(f"SELECT * FROM tempchannels WHERE guild_id = '{ctx.guild.id}'")
        tempchannel = c.fetchone()

        if tempchannel is not None:
            c.execute(f"UPDATE tempchannels SET channel_id = '{channel.id}' WHERE guild_id = '{ctx.guild.id}'")
            db.commit()

            embed = nextcord.Embed(
                description=f"** `⏳`Tempchannel aktualisiert**\n\n> **Channel:** `{channel.name}`\n> **Name:** `{tempchannel[2]}`",
                color=nextcord.Color.dark_green()
            )

            return await ctx.reply(embed=embed)

        c.execute("INSERT INTO tempchannels(guild_id, channel_id, name) VALUES(?, ?, ?)", [ctx.guild.id, channel.id, "⏳ {user}"])
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
        c.execute(f"SELECT * FROM tempchannels WHERE guild_id = '{ctx.guild.id}'")
        tempchannel = c.fetchone()

        if tempchannel is None or tempchannel[1] is None:
            embed = nextcord.Embed(
                description="**Es existiert noch kein Tempchannel auf diesem Server**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        c.execute(f"UPDATE tempchannels SET channel_id=NULL WHERE guild_id = '{ctx.guild.id}'")
        db.commit()

        embed = nextcord.Embed(
            description=f"** `⏳`Tempchannel gelöscht**\n\n> **Channel:** `{tempchannel[1]}`\n> **Name:** `{tempchannel[2]}`",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_tempchannel.command(name="name", aliases=['setname'])
    @commands.has_permissions(manage_guild=True)
    async def _name(self, ctx, *, name):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM tempchannels WHERE guild_id = '{ctx.guild.id}'")
        tempchannel = c.fetchone()

        if tempchannel is None or tempchannel[1] is None:
            embed = nextcord.Embed(
                description="**Es existiert noch kein Tempchannel auf diesem Server**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        c.execute(f"UPDATE tempchannels SET name = '{name}' WHERE guild_id = '{ctx.guild.id}'")
        db.commit()

        embed = nextcord.Embed(
            description=f"** `⏳`Tempchannel aktualisiert**\n\n> **Channel:** `{tempchannel[1]}`\n> **Name:** `{name}`",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT channel_id FROM open_tempchannels")
        open_tempchannels = c.fetchall()

        for tempchannel in open_tempchannels:
            channel = self.bot.get_channel(tempchannel[0])

            if not channel:
                c.execute(f"DELETE FROM open_tempchannels WHERE channel_id = '{tempchannel[0]}'")
                continue

            if len(channel.members) == 0:
                await channel.delete()

                c.execute(f"DELETE FROM open_tempchannels WHERE channel_id = '{tempchannel[0]}'")
        
        db.commit()

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # sourcery skip: merge-nested-ifs, remove-redundant-fstring
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM open_tempchannels WHERE guild_id = '{member.guild.id}'")
        tempchannels = c.fetchall()

        c.execute(f"SELECT * FROM tempchannels WHERE guild_id = '{member.guild.id}'")
        tempchannel = c.fetchone()

        if tempchannels:
            if before.channel:
                if before.channel.id in [tempchannel[1] for tempchannel in tempchannels]:
                    if len(before.channel.members) == 0:
                        c.execute(f"DELETE FROM open_tempchannels WHERE guild_id = '{member.guild.id}' AND channel_id = '{before.channel.id}'")
                        db.commit()

                        await before.channel.delete(reason="Tempchannel leer")

        if tempchannel is not None:
            if after.channel:
                if after.channel.id == tempchannel[1]:
                    memberPermissions = nextcord.PermissionOverwrite(manage_permissions=True, move_members=True, manage_channels=True)

                    name = tempchannel[2].format(user=member.name, anzahl=len(tempchannels) + 1)

                    tempchannel = await after.channel.clone(name=name, reason="Tempchannel erstellen")

                    await tempchannel.set_permissions(member, overwrite=memberPermissions)
                    await tempchannel.set_permissions(member.guild.default_role, overwrite=nextcord.PermissionOverwrite(speak=True))

                    await member.move_to(tempchannel)

                    c.execute(f"INSERT INTO open_tempchannels(guild_id, channel_id, host_id, name) VALUES(?, ?, ?, ?)", [member.guild.id, tempchannel.id, member.id, tempchannel.name])
                    db.commit()


def setup(bot):
    bot.add_cog(tempchannel(bot))
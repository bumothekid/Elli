import nextcord
import sqlite3
import chat_exporter
import io
from nextcord.ext import commands
from nextcord.ext.commands import Cog

class ticket(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="ticket", aliases=["ticketsystem"], invoke_without_command=True)
    async def _ticket(self, ctx):
        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Ticket System**\n\n> `!ticket create <#channel> <@rolle> <text>`\n> `!ticket update <#channel> <messageid> <@rolle> <text>`\n> `!ticket delete <#channel> <messageid>`\n> `!ticket list`\n> `!ticket log set <#channel>`\n> `!ticket log remove`\n\n> Du kannst ein Ticket mit mehreren Zeilen erstellen mit `\\n`",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed)

    # @_ticket.command(name="transcript", aliases=["script"])
    # @commands.has_permissions(manage_guild=True)
    # async def _transcript(self, ctx, channel: nextcord.TextChannel):
    #     print("transcript")
    #     transcript = await chat_exporter.export(channel)
    #     print("transcript")
    #     transcript_file = nextcord.File(io.BytesIO(transcript.encode()), filename="transcript.html")
    #     print("transcript")

    #     await ctx.reply(file=transcript_file)

    @_ticket.command(name="create", aliases=["new"])
    @commands.has_permissions(manage_guild=True)
    async def _create(self, ctx, channel: nextcord.TextChannel, role: nextcord.Role, *, text):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Ticketsystem**\n\n" + text.replace("\\n", "\n"),
            color=nextcord.Color.blurple()
        )

        ticket = await channel.send(embed=embed)
        emote = self.bot.get_emoji(959885507557470239)
        await ticket.add_reaction(emote)

        c.execute("INSERT INTO tickets(guild_id, channel_id, message_id, role_id, text) VALUES(?, ?, ?, ?, ?)", (ctx.guild.id, channel.id, ticket.id, role.id, text))
        db.commit()

        embed = nextcord.Embed(
            description=f"** <:Ticket:959885507557470239> Ticket erstellt**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{ticket.id}/)\n> **Support Rolle:** {role.mention}",
            color=nextcord.Color.dark_green()
        )

        await ctx.send(embed=embed)

    @_ticket.command(name="update", aliases=["edit"])
    @commands.has_permissions(manage_guild=True)
    async def _update(self, ctx, channel: nextcord.TextChannel, message_id, role: nextcord.Role, *, text):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM tickets WHERE guild_id = ? AND channel_id = ? AND message_id = ?", (ctx.guild.id, channel.id, message_id))
        ticket = c.fetchone()

        if ticket is None:
            embed = nextcord.Embed(
                description="**Dieses Ticket existiert nicht**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Ticketsystem**\n\n" + text.replace("\\n", "\n"),
            color=nextcord.Color.blurple()
        )

        ticket = await channel.fetch_message(message_id)
        await ticket.edit(embed=embed)

        c.execute("UPDATE tickets SET text = ? AND role_id = ? WHERE guild_id = ? AND channel_id = ? AND message_id = ?", (text, role.id, ctx.guild.id, channel.id, message_id))
        db.commit()

        embed = nextcord.Embed(
            description=f"** <:Ticket:959885507557470239> Ticket aktualisiert**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{ticket.id}/)\n> **Support Rolle:** {role.mention}",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)
    
    @_ticket.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    async def _delete(self, ctx, channel: nextcord.TextChannel, message_id):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM tickets WHERE guild_id = ? AND channel_id = ? AND message_id = ?", (ctx.guild.id, channel.id, message_id))
        dbticket = c.fetchone()

        if dbticket is None:
            embed = nextcord.Embed(
                description="**Dieses Ticket existiert nicht**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        ticket = await channel.fetch_message(message_id)
        await ticket.delete()

        c.execute("DELETE FROM tickets WHERE guild_id = ? AND channel_id = ? AND message_id = ?", (ctx.guild.id, channel.id, message_id))
        db.commit()

        role = ctx.guild.get_role(dbticket[3])

        embed = nextcord.Embed(
            description=f"**<:Ticket:959885507557470239> Ticket gelöscht**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Support Rolle:** {role.mention}\n> **Text:** {dbticket[4]}",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_ticket.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def _list(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM tickets WHERE guild_id = ?", [ctx.guild.id])
        tickets = c.fetchall()

        if len(tickets) == 0:
            embed = nextcord.Embed(
                description="**Es wurden keine Tickets gefunden**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Tickets**\n\n",
            color=nextcord.Color.blurple()
        )

        i = 1
        for ticket in tickets:
            channel = ctx.guild.get_channel(ticket[1])
            message = await channel.fetch_message(ticket[2])
            role = ctx.guild.get_role(ticket[3])
            
            embed.add_field(name=f"Ticket {i}", value=f"> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}/)\n> **Support Rolle:** {role.mention}", inline=True)
            i += 1

        await ctx.reply(embed=embed)

    @_ticket.group(name="log", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _log(self, ctx):
        embed = nextcord.Embed(description="**Es fehlt ein benötigtes Argument.**", color=nextcord.Color.dark_red())
        await ctx.reply(embed=embed)

    @_log.command(name="set", aliases=["add"])
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT channel_id FROM ticket_logs WHERE guild_id = ?", [ctx.guild.id])
        log = c.fetchone()

        if log is not None:
            c.execute(f"UPDATE ticket_logs SET channel_id = {channel.id} WHERE guild_id = {ctx.guild.id}")
            db.commit()

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Log Channel aktualisiert**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)",
                color=nextcord.Color.dark_green()
            )

            return await ctx.reply(embed=embed)

        c.execute("INSERT INTO ticket_logs (guild_id, channel_id) VALUES (?, ?)", [ctx.guild.id, channel.id])
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:Ticket:959885507557470239> Log Channel gesetzt**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)
    


def setup(bot):
    bot.add_cog(ticket(bot))
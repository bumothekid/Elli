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
            description="**<:Ticket:959885507557470239> Ticket System**\n\n> `!ticket create <#channel> <@rolle> <text>`\n> `!ticket update <#channel> <messageid> <@rolle> <text>`\n> `!ticket delete <#channel> <messageid>`\n> `!ticket log set <#channel>`\n> `!ticket log remove`\n\n> Du kannst ein Ticket mit mehreren Zeilen erstellen mit `\\n`",
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
    


def setup(bot):
    bot.add_cog(ticket(bot))
import nextcord
import sqlite3
import chat_exporter
import io
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.utils import safeDict

class ticket(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="ticket", aliases=["ticketsystem"], invoke_without_command=True)
    async def _ticket(self, ctx):
        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Ticket System**\n\n> `-ticket create <#channel> <@rolle> <text>`\n> `-ticket update <#channel> <messageid> <@rolle> <text>`\n> `-ticket delete <#channel> <messageid>`\n> `-ticket message <text>`\n> `-ticket list`\n> `-ticket log set <#channel>`\n> `-ticket log remove`\n\n> Variablen für custom Message: `{user_name}` `{user_discriminator}` `{user_mention}` `{ticket_link}` `{guild_name}` `{moderation_role}`\n> Du kannst ein Ticket mit mehreren Zeilen erstellen mit `\\n`",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed)

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

        c.execute(f"SELECT * FROM ticket_messages WHERE guild_id = {ctx.guild.id}")
        messages = c.fetchone()

        if messages is None:
            c.execute("INSERT INTO ticket_messages(guild_id, text) VALUES(?, ?)", [ctx.guild.id, "Hey {user_name}, es wird dir bald geholfen.\n\n**Ticket von {user_name}#{user_discriminator}**"])

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

    @_ticket.command(name="message", aliases=["setmessage"])
    @commands.has_permissions(manage_guild=True)
    async def _message(self, ctx, *, text):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM ticket_messages WHERE guild_id = ?", (ctx.guild.id,))
        message = c.fetchone()

        if message is None:
            c.execute("INSERT INTO ticket_messages(guild_id, text) VALUES(?, ?)", [ctx.guild.id, text])
        else:
            c.execute("UPDATE ticket_messages SET text = ? WHERE guild_id = ?", (text, ctx.guild.id))

        db.commit()
        
        text = text.replace("\\n", "\n")

        embed = nextcord.Embed(
            description=f"** <:Ticket:959885507557470239> Nachricht aktualisiert**\n\n> **Nachricht:**\n{text}",
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

        for i, ticket in enumerate(tickets, 1):
            channel = ctx.guild.get_channel(ticket[1])
            message = await channel.fetch_message(ticket[2])
            role = ctx.guild.get_role(ticket[3])
            
            embed.add_field(name=f"Ticket {i}", value=f"> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}/)\n> **Support Rolle:** {role.mention}", inline=True)

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
    
    @_log.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    async def _delete(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT channel_id FROM ticket_logs WHERE guild_id = ?", [ctx.guild.id])
        log = c.fetchone()

        if log is None:
            embed = nextcord.Embed(
                description="**Es ist kein Ticket Logging gesetzt**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        c.execute("DELETE FROM ticket_logs WHERE guild_id = ?", [ctx.guild.id])
        db.commit()

        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Log Channel gelöscht**",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        emote = self.bot.get_emoji(959885507557470239)
        if payload.emoji not in [emote] and payload.emoji.name not in ["🔒", "🔓", "❌"]:
            return

        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute(f"SELECT * FROM tickets WHERE guild_id = {payload.guild_id} AND message_id = {payload.message_id}")
        db_ticket = c.fetchone()

        c.execute(f"SELECT * FROM open_tickets WHERE guild_id = {payload.guild_id} AND channel_id = {payload.channel_id} AND message_id = {payload.message_id}")
        open_ticket = c.fetchone()

        c.execute(f"SELECT * FROM ticket_messages WHERE guild_id = {payload.guild_id}")
        ticket_message = c.fetchone()

        if db_ticket is None and open_ticket is None:
            return

        c.execute(f"SELECT channel_id FROM ticket_logs WHERE guild_id = {payload.guild_id}")
        log = c.fetchone()

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        category = channel.category
        message = await channel.fetch_message(payload.message_id)

        if payload.emoji == emote:
            if open_ticket is not None:
                await message.remove_reaction(emote, payload.member)

                embed = nextcord.Embed(
                    description=f"**Du hast bereits ein Ticket auf {guild.name} geöffnet**",
                    color=nextcord.Color.dark_red()
                )

                try:
                    dm = await payload.member.create_dm()
                    return await dm.send(embed=embed)
                except Exception:
                    return

            role = guild.get_role(db_ticket[3])
            await message.remove_reaction(emote, payload.member)

            ticket = await guild.create_text_channel(name=f"ticket-{payload.member.name}", category=category, reason=f"Ticket von {payload.member.name} erstellt")

            oldPerms = nextcord.PermissionOverwrite(read_messages=None, send_messages=None, add_reactions=None)
            memberPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True)
            supportPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, manage_permissions=True)
            everyonePerms = nextcord.PermissionOverwrite(read_messages=False, send_messages=False, add_reactions=False)

            for perm in ticket.overwrites:
                await ticket.set_permissions(perm, overwrite=oldPerms)
            await ticket.set_permissions(payload.member, overwrite=memberPerms)
            await ticket.set_permissions(role, overwrite=supportPerms)
            await ticket.set_permissions(guild.default_role, overwrite=everyonePerms)

            embed = nextcord.Embed(
                description=((ticket_message[1]).replace('\\n', '\n')).format_map(safeDict(user_mention=payload.member.mention, user_name=payload.member.name, user_discriminator=payload.member.discriminator, ticket_link=f"[`📎`Link](https://discord.com/channels/{db_ticket[0]}/{db_ticket[1]}/{db_ticket[2]}/)", guild_name=guild.name, moderation_role=role.mention)),
                color=nextcord.Color.blurple()
            )

            message = await ticket.send(f"{payload.member.mention} | {role.mention}", embed=embed)
            await message.add_reaction("🔒")

            c.execute("INSERT INTO open_tickets(guild_id, channel_id, message_id, role_id, user_id) VALUES (?, ?, ?, ?, ?)", [payload.guild_id, ticket.id, message.id, role.id, payload.member.id])
            db.commit()

            if log is None:
                return

            logging = guild.get_channel(log[0])

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket erstellt**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{ticket.id}/{message.id})\n> **User:** {payload.member.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.dark_green()
            )

            await logging.send(embed=embed)

        elif payload.emoji.name == "🔒":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("🔒", payload.member)

            memberPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=False, add_reactions=True, embed_links=None, attach_files=None, read_message_history=True)

            await channel.set_permissions(user, overwrite=memberPerms)

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket geschlossen**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.dark_green()
            )

            message = await channel.send(embed=embed)
            await message.add_reaction("🔓")
            await message.add_reaction("❌")

            c.execute(f"UPDATE open_tickets SET message_id = {message.id} WHERE guild_id = {payload.guild_id} AND user_id = {payload.member.id}")
            db.commit()

            if log is None:
                return

            logging = guild.get_channel(log[0])

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket geschlossen**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.blurple()
            )

            await logging.send(embed=embed)

        elif payload.emoji.name == "🔓":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("🔓", payload.member)

            memberPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True)

            await channel.set_permissions(user, overwrite=memberPerms)

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket erneut geöffnet**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.dark_green()
            )

            message = await channel.send(embed=embed)

            first_message = (await channel.history(limit=1, oldest_first=True).flatten())[0]

            c.execute(f"UPDATE open_tickets SET message_id = {first_message.id} WHERE guild_id = {payload.guild_id} AND user_id = {payload.member.id}")
            db.commit()

            if log is None:
                return

            logging = guild.get_channel(log[0])

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket erneut geöffnet**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.dark_green()
            )

            await logging.send(embed=embed)
        elif payload.emoji.name == "❌":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("❌", payload.member)

            if role not in payload.member.roles:
                embed = nextcord.Embed(
                    description=f"{payload.member.mention}, du hast keine Berechtigungen um dieses Ticket zu schließen\n\n> Du benötigst die Rolle {role.mention}",
                    color=nextcord.Color.dark_red()
                )

                return await channel.send(embed=embed)

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket wird gelöscht**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.dark_red()
            )

            await channel.send(embed=embed)

            c.execute(f"DELETE FROM open_tickets WHERE guild_id = {payload.guild_id} AND user_id = {payload.member.id}")
            db.commit()

            if log is None:
                return

            logging = guild.get_channel(log[0])

            transcript = await chat_exporter.export(channel)
            transcript_file = nextcord.File(io.BytesIO(transcript.encode()), filename="transcript.html")

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket wird gelöscht**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.dark_red()
            )

            await logging.send(embed=embed, file=transcript_file)

            await channel.delete()

            



        

def setup(bot):
    bot.add_cog(ticket(bot))
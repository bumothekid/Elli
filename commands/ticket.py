import nextcord
import chat_exporter
import io
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.other import safeDict
from .utils.embeds import infoEmbed, successEmbed, errorEmbed
from .utils.database import readOne, readAll, insert, update, delete

class ticket(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="ticket", aliases=["ticketsystem"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _ticket(self, ctx):
        await infoEmbed(self, ctx, "**<:Ticket:959885507557470239> Ticket System**\n\n> `-ticket create <#channel> <@rolle> <text>`\n> `-ticket update <#channel> <messageid> <@rolle> <text>`\n> `-ticket delete <#channel> <messageid>`\n> `-ticket message <text>`\n> `-ticket list`\n> `-ticket log set <#channel>`\n> `-ticket log remove`\n\n> Variablen für custom Message: `{user_name}` `{user_discriminator}` `{user_mention}` `{ticket_link}` `{guild_name}` `{moderation_role}`\n> Du kannst ein Ticket mit mehreren Zeilen erstellen mit `\\n`")

    @_ticket.command(name="create", aliases=["new"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _create(self, ctx, channel: nextcord.TextChannel, role: nextcord.Role, *, text):
        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Ticketsystem**\n\n" + text.replace("\\n", "\n"),
            color=nextcord.Color.blurple()
        )

        ticket = await channel.send(embed=embed)
        emote = self.bot.get_emoji(959885507557470239)
        await ticket.add_reaction(emote)

        insert(table="tickets", columns="guild_id, channel_id, message_id, role_id, text", values=[ctx.guild.id, channel.id, ticket.id, role.id, text])
        messages = readOne(columns="*", table="ticket_messages", where="guild_id", values=[ctx.guild.id])

        if messages is None:
            insert(table="ticket_messages", columns="guild_id, text", values=[ctx.guild.id, "Hey {user_name}, es wird dir bald geholfen.\n\n**Ticket von {user_name}#{user_discriminator}**"])

        await successEmbed(self, ctx, f"** <:Ticket:959885507557470239> Ticket erstellt**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{ticket.id}/)\n> **Support Rolle:** {role.mention}")

    @_ticket.command(name="update", aliases=["edit"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _update(self, ctx, channel: nextcord.TextChannel, message_id, role: nextcord.Role, *, text):
        ticket = readOne(columns="*", table="tickets", where="guild_id channel_id message_id", values=[ctx.guild.id, channel.id, message_id])

        if ticket is None:
            return await errorEmbed(self, ctx, "Dieses Ticket existiert nicht.")

        embed = nextcord.Embed(
            description="**<:Ticket:959885507557470239> Ticketsystem**\n\n" + text.replace("\\n", "\n"),
            color=nextcord.Color.blurple()
        )

        ticket = await channel.fetch_message(message_id)
        await ticket.edit(embed=embed)

        update(table="tickets", columns="text role_id", where="guild_id channel_id message_id", values=[text, role.id, ctx.guild.id, channel.id, message_id])
        await infoEmbed(self, ctx,"** <:Ticket:959885507557470239> Ticket aktualisiert**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{ticket.id}/)\n> **Support Rolle:** {role.mention}")
    
    @_ticket.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _delete(self, ctx, channel: nextcord.TextChannel, *, message_id):
        dbticket = readOne(columns="*", table="tickets", where="guild_id channel_id message_id", values=[ctx.guild.id, channel.id, message_id])

        if dbticket is None:
            return await errorEmbed(self, ctx, "Dieses Ticket existiert nicht.")

        ticket = await channel.fetch_message(message_id)
        await ticket.delete()

        delete(table="tickets", where="guild_id channel_id message_id", values=[ctx.guild.id, channel.id, message_id])

        role = ctx.guild.get_role(dbticket[3])

        await successEmbed(self, ctx, f"**<:Ticket:959885507557470239> Ticket gelöscht**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Support Rolle:** {role.mention}\n> **Text:** {dbticket[4]}")

    @_ticket.command(name="message", aliases=["setmessage"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _message(self, ctx, *, text):
        message = readOne(columns="*", table="ticket_messages", where="guild_id", values=[ctx.guild.id])

        if message is None:
            insert(table="ticket_messages", columns="guild_id, text", values=[ctx.guild.id, text])
        else:
            update(table="ticket_messages", columns="text", where="guild_id", values=[text, ctx.guild.id])
        
        text = text.replace("\\n", "\n")

        await successEmbed(self, ctx, f"** <:Ticket:959885507557470239> Nachricht aktualisiert**\n\n> **Nachricht:**\n{text}")

    @_ticket.command(name="list")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _list(self, ctx):
        tickets = readAll(columns="*", table="tickets", where="guild_id", values=[ctx.guild.id])

        if not tickets:
            return await errorEmbed(self, ctx, "Es wurden keine Tickets gefunden.")

        fields = []

        for i, ticket in enumerate(tickets, 1):
            channel = ctx.guild.get_channel(ticket[1])
            message = await channel.fetch_message(ticket[2])
            role = ctx.guild.get_role(ticket[3])

            fields.append({"name": f"Ticket {i}", "value": f"> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}/)\n> **Support Rolle:** {role.mention}", "inline": True})
        
        await infoEmbed(self, ctx, "**<:Ticket:959885507557470239> Tickets**\n\n", fields=fields)

    @_ticket.group(name="log", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _log(self, ctx):
        await errorEmbed(self, ctx, "Es fehlt ein benötigtes Argument.")

    @_log.command(name="set", aliases=["add"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        log = readOne(columns="channel_id", table="ticket_logs", where="guild_id", values=[ctx.guild.id])

        if log is not None:
            update(table="ticket_logs", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])

            return await successEmbed(self, ctx, f"**<:Ticket:959885507557470239> Log Channel aktualisiert**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)")

        insert(table="ticket_logs", columns="guild_id, channel_id", values=[ctx.guild.id, channel.id])
        await successEmbed(self, ctx, f"**<:Ticket:959885507557470239> Log Channel gesetzt**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)")
    
    @_log.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _delete(self, ctx):
        log = readOne(columns="channel_id", table="ticket_logs", where="guild_id", values=[ctx.guild.id])

        if log is None:
            return await errorEmbed(self, ctx, "Es ist noch kein Ticket Logging gesetzt.")

        delete(table="ticket_logs", where="guild_id", values=[ctx.guild.id])
        await successEmbed(self, ctx, "**<:Ticket:959885507557470239> Log Channel gelöscht**")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member is None:
            return
            
        if payload.member.bot:
            return

        emote = self.bot.get_emoji(959885507557470239)
        if payload.emoji not in [emote] and payload.emoji.name not in ["🔒", "🔓", "❌"]:
            return

        db_ticket = readOne(columns="*", table="tickets", where="guild_id message_id", values=[payload.guild_id, payload.message_id])
        open_ticket = readOne(columns="*", table="open_tickets", where="guild_id user_id", values=[payload.guild_id, payload.member.id])
        ticket_message = readOne(columns="*", table="ticket_messages", where="guild_id", values=[payload.guild_id])

        if db_ticket is None and open_ticket is None:
            return

        log = readOne(columns="channel_id", table="ticket_logs", where="guild_id", values=[payload.guild_id])

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        category = channel.category
        message = await channel.fetch_message(payload.message_id)

        if payload.emoji == emote:
            if open_ticket is not None:
                await message.remove_reaction(emote, payload.member)

                return await errorEmbed(self, payload.member, f"Du hast bereits ein Ticket auf {guild.name} geöffnet.")

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

            insert(table="open_tickets", columns="guild_id, channel_id, message_id, role_id, user_id", values=[payload.guild_id, ticket.id, message.id, role.id, payload.member.id])

            if log is None:
                return

            await infoEmbed(self, guild.get_channel(log[0]), f"**<:Ticket:959885507557470239> Ticket erstellt**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{ticket.id}/{message.id})\n> **User:** {payload.member.mention}\n> **Support:** {role.mention}", color=nextcord.Color.green())

        elif payload.emoji.name == "🔒":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("🔒", payload.member)

            memberPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=False, add_reactions=True, embed_links=None, attach_files=None, read_message_history=True)

            await channel.set_permissions(user, overwrite=memberPerms)

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket geschlossen**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.green()
            )

            message = await channel.send(embed=embed)
            await message.add_reaction("🔓")
            await message.add_reaction("❌")

            update(table="open_tickets", columns="message_id", where="guild_id user_id", values=[message.id, payload.guild_id, payload.member.id])

            if log is None:
                return

            await infoEmbed(self, guild.get_channel(log[0]), f"**<:Ticket:959885507557470239> Ticket geschlossen**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}")

        elif payload.emoji.name == "🔓":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("🔓", payload.member)

            memberPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True)

            await channel.set_permissions(user, overwrite=memberPerms)

            embed = nextcord.Embed(
                description=f"**<:Ticket:959885507557470239> Ticket erneut geöffnet**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}",
                color=nextcord.Color.green()
            )

            message = await channel.send(embed=embed)

            first_message = (await channel.history(limit=1, oldest_first=True).flatten())[0]
            update(table="open_tickets", columns="message_id", where="guild_id user_id", values=[first_message.id, payload.guild_id, payload.member.id])

            if log is None:
                return

            await infoEmbed(self, guild.get_channel(log[0]), f"**<:Ticket:959885507557470239> Ticket erneut geöffnet**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}", color=nextcord.Color.green())

        elif payload.emoji.name == "❌":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("❌", payload.member)

            if role not in payload.member.roles:
                return await errorEmbed(self, channel, f"{payload.member.mention}, du hast keine Berechtigungen um dieses Ticket zu schließen**\n\n**> Du benötigst die Rolle {role.mention}")

            await infoEmbed(self, channel, f"**<:Ticket:959885507557470239> Ticket wird gelöscht**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}", color=nextcord.Color.red())

            delete(table="open_tickets", where="guild_id user_id", values=[payload.guild_id, payload.member.id])

            if log is None:
                return await channel.delete()

            transcript = await chat_exporter.export(channel)
            transcript_file = nextcord.File(io.BytesIO(transcript.encode()), filename="transcript.html")

            await infoEmbed(self, guild.get_channel(log[0]), f"**<:Ticket:959885507557470239> Ticket wird gelöscht**\n\n> **Ticket:** [`📎`Link](https://discord.com/channels/{payload.guild_id}/{open_ticket[1]}/{open_ticket[2]})\n> **User:** {user.mention}\n> **Support:** {role.mention}", file=transcript_file)
            await channel.delete()

            



        

def setup(bot):
    bot.add_cog(ticket(bot))
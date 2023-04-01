import nextcord
import chat_exporter
import io
from nextcord.ext import commands
from nextcord.ext.commands import Cog, Context
from .utils.other import safeDict
from .utils.embeds import infoEmbed, successEmbed, errorEmbed
from .utils.database import readOne, readAll, insert, update, delete
from .utils.language import getLanguageStrings, getGuildLanguage, getLocale

languageStrings = {}
class Ticket(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="ticket", aliases=["ticketsystem"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _ticket(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])[0]

        await infoEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketsystemDescription", prefix))

    @_ticket.command(name="create", aliases=["new"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _create(self, ctx, channel: nextcord.TextChannel, role: nextcord.Role, *, text):
        guildLocale = getGuildLanguage(ctx.guild.id)
        embed = nextcord.Embed(
            description="**<:Ticket:1087437978873376798> Ticketsystem**\n\n" + text.replace("\\n", "\n"),
            color=nextcord.Color.blurple()
        )

        ticket = await channel.send(embed=embed)
        emote = self.bot.get_emoji(1087437978873376798)
        await ticket.add_reaction(emote)

        insert(table="tickets", columns="guild_id, channel_id, message_id, role_id, text", values=[ctx.guild.id, channel.id, ticket.id, role.id, text])
        messages = readOne(columns="*", table="ticket_messages", where="guild_id", values=[ctx.guild.id])

        if messages is None:
            message = getLocale(languageStrings, guildLocale, "ticketMessage", "{user_name}", "{user_name}", "{user_discriminator}")
            insert(table="ticket_messages", columns="guild_id, text", values=[ctx.guild.id, message])

        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketCreated", ctx.guild.id, channel.id, ticket.id, role.mention))

    @_ticket.command(name="update", aliases=["edit"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _update(self, ctx, channel: nextcord.TextChannel, message_id, role: nextcord.Role, *, text):
        guildLocale = getGuildLanguage(ctx.guild.id)
        ticket = readOne(columns="*", table="tickets", where="guild_id channel_id message_id", values=[ctx.guild.id, channel.id, message_id])
        
        if ticket is None:
            return await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketNotFound"))
        
        embed = nextcord.Embed(
            description="**<:Ticket:1087437978873376798> Ticketsystem**\n\n" + text.replace("\\n", "\n"),
            color=nextcord.Color.blurple()
        )
        
        ticket = await channel.fetch_message(message_id)
        await ticket.edit(embed=embed)
        
        update(table="tickets", columns="text role_id", where="guild_id channel_id message_id", values=[text, role.id, ctx.guild.id, channel.id, message_id])
        
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketUpdated", ctx.guild.id, channel.id, ticket.id, role.mention))

    @_ticket.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def deleteTicket(self, ctx, channel: nextcord.TextChannel, message_id:int):
        guildLocale = getGuildLanguage(ctx.guild.id)
        dbticket = readOne(columns="*", table="tickets", where="guild_id channel_id message_id", values=[ctx.guild.id, channel.id, message_id])
        
        if dbticket is None:
            return await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketNotFound"))
        
        ticket = await channel.fetch_message(message_id)
        await ticket.delete()
        
        delete(table="tickets", where="guild_id channel_id message_id", values=[ctx.guild.id, channel.id, message_id])
        
        role = ctx.guild.get_role(dbticket[3])
        
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketDeleted", ctx.guild.id, channel.id, role.mention, dbticket[4]))

    @_ticket.command(name="message", aliases=["setmessage"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _message(self, ctx, *, text):
        guildLocale = getGuildLanguage(ctx.guild.id)
        message = readOne(columns="*", table="ticket_messages", where="guild_id", values=[ctx.guild.id])

        if message is None:
            insert(table="ticket_messages", columns="guild_id, text", values=[ctx.guild.id, text])
        else:
            update(table="ticket_messages", columns="text", where="guild_id", values=[text, ctx.guild.id])

        text = text.replace("\\n", "\n")
        
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketMessageUpdated", text))

    @_ticket.command(name="list")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _list(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        tickets = readAll(columns="*", table="tickets", where="guild_id", values=[ctx.guild.id])

        if not tickets:
            return await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketNotFound"))

        fields = []

        for i, ticket in enumerate(tickets, 1):
            channel = ctx.guild.get_channel(ticket[1])
            message = await channel.fetch_message(ticket[2])
            role = ctx.guild.get_role(ticket[3])
            
            value = getLocale(languageStrings, guildLocale, "ticketList", ctx.guild.id, channel.id, message.id, role.mention)
            fields.append({"name": f"Ticket {i}", "value": value, "inline": True})

        await infoEmbed(self, ctx, "**<:Ticket:1087437978873376798> Tickets**\n\n", fields=fields)

    @_ticket.group(name="log", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _log(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)

    @_log.command(name="set", aliases=["add"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        guildLocale = getGuildLanguage(ctx.guild.id)
        log = readOne(columns="channel_id", table="ticket_logs", where="guild_id", values=[ctx.guild.id])

        if log is not None:
            update(table="ticket_logs", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])
            
            return await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketLogSet", ctx.guild.id, channel.id))

        insert(table="ticket_logs", columns="guild_id, channel_id", values=[ctx.guild.id, channel.id])
        
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketLogSet", ctx.guild.id, channel.id))

    @_log.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _delete(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        log = readOne(columns="channel_id", table="ticket_logs", where="guild_id", values=[ctx.guild.id])

        if log is None:
            return await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketLogNotFound"))

        delete(table="ticket_logs", where="guild_id", values=[ctx.guild.id])
        
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "ticketLogRemoved", ctx.guild.id))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member is None:
            return

        if payload.member.bot:
            return

        emote = self.bot.get_emoji(1087437978873376798)
        if payload.emoji not in [emote] and payload.emoji.name not in ["🔒", "🔓", "❌"]:
            return

        db_ticket = readOne(columns="*", table="tickets", where="guild_id message_id", values=[payload.guild_id, payload.message_id])
        user_open_ticket = readOne(columns="*", table="open_tickets", where="guild_id user_id", values=[payload.guild_id, payload.user_id])
        open_ticket = readOne(columns="*", table="open_tickets", where="guild_id channel_id", values=[payload.guild_id, payload.channel_id])
        ticket_message = readOne(columns="*", table="ticket_messages", where="guild_id", values=[payload.guild_id])
        
        if db_ticket is None and open_ticket is None:
            return

        log = readOne(columns="channel_id", table="ticket_logs", where="guild_id", values=[payload.guild_id])

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        category = channel.category
        message = await channel.fetch_message(payload.message_id)
        guildLocale = getGuildLanguage(guild.id)

        if payload.emoji == emote:
            if user_open_ticket is not None:
                await message.remove_reaction(emote, payload.member)
                
                return await errorEmbed(self, payload.member, getLocale(languageStrings, guildLocale, "ticketAlreadyOpen", guild.name))

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
            
            await infoEmbed(self, guild.get_channel(log[0]), getLocale(languageStrings, guildLocale, "userTicketCreated", payload.guild_id, ticket.id, message.id, payload.member.mention, role.mention), color=nextcord.Color.green())

        elif payload.emoji.name == "🔒":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("🔒", payload.member)

            memberPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=False, add_reactions=True, embed_links=None, attach_files=None, read_message_history=True)

            await channel.set_permissions(user, overwrite=memberPerms)
            
            ticketClosed = getLocale(languageStrings, guildLocale, "userTicketClosed", payload.guild_id, open_ticket[1], open_ticket[2], user.mention, role.mention)

            embed = nextcord.Embed(
                description=ticketClosed,
                color=nextcord.Color.green()
            )

            message = await channel.send(embed=embed)
            await message.add_reaction("🔓")
            await message.add_reaction("❌")

            update(table="open_tickets", columns="message_id", where="guild_id user_id", values=[message.id, payload.guild_id, payload.member.id])

            if log is None:
                return

            await infoEmbed(self, guild.get_channel(log[0]), ticketClosed)

        elif payload.emoji.name == "🔓":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("🔓", payload.member)

            memberPerms = nextcord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True)

            await channel.set_permissions(user, overwrite=memberPerms)
            
            ticketReopened = getLocale(languageStrings, guildLocale, "userTicketReopened", payload.guild_id, open_ticket[1], open_ticket[2], user.mention, role.mention)

            embed = nextcord.Embed(
                description=ticketReopened,
                color=nextcord.Color.green()
            )

            message = await channel.send(embed=embed)

            first_message = (await channel.history(limit=1, oldest_first=True).flatten())[0]
            update(table="open_tickets", columns="message_id", where="guild_id user_id", values=[first_message.id, payload.guild_id, payload.member.id])

            if log is None:
                return

            await infoEmbed(self, guild.get_channel(log[0]), ticketReopened, color=nextcord.Color.green())

        elif payload.emoji.name == "❌":
            user = guild.get_member(open_ticket[4])
            role = guild.get_role(open_ticket[3])

            await message.remove_reaction("❌", payload.member)

            if role not in payload.member.roles:
                return await errorEmbed(self, channel, getLocale(languageStrings, guildLocale, "userTicketCloseNoPermission", payload.member.mention, role.mention))
            
            ticketDeleted = getLocale(languageStrings, guildLocale, "userTicketDeleted", payload.guild_id, open_ticket[1], open_ticket[2], user.mention, role.mention)
            
            await infoEmbed(self, channel, ticketDeleted, color=nextcord.Color.red())

            delete(table="open_tickets", where="guild_id user_id", values=[payload.guild_id, payload.member.id])

            if log is None:
                return await channel.delete()

            transcript = await chat_exporter.export(channel)
            transcript_file = nextcord.File(io.BytesIO(transcript.encode()), filename="transcript.html")

            await infoEmbed(self, guild.get_channel(log[0]), ticketDeleted, file=transcript_file)
            await channel.delete()







def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("ticket")
    bot.add_cog(Ticket(bot))
import nextcord
from nextcord import ui, ButtonStyle
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.database import readOne, insert, update

class leave(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="leave", invoke_without_command=True)
    async def _leave(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:icon_member_left:965034270622122044> Verlassnachrichten**\n\n> `-leave channel set <#channel>`\n> `-leave channel remove <#channel>`\n> `-leave message <message>`\n> `-leave picture set <picture>`\n> `-leave picture remove`\n> `-leave picture show`\n\n> Variablen für die Verlassnachricht `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{guild_name}`, `{guild_membercount}`\n> Du kannst eine Verlassnachricht mit mehreren Zeilen erstellen mit `\\n`\n> Um die Verlassnachricht ganz zu entfernen füge `_ _` als Nachricht ein")

    @_leave.command(name="channel", invoke_without_command=True)
    async def _channel(self, ctx):
        await errorEmbed(self, ctx, "Es fehlt ein benötigtes Argument.")

    @_leave.command(name="set", aliases=["add", "update"])
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is not None:
            message = leave[2] if leave[2] is not None else "Tschüß {user_name}#{user_discriminator} hoffentlich kommst du bald wieder!"
            picture = leave[3] if leave[3] is not None else "Keins"
            update(table="leave", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])

            return await successEmbed(self, ctx, f"**<:icon_member_left:965034270622122044> Verlasskanal aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** {message}\n> **Bild:** `{picture}`")

        insert(table="leave", columns="guild_id, channel_id, message, picture", values=[ctx.guild.id, channel.id, "Tschüß {user_name}#{user_discriminator} hoffentlich kommst du bald wieder!", "null"])

        await successEmbed(self, ctx, f"**<:icon_member_left:965034270622122044> Verlasskanal gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Tschüß {{user_name}}#{{user_discriminator}} hoffentlich kommst du bald wieder!\n> **Bild:** `Keins`")

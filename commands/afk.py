import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time
from .utils.database import readOne, readAll, insert, update, delete
from .utils.embeds import errorEmbed, successEmbed
from .utils.other import getPrefixFromDatabase, checkLink

class Afk(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="afk", aliases=["away"], invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _afk(self, ctx, *, reason="AFK"):
        is_afk = readOne(columns="reason", table="afk", where="guild_id user_id", values=[ctx.guild.id, ctx.author.id])

        if checkLink(reason):
            return await errorEmbed(ctx, "Es dürfen keine Links oder Invites in deinem AFK-Status sein.")

        if len(reason) > 1000:
            return await errorEmbed(ctx, "Dein AFK-Status darf nicht länger als `1000` Zeichen sein.")

        if is_afk is not None:
            update(table="afk", columns="reason", where="guild_id user_id", values=[reason, ctx.guild.id, ctx.author.id])
        else:
            insert(table="afk", columns="guild_id, user_id, time, reason", values=[ctx.guild.id, ctx.author.id, time(), reason])

        await successEmbed(self, ctx, f"**<:Idle:1087452184582561802> Du bist jetzt AFK**\n\n**Grund:** {reason}", color=nextcord.Color.dark_gold())

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(getPrefixFromDatabase(self.bot, message)):
            return

        users = readAll(columns="user_id, time, reason", table="afk", where="guild_id", values=[message.guild.id])

        if not users:
            return

        for user in users:
            if user[0] == message.author.id:
                _time = time() - float(user[1])
                hours, minutes, seconds = _time / 3600, (_time / 60) % 60, _time % 60
                timeUp = f"`{int(hours)} Stunde(n), {int(minutes)} Minuten und {int(seconds)} Sekunden`" if hours >= 1 else f"`{int(minutes)} Minuten und {int(seconds)} Sekunden`"

                delete(table="afk", where="guild_id user_id", values=[message.guild.id, message.author.id])

                return await successEmbed(self, message, f"**<:Online:1087457380591206450> Du bist nicht mehr AFK**\n\n**Länge:** {timeUp}\n**Grund:** {user[2]}")
    
            if user[0] in [member.id for member in message.mentions]:
                member = message.guild.get_member(user[0])

                _time = time() - float(user[1])
                hours, minutes, seconds = _time / 3600, (_time / 60) % 60, _time % 60
                timeUp = f"`{int(hours)} Stunde(n), {int(minutes)} Minuten und {int(seconds)} Sekunden`" if hours >= 1 else f"`{int(minutes)} Minuten und {int(seconds)} Sekunden`"

                return await successEmbed(self, message, f"**<:Idle:1087452184582561802> {member.mention} ist AFK**\n\n**Länge:** {timeUp}\n**Grund:** {user[2]}", color=nextcord.Color.dark_gold())


def setup(bot):
    bot.add_cog(Afk(bot))
import nextcord
import sqlite3
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time

class afk(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="afk", aliases=["away"], invoke_without_command=True)
    async def _afk(self, ctx, *, reason="AFK"):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT reason FROM afk WHERE guild_id = '{ctx.guild.id}' AND user_id = '{ctx.author.id}'")
        is_afk = c.fetchone()
        if "https://" in reason or "http://" in reason:
            embed = nextcord.Embed(
                description="**Es dürfen keine Links in deinem AFK-Status sein**",
                color=nextcord.Color.dark_red()
            )
            return await ctx.reply(embed=embed)
        elif "discord." in reason or "discordapp." in reason:
            embed = nextcord.Embed(
                description="**Es dürfen keine Invites in deinem AFK-Status sein**",
                color=nextcord.Color.dark_red()
            )
            return await ctx.reply(embed=embed)
        elif len(reason) > 1000:
            embed = nextcord.Embed(
                description="**Dein AFK-Status darf nicht länger als 1000 Zeichen sein**",
                color=nextcord.Color.dark_red()
            )
            return await ctx.reply(embed=embed)

        if is_afk is not None:
            c.execute("UPDATE afk SET reason = ? WHERE guild_id = ? AND user_id = ?", [reason, ctx.guild.id, ctx.author.id])
        else:
            c.execute("INSERT INTO afk(guild_id, user_id, time, reason) VALUES(?, ?, ?, ?)", [ctx.guild.id, ctx.author.id, time(), reason])

        db.commit()

        embed = nextcord.Embed(
            description=f"**<:Idle:960157731388555274> Du bist jetzt AFK**\n\n**Grund:** {reason}",
            color=nextcord.Color.dark_gold()
        )

        await ctx.reply(embed=embed)

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith("!"):
            return

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT user_id, time, reason  FROM afk WHERE guild_id = '{message.guild.id}'")
        users = c.fetchall()

        if not users:
            return

        for user in users:
            if user[0] == message.author.id:

                _time = time() - float(user[1])
                hours, minutes, seconds = _time / 3600, (_time / 60) % 60, _time % 60
                timeUp = f"`{int(hours)} Stunden, {int(minutes)} Minuten und {int(seconds)} Sekunden`"

                if hours >= 1:
                    if hours > 1:
                        timeUp = f"`{int(hours)} Stunden, {int(minutes)} Minuten und {int(seconds)} Sekunden`"
                    else:
                        timeUp = f"`{int(hours)} Stunde, {int(minutes)} Minuten und {int(seconds)} Sekunden`"
                else:
                    timeUp = f"`{int(minutes)} Minuten und {int(seconds)} Sekunden`"



                embed = nextcord.Embed(
                    description=f"**<:Online:960157889899663411> Du bist nicht mehr AFK**\n\n**Länge:** {timeUp}\n**Grund:** {user[2]}",
                    color=nextcord.Color.dark_green()
                )

                await message.reply(embed=embed)

                c.execute(f"DELETE FROM afk WHERE guild_id = '{message.guild.id}' AND user_id = '{message.author.id}'")
                return db.commit()
            
            if f"<@{user[0]}>" in message.content or f"<@!{user[0]}>" in message.content:
                user = message.guild.get_member(user[0])

                _time = time() - float(user[1])
                hours, minutes, seconds = _time / 3600, (_time / 60) % 60, _time % 60
                timeUp = f"`{int(hours)} Stunden, {int(minutes)} Minuten und {int(seconds)} Sekunden`"

                embed = nextcord.Embed(
                    description=f"**<:Idle:960157731388555274> {user.mention} ist AFK**\n\n**Länge:** {timeUp}\n**Grund:** {user[2]}",
                    color=nextcord.Color.dark_gold()
                )

                return await message.reply(embed=embed)


def setup(bot):
    bot.add_cog(afk(bot))
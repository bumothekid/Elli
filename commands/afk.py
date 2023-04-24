import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from time import time
from .utils.database import readOne, readAll, insert, update, delete
from .utils.embeds import errorEmbed, successEmbed
from .utils.other import getPrefixFromDatabase, checkLink
from .utils.language import getGuildLanguage, getLocale, getLanguageStrings

languageStrings = {}
class Afk(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="afk", aliases=["away"], invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _afk(self, ctx, *, reason="AFK"):
        guildLocale = getGuildLanguage(ctx.guild.id)
        is_afk = readOne(columns="reason", table="afk", where="guild_id user_id", values=[ctx.guild.id, ctx.author.id])

        if checkLink(reason):
            return await errorEmbed(self, ctx, getLocale(guildLocale, "afk", "linkInReason"))

        if len(reason) > 150:
            return await errorEmbed(self, ctx, getLocale(guildLocale, "afk", "reasonTooLong"))

        if is_afk is not None:
            update(table="afk", columns="reason", where="guild_id user_id", values=[reason, ctx.guild.id, ctx.author.id])
        else:
            insert(table="afk", columns="guild_id, user_id, time, reason", values=[ctx.guild.id, ctx.author.id, time(), reason])

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "afkSet", reason), color=nextcord.Color.dark_gold())

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.content.startswith(getPrefixFromDatabase(self.bot, message)):
            return

        users = readAll(columns="user_id, time, reason", table="afk", where="guild_id", values=[message.guild.id])

        if not users:
            return

        for user in users:
            if user[0] == message.author.id:
                guildLocale = getGuildLanguage(message.guild.id)
                
                _time = time() - float(user[1])
                hours, minutes, seconds = _time / 3600, (_time / 60) % 60, _time % 60
                timeUp = getLocale(self.bot, languageStrings, guildLocale, "timeUpHours", int(hours), int(minutes), int(seconds)) if hours >= 1 else getLocale(self.bot, languageStrings, guildLocale, "timeUp", int(minutes), int(seconds))

                delete(table="afk", where="guild_id user_id", values=[message.guild.id, message.author.id])

                return await successEmbed(self, message, getLocale(self.bot, languageStrings, guildLocale, "afkRemoved", timeUp, user[2]))
    
            if user[0] in [member.id for member in message.mentions]:
                guildLocale = getGuildLanguage(message.guild.id)
                member = message.guild.get_member(user[0])

                _time = time() - float(user[1])
                hours, minutes, seconds = _time / 3600, (_time / 60) % 60, _time % 60
                timeUp = getLocale(self.bot, languageStrings, guildLocale, "timeUpHours", int(hours), int(minutes), int(seconds)) if hours >= 1 else getLocale(self.bot, languageStrings, guildLocale, "timeUp", int(minutes), int(seconds))

                return await successEmbed(self, message, getLocale(self.bot, languageStrings, guildLocale, "isAfk", member.mention, timeUp, user[2]), color=nextcord.Color.dark_gold())


def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("afk")
    bot.add_cog(Afk(bot))
import contextlib
from nextcord.ext import commands
from nextcord.ext.commands import Cog

from .utils.other import getPrefixFromDatabase
from .utils.embeds import infoEmbed, errorEmbed, successEmbed
from .utils.database import delete, insert, readOne, readAll

class automod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="badword", aliases=["bad-word", "bad_word", "wordblacklist", "word_blacklist", "word-blacklist"], invoke_without_command=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _badword(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:icon_badword:970238990743658518> Bad Words**\n\n> `-badword add <word>`\n> `-badword remove <word>`\n> `-badword show`")

    @_badword.command(name="add", aliases=["a"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _add(self, ctx, word):
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word.lower()])

        if exists is not None:
            return await errorEmbed(self.bot, ctx, "Dieses Wort ist bereits in den Badwords vorhanden.")
        
        insert("badwords", "guild_id, word", [ctx.guild.id, word.lower()])
        await successEmbed(self.bot, ctx, f"**{word} wurde erfolgreich hinzugefügt.**")

    @_badword.command(name="remove", aliases=["del", "delete"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _remove(self, ctx, word):
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word.lower()])

        if exists is None:
            return await errorEmbed(self.bot, ctx, f"{word} ist nicht auf der Badword Liste.")
        
        delete("badwords", "guild_id word", [ctx.guild.id, word.lower()])
        await successEmbed(self.bot, ctx, f"**{word} wurde erfolgreich entfernt.**")

    @_badword.command(name="list", aliases=["show"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _list(self, ctx):
        words = readAll("word", "badwords", "guild_id", [ctx.guild.id])

        if not words:
            return await errorEmbed(self.bot, ctx, "Es gibt noch keine Badwords.")

        string = "".join(f"{word[0]}\n" for word in words)

        await infoEmbed(self.bot, ctx, f"**<:icon_badword:970238990743658518> Bad Words**\n\n{string}")

        

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.guild_permissions.administrator:
            return
        
        if message.content.startswith(getPrefixFromDatabase(message)):
            return

        words = readAll("word", "badwords", "guild_id", [message.guild.id])

        if all(word[0].lower() not in message.content.lower() for word in words):
            return
        
        await infoEmbed(self.bot, message, "**<:icon_badword:970238990743658518> Du darfst dieses Wort nicht sagen.**")
        with contextlib.suppress(Exception):
            message.delete()

def setup(bot):
    bot.add_cog(automod(bot))
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import infoEmbed, errorEmbed, successEmbed
from .utils.database import delete, insert, readOne

class automod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="badword", aliases=["bad-word", "bad_word", "wordblacklist", "word_blacklist", "word-blacklist"], invoke_without_command=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _badword(self, ctx):
        await infoEmbed(self.bot, ctx, "**Bad Words**\n\n> `-badword add <word>`\n> `-badword remove <word>`\n> `-badword show`")

    @_badword.command(name="add", aliases="a")
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _add(self, ctx, word):
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word])

        if exists is not None:
            return await errorEmbed(self.bot, ctx, "Dieses Wort ist bereits in den Badwords vorhanden.")
        
        insert("badwords", "guild_id, word", [ctx.guild.id, word])
        await successEmbed(self.bot, ctx, f"**{word} wurde erfolgreich hinzugefügt.**")

    @_badword.command(name="remove", aliases=["del", "delete"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _remove(self, ctx, word):
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word])

        if exists is None:
            return await errorEmbed(self.bot, ctx, f"{word} ist nicht auf der Badword Liste.")
        
        delete("badwords", "guild_id word", [ctx.guild.id, word])
        await successEmbed(self.bot, ctx, f"**{word} wurde erfolgreich entfernt.**")

def setup(bot):
    bot.add_cog(automod(bot))
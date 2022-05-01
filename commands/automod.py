from ast import alias
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import infoEmbed, errorEmbed, successEmbed
from .utils.database import readOne

class automod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="badword", aliases=["bad-word", "bad_word", "wordblacklist", "word_blacklist", "word-blacklist"], invoke_without_command=True)
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _badword(self, ctx):
        await infoEmbed(self.bot, ctx, "**Bad Words**\n\n> `-badword add <word>`\n> `-badword remove <word>`\n> `-badword show`")

    

def setup(bot):
    bot.add_cog(automod(bot))
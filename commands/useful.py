import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed

class useful(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _ping(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**{self.bot.user.name}'s Latenz**\n\n> **Latenz: `{round(self.bot.latency * 1000)}ms`**"
        )

def setup(bot):
    bot.add_cog(useful(bot))
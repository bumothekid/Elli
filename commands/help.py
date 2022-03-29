import nextcord
from nextcord.ext import commands

class helpcmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def _help(self, interaction):

        await interaction.response.send_message("hilfe ist unterwegs")


def setup(bot):
    bot.add_cog(helpcmd(bot))
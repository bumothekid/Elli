from itsdangerous import NoneAlgorithm
import nextcord
from nextcord.ext.commands import Cog
from .utils.other import getPrefixFromDatabase
from .utils.database import readOne, insert
from .utils.embeds import infoEmbed

class EventsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild):
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[guild.id])

        if prefix is None:
            insert(table="guilds", columns="guild_id, prefix", values=[guild.id, "-"])

        iconURL = guild.icon.url if guild.icon is not None else ""

        await infoEmbed(self,
                        self.bot.get_channel(1087441039855468614),
                        f"**Joined a guild**\n\n> **Name:** {guild.name}\n> **ID:** {guild.id}\n> **Owner:** {guild.owner.name}#{guild.owner.discriminator}\n\n> **Member:** {len(guild.members)}\n> **Icon:** [`📎`Link]({iconURL})\n> **Erstellt am:** {guild.created_at.strftime('%d.%m.%Y')}",
                        color=nextcord.Color.green()
        )

    @Cog.listener()
    async def on_guild_remove(self, guild):
        iconURL = guild.icon.url if guild.icon is not None else ""

        await infoEmbed(self,
                        self.bot.get_channel(1087441039855468614),
                        f"**Left a guild**\n\n> **Name:** {guild.name}\n> **ID:** {guild.id}\n> **Owner:** {guild.owner.name}#{guild.owner.discriminator}\n\n> **Member:** {len(guild.members)}\n> **Icon:** [`📎`Link]({iconURL})\n> **Erstellt am:** {guild.created_at.strftime('%d.%m.%Y')}",
                        color=nextcord.Color.red()
        )

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions and len(message.mentions) == 1 and message.content.startswith("<@"):
            await infoEmbed(self, message, f"> **Die Prefix für diesen Server ist:** `{getPrefixFromDatabase(self, message)[0]}`.")
    



def setup(bot):
    bot.add_cog(EventsCog(bot))
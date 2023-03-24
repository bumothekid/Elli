import nextcord
import contextlib
from nextcord.ext.commands import Cog
from .utils.other import getPrefixFromDatabase
from .utils.database import readOne, insert
from .utils.embeds import infoEmbed, errorEmbed

class EventsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild):
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[guild.id])

        if prefix is None:
            insert(table="guilds", columns="guild_id, prefix, language", values=[guild.id, "-", "en"])

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
            with contextlib.suppress(IndexError):
                argument = message.content.split(" ")[1]
                prefixArgument = message.content.split(" ")[2] if len(message.content.split(" ")) > 2 else None
                if argument == "prefix":
                    if prefixArgument is None:
                        await errorEmbed(self, message, f"Es fehlt ein benötigtes Argument.\n> **Beispiel:** <@{self.bot.user.id}> prefix -")
                        return

                    await self.bot.get_command("prefix").callback(self, message, prefixArgument)

                return
            
            await infoEmbed(self, message, f"**<:Elli:1087732423074259106> {self.bot.user.name}**\n\n> **Server Prefix:** `{getPrefixFromDatabase(self, message)[0]}`\n> **Invite:** `{getPrefixFromDatabase(self, message)[0]}invite`\n> **[`🔗` Support](https://discord.gg/FWPExbfCTa)**\n> **Vote:** *Soon!*", thumbnail=self.bot.user.display_avatar.url, color=nextcord.Color.from_rgb(255, 255, 255))
    



def setup(bot):
    bot.add_cog(EventsCog(bot))
import nextcord
import sqlite3
from nextcord.ext import commands
from nextcord.ext.commands import Cog

class eventsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (guild.id,))
        prefix = c.fetchone()

        if prefix is None:
            c.execute("INSERT INTO guilds(guild_id, prefix) VALUES (?, ?)", (guild.id, "-"))
            db.commit()

        embed = nextcord.Embed(
            description=f"**Joined a guild**\n\n> **Name:** {guild.name}\n> **ID:** {guild.id}\n> **Owner:** {guild.owner.name}#{guild.owner.discriminator}\n\n> **Member:** {len(guild.members)}\n> **Icon:** [`📎`Link]({guild.icon_url})\n> **Erstellt am:** {guild.created_at.strftime('%d.%m.%Y')}",
            color=nextcord.Color.green()
        )

        channel = self.bot.get_channel(786289557805072424)
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_remove(self, guild):
        embed = nextcord.Embed(
            description=f"**Left a guild**\n\n> **Name:** {guild.name}\n> **ID:** {guild.id}\n> **Owner:** {guild.owner.name}#{guild.owner.discriminator}\n\n> **Member:** {len(guild.members)}\n> **Icon:** [`📎`Link]({guild.icon_url})\n> **Erstellt am:** {guild.created_at.strftime('%d.%m.%Y')}",
            color=nextcord.Color.red()
        )

        channel = self.bot.get_channel(786289557805072424)
        await channel.send(embed=embed)



def setup(bot):
    bot.add_cog(eventsCog(bot))
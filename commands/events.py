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

def setup(bot):
    bot.add_cog(eventsCog(bot))
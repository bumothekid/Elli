import nextcord
import sqlite3
from nextcord.ext import commands
from nextcord.ext.commands import Cog

class ticket(Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(ticket(bot))
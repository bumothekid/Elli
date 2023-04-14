
# TODO*: Renew the level system to be more user friendly. (e.g. less code, more functions and less commands.) 

import math
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.database import readOne, readAll, insert, update, delete
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import getPrefixFromDatabase
from .utils.models.LevelingUser import LevelingUser as User
from .utils.models.LevelingGuild import LevelingGuild as Guild
from time import time

languageStrings = {}

class LevelSystem(Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @commands.command(name="level", aliases=["lvl", "rank", "xp", "r"])
    async def level(self, ctx, member: nextcord.Member = None):
        if not checkIfLevelSystemIsEnabled(ctx.guild):
            return await errorEmbed(getLocale(languageStrings, getGuildLanguage(ctx.guild.id), "levelsysNotEnabled"))
        
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if member is None: member = ctx.author
        
        
        user: User = readUser(ctx.guild, member.id)
        allUsers = readAll("user_id", "level_users", "guild_id", ctx.guild.id, "xp DESC")
        
        top10 = False
        placing = 1
        
        for i, databaseUser in enumerate(allUsers):
            if databaseUser[0] == user.user_id:
                if i <= 10: top10 = True
                placing = i + 1
                break
        
        await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysUserLevel", member, user.level, user.xp, user.xp_needed, placing, len(allUsers), getLocale(languageStrings, guildLocale, "yes" if top10 else "no")), thumbnail=member.display_avatar.url, color=member.color)

def checkIfLevelSystemIsEnabled(guild: nextcord.Guild) -> bool:
    """Checks if the level system is enabled in the guild and returns True if it is enabled."""
    enabled = readOne("enabled", "level_system", "guild_id", [guild.id])

    return False if enabled is None else enabled[0] == 1

def readUser(guild: nextcord.Guild, userID: int) -> User:
    """Reads the user from the database and returns a User object."""
    databaseUser = readOne("messages, level, xp, cooldown", "level_users", "guild_id user_id", [guild.id, userID])
    
    if databaseUser is None:
        insert("level_users", "guild_id, user_id, messages, level, xp, cooldown", [guild.id, userID, 0, 1, 0, time()])
        return User(userID, 0, 1, 0, time(), 27)
    
    xpNeeded = 27 if databaseUser[1] == 1 else math.ceil(10 * (databaseUser[1] ** 1.5) + 20)
    
    return User(userID, databaseUser[0], databaseUser[1], databaseUser[2], databaseUser[3], xpNeeded)

def readGuild(guild: nextcord.Guild) -> Guild:
    """Reads the guild from the database and returns a Guild object."""
    databaseGuild = readOne("enabled, cooldown, mention, message", "level_system", "guild_id", [guild.id])
    
    if databaseGuild is None:
        insert("level_system", "guild_id, enabled, xp, cooldown, mention, message", [guild.id, 0, 3, 6, 1, getLocale(languageStrings, getGuildLanguage(guild.id), "levelsysDefaultMessage")])
        return Guild(guild.id, False, 6, True, getLocale(languageStrings, getGuildLanguage(guild), "levelsysDefaultMessage"))
    
    return Guild(guild.id, databaseGuild[0] == 1, databaseGuild[1], databaseGuild[2] == 1, databaseGuild[3])

def addUserXP(guild: Guild, user: User) -> bool:
    """Adds the xp to the user and returns True if the user leveled up."""
    if time() - user.cooldown < guild.cooldown: return
    
    user.xp += guild.xp
    user.messages += 1
    user.cooldown = time()
    
    if user.xp >= user.xp_needed:
        user.level += 1
        user.xp_needed = 27 if user.level == 1 else math.ceil(10 * (user.level ** 1.5) + 20)
        
        update("level_users", "messages level xp cooldown", "guild_id user_id", [user.messages, user.level, user.xp, user.cooldown, guild.guild_id, user.user_id])
        return True
    
    update("level_users", "messages xp cooldown", "guild_id user_id", [user.messages, user.xp, user.cooldown, guild.guild_id, user.user_id])
    return False


def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("levelsys")
    bot.add_cog(LevelSystem(bot))
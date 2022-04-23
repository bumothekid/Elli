import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.database import readOne, readAll, update, insert, delete

class levelingSystem(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name="leveling", aliases=["levelsystem", "levelingsystem", "levelsys", "levelingsys", "levelingsetup", "levelsetup"], invoke_without_command=True)
    async def _leveling(self, ctx):
        await infoEmbed(self.bot, ctx, "** Leveling System**\n\n"
                                        "> `-leveling <on | off>`\n"
                                        "> `-leveling settings xp <anzahl>`\n"
                                        "> `-leveling settings cooldown <seconds>`\n"
                                        "> `-leveling settings message set <text>`\n"
                                        "> `-leveling settings message ping <on | off>`\n"
                                        "> `-leveling settings message rankup set <text>`\n"
                                        "> `-leveling settings message rankup remove`\n"
                                        "> `-leveling settings message rankup show`\n"
                                        "> `-leveling settings message show`\n"
                                        "> `-leveling settings show`\n\n"
                                        "> Variablen für die Level Up Nachricht `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{level}`, `{xp_needed}` und `{role}` für Rank Up Nachrichten\n"
        )
    
    @_leveling.command(name="on", aliases=["enable", "e", "o"])
    async def _on(self, ctx):
        if checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Leveling System ist bereits aktiviert.")

        update("leveling_system", "enabled", "guild_id", [1, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Das Leveling System wurde aktiviert.")
    
    @_leveling.command(name="off", aliases=["disable", "d", ""])
    async def _off(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Leveling System ist bereits deaktiviert.")

        update("leveling_system", "enabled", "guild_id", [0, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Das Leveling System wurde deaktiviert.")

def checkLevelOn(guildid: int) -> bool:
    enabled = readOne("enabled", "leveling_system", "guild_id", guildid)

    if enabled is None:
        levelupmessage = "Glückwunsch **{user_name}#{user_discriminator}**!\n\nDu bist ein Level aufgestiegen!\nDu bist nun `{level}` Level\nDu brauchst `{xp_needed}` XP bis zum nächsten Level."
        rankupmessage = "Glückwunsch **{user_name}#{user_discriminator}**!\n\nDu bist ein Level aufgestiegen und hast die Rolle {role} erhalten!\nDu bist nun `{level}` Level\nDu brauchst `{xp_needed}` XP bis zum nächsten Level."
        insert("leveling_system", "guild_id, enabled, xp, cooldown, mention, message_levelup, message_rankup", [guildid, 0, 3, 3, 1, levelupmessage, rankupmessage])
        return False
    
    return enabled[0] == 1
    
def setup(bot):
    bot.add_cog(levelingSystem(bot))
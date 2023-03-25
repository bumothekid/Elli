import contextlib
import nextcord

from nextcord.ext import commands
from .utils.embeds import infoEmbed, errorEmbed
from .utils.database import readOne, readAll, insert, delete
from nextcord.ext.commands import Cog
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale

languageStrings = {}

class Autoroles(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name="autoroles", invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def autoroles(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne("prefix", "guilds", "guild_id", ctx.guild.id)[0]
        
        await infoEmbed(self, ctx, getLocale(languageStrings, guildLocale, "autorolesHelp", prefix))

    @autoroles.command(name="add")
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def add(self, ctx, role: nextcord.Role):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if role.position >= ctx.author.top_role.position:
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "userRoleHigher"))
            return

        if role.position >= ctx.guild.me.top_role.position or not role.is_assignable():
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "botRoleHigher"))
            return

        if (
            readAll("role_id", "autoroles", "guild_id", ctx.guild.id) is not None
            and len(readAll("role_id", "autoroles", "guild_id", ctx.guild.id))
            >= 10
        ):
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "maxAutoroles"))
            return

        if readOne("role_id", "autoroles", "role_id", role.id) is not None:
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "roleAlreadyAdded"))
            return

        insert("autoroles", "guild_id, role_id", [ctx.guild.id, role.id])
        await infoEmbed(self, ctx, getLocale(languageStrings, guildLocale, "roleAdded", role.name))

    @autoroles.command(name="remove")
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def remove(self, ctx, role: nextcord.Role):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if role.position >= ctx.author.top_role.position:
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "userRoleHigher"))
            return
        
        if role.position >= ctx.guild.me.top_role.position or not role.is_assignable():
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "botRoleHigher"))
            return

        if readOne("role_id", "autoroles", "role_id", role.id) is None:
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "roleNotAdded"))
            return
        
        delete("autoroles", "role_id", role.id)
        await infoEmbed(self, ctx, getLocale(languageStrings, guildLocale, "roleRemoved", role.name))

    @autoroles.command(name="list", aliases=["show"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def list(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        roles = readAll("role_id", "autoroles", "guild_id", ctx.guild.id)

        if len(roles) == 0:
            await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "noAutoroles"))
            return
        
        roleList = "".join([f"> {ctx.guild.get_role(role[0]).mention}\n" for role in roles])

        await infoEmbed(self, ctx, getLocale(languageStrings, guildLocale, "roleList", roleList))

    @Cog.listener()
    async def on_member_join(self, member):
        roles = readAll("role_id", "autoroles", "guild_id", member.guild.id)

        if len(roles) == 0:
            return
        
        with contextlib.suppress(nextcord.Forbidden, nextcord.HTTPException, nextcord.NotFound):
            await member.add_roles(*[member.guild.get_role(role[0]) for role in roles], reason="Autoroles")

    @Cog.listener()
    async def on_guild_role_delete(self, role):
        roles = readAll("role_id", "autoroles", "guild_id", role.guild.id)

        if len(roles) == 0:
            return
        
        if role.id in [role[0] for role in roles]:
            delete("autoroles", "role_id", role.id)

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("autoroles")
    bot.add_cog(Autoroles(bot))
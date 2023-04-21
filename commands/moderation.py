import re
from time import mktime
import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog, BucketType
from .utils.database import readOne
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import messagePinned
from datetime import datetime, timedelta

languageStrings = {}

class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="moderation", aliases=["mod"])
    @commands.cooldown(2, 10, BucketType.user)
    async def _moderation(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne("prefix", "guilds", "guild_id", ctx.guild.id)[0]

        await infoEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "moderationDescription", prefix))

    @commands.command(name="clear", aliases=["clr", "clean"])
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, BucketType.user)
    async def _clear(self, ctx, amount: int):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if amount < 1:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "clearAtLeastOne"))
        
        if amount > 200:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "clearMax200"))

        await ctx.channel.purge(limit=amount + 1, check=messagePinned)
        await successEmbed(self.bot, ctx.channel, getLocale(self.bot, languageStrings, guildLocale, "clearSuccess", amount), delete_after=10)
    
    @commands.command(name="kick", aliases=["k"])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _kick(self, ctx, member: nextcord.Member, *, reason: str = None):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if reason is None:
            reason = getLocale(self.bot, languageStrings, guildLocale, "noReason")

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "kickYourself"))
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "kickBot"))
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "kickHigherRole"))
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "kickBotHigherRole"))

        await member.kick(reason=reason)
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "kickSuccess", member))

    @commands.command(name="ban", aliases=["b"])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _ban(self, ctx, member: nextcord.Member, *, reason: str = None):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if reason is None:
            reason = getLocale(self.bot, languageStrings, guildLocale, "noReason")

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "banYourself"))
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "banBot"))
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "banHigherRole"))
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "banBotHigherRole"))

        await member.ban(reason=reason)
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "banSuccess", member))

    @commands.command(name="mute", aliases=["timeout"])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _mute(self, ctx, member: nextcord.Member, *, time: str):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteYourself"))
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteBot"))
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteHigherRole"))
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteBotHigherRole"))

        timeRegex = re.compile(r'(?:(\d{1,5})(d|h|m|s))+?')
        timeDict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

        matches = re.findall(timeRegex, time)
        seconds = 0

        if not matches:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteInvalidTime"))

        for key, value in matches:    
            try:
                seconds += timeDict[value] * float(key)
            except KeyError:
                await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteInvalidTimeUnit"))
                continue
            except ValueError:
                await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteInvalidTimeValue"))
                continue
            except Exception as e:
                print(e)
                await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteUnknownError"))
                continue

        if seconds < 30:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteMin30"))

        if seconds > 28 * 86400:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteMax28"))

        now = datetime.utcnow()
        unixnow = datetime.now()
        await member.timeout(timeout=now + timedelta(seconds=seconds), reason=f"Mute | {ctx.author}")
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "muteSuccess", member, int(mktime((unixnow + timedelta(seconds=seconds)).timetuple()))))

    @commands.command(name="unmute", aliases=["untimeout"])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _unmute(self, ctx, member: nextcord.Member):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "unmuteYourself"))
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "unmuteBot"))
        
        if not member.is_timed_out:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "unmuteNotMuted"))
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "unmuteHigherRole"))
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "unmuteBotHigherRole"))

        await member.timeout(timeout=None, reason=f"Unmute | {ctx.author}")
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "unmuteSuccess", member))

    @commands.command(name="addrole", aliases=["addr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(2, 20, BucketType.user)
    async def _addrole(self, ctx, member: nextcord.Member, role: nextcord.Role):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "addroleYourself"))
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "addroleBot"))

        if role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "addroleHigherRole"))

        if role.position >= ctx.guild.me.top_role.position or not role.is_assignable():
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "addroleBotHigherRole"))
        
        if role in member.roles:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "addroleAlreadyHasRole"))

        await member.add_roles(role)
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "addroleSuccess", member, role))
    
    @commands.command(name="removerole", aliases=["remr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(2, 20, BucketType.user)
    async def _removerole(self, ctx, member: nextcord.Member, role: nextcord.Role):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "removeroleYourself"))
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "removeroleBot"))
        
        if role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "removeroleHigherRole"))

        if role.position >= ctx.guild.me.top_role.position or not role.is_assignable():
            return await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "removeroleBotHigherRole"))

        await member.remove_roles(role)
        await successEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "removeroleSuccess", member, role))

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("moderation")
    bot.add_cog(Moderation(bot))

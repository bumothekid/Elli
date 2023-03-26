import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog

from .utils.other import capString
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.embeds import successEmbed, errorEmbed, infoEmbed, devLogging

languageStrings = {}

class Useful(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", aliases=["latency"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _ping(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)

        await infoEmbed(
            self,
            ctx,
            getLocale(languageStrings, guildLocale, "pingDescription", round(self.bot.latency * 1000))
        )

    @commands.command(name="userinfo", aliases=["user", "ui"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _userinfo(self, ctx, member: nextcord.Member = None):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if member is None:
            member = ctx.author

        await infoEmbed(
            self,
            ctx,
            getLocale(languageStrings, guildLocale, "userinfoDescription", member.name, member, member.id, capString(str(member.status)), member.display_avatar.url, int(member.joined_at.timestamp()), int(member.created_at.timestamp())),
            thumbnail=member.display_avatar.url
        )

    @commands.command(name="serverinfo", aliases=["server", "si"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _serverinfo(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        iconURL = ctx.guild.icon.url if ctx.guild.icon is not None else ""

        await infoEmbed(
            self,
            ctx,
            getLocale(languageStrings, guildLocale, "serverinfoDescription", ctx.guild.name, ctx.guild.id, ctx.guild.owner, capString(str(ctx.guild.verification_level)), ctx.guild.premium_tier, ctx.guild.premium_subscription_count, len(ctx.guild.members), iconURL, int(ctx.guild.created_at.timestamp())),
            thumbnail=iconURL
        )
    
    @commands.command(name="avatar", aliases=["pfp", "profile", "av"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _avatar(self, ctx, member: nextcord.Member = None):
        if member is None:
            member = ctx.author

        await infoEmbed(
            self,
            ctx,
            f"**{member.name}'s Avatar**\n\n> **Avatar: [`📎` Link]({member.display_avatar.url})**",
            thumbnail=member.display_avatar.url
        )

    @commands.command(name="bug", aliases=['bugreport', "report"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _bug(self, ctx, *, bug):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if len(bug) < 10:
            return await errorEmbed(self, ctx, getLocale(languageStrings, guildLocale, "bugTooShort"))
        

        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "bugReported", bug))
        await devLogging(self, ctx, f"{ctx.author} hat einen Bugreport gemeldet:\n> **{bug}**")

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("useful")
    bot.add_cog(Useful(bot))
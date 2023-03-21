import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog

from .utils.other import capString
from .utils.embeds import successEmbed, errorEmbed, infoEmbed, devLogging

class useful(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", aliases=["latency"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _ping(self, ctx):
        await infoEmbed(
            self,
            ctx,
            f"**{self.bot.user.name}'s Latenz**\n\n> **Latenz: `{round(self.bot.latency * 1000)}ms`**"
        )

    @commands.command(name="userinfo", aliases=["user", "ui"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _userinfo(self, ctx, member: nextcord.Member = None):
        if member is None:
            member = ctx.author

        await infoEmbed(
            self,
            ctx,
            f"**{member.name}'s Userinfo**\n\n> **User Name:** `{member}`\n> **User ID: `{member.id}`**\n> **Status: `{capString(str(member.status))}`**\n\n> **Avatar: [`📎` Link]({member.display_avatar.url})**\n> **Gejoint: **<t:{int(member.joined_at.timestamp())}:R>\n> **Erstellt: <t:{int(member.created_at.timestamp())}:R>**",
            thumbnail=member.display_avatar.url
        )

    @commands.command(name="serverinfo", aliases=["server", "si"])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def _serverinfo(self, ctx):
        iconURL = ctx.guild.icon.url if ctx.guild.icon is not None else ""

        await infoEmbed(
            self,
            ctx,
            f"**{ctx.guild.name}'s Serverinfo**\n\n> **Server Name:** `{ctx.guild.name}`\n> **Server ID: `{ctx.guild.id}`**\n> **Server Owner: `{ctx.guild.owner}`**\n\n> **Verifikations Stufe: `{capString(str(ctx.guild.verification_level))}`**\n> **Boost Stufe: `{ctx.guild.premium_tier}`**\n> **Boost Anzahl: `{ctx.guild.premium_subscription_count}`**\n\n> **Mitglieder: `{len(ctx.guild.members)}`**\n> **Server Icon:** [`📎` Link]({iconURL})\n> **Server Erstellt: <t:{int(ctx.guild.created_at.timestamp())}:R>**",
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
        if len(bug) < 10:
            return await errorEmbed(self, ctx, "Der Bugreport muss mindestens 10 Zeichen lang sein.")
        
        await successEmbed(self, ctx, f"**<:icon_bug:966028792890003547> Bugreport**\n\n> **Bugreport:** `{bug}`")
        await devLogging(self, ctx, f"{ctx.author} hat einen Bugreport gemeldet:\n> **{bug}**")

def setup(bot):
    bot.add_cog(useful(bot))
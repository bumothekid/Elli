import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog

from .utils.other import capString
from .utils.embeds import successEmbed, errorEmbed, infoEmbed

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

def setup(bot):
    bot.add_cog(useful(bot))
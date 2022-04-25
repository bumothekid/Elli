import asyncio
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog, BucketType
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import messagePinned

class moderation(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="moderation", aliases=["mod"])
    @commands.cooldown(2, 10, BucketType.user)
    async def _moderation(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:icon_moderation:967038345395961896> Moderations Befehle**\n\n> `-clear <anzahl>`\n> `> kick <@user> <grund>`\n> `-ban <@user> <grund>`\n> `-addrole <@user> <@rolle>`\n> `-removerole <@user> <@rolle>`")

    @commands.command(name="clear", aliases=["clr", "clean"])
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, BucketType.user)
    async def _clear(self, ctx, amount: int):
        if amount > 200:
            return await errorEmbed(self.bot, ctx, "Du kannst maximal 200 Nachrichten löschen.")

        await ctx.channel.purge(limit=amount + 1, check=messagePinned)
        await successEmbed(self.bot, ctx.channel, f"**<:icon_moderation:967038345395961896> {amount} Nachrichten gelöscht.**", delete_after=10)
    
    @commands.command(name="kick", aliases=["k"])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _kick(self, ctx, member: nextcord.Member, *, reason: str = None):
        if reason is None:
            reason = "Kein Grund angegeben."

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, "Du kannst dich nicht selbst kicken.")
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, "Ich kann mich nicht selbst kicken.")
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, "Du kannst diesen User nicht kicken.")

        await member.kick(reason=reason)
        await successEmbed(self.bot, ctx, f"**<:icon_moderation:967038345395961896> {member} wurde gekickt.**")

    @commands.command(name="ban", aliases=["b"])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _ban(self, ctx, member: nextcord.Member, *, reason: str = None):
        if reason is None:
            reason = "Kein Grund angegeben."

        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, "Du kannst dich nicht selbst bannen.")
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, "Ich kann mich nicht selbst bannen.")
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, "Du kannst diesen User nicht bannen.")

        await member.ban(reason=reason)
        await successEmbed(self.bot, ctx, f"**<:icon_moderation:967038345395961896> {member} wurde gebannt.**")

    @commands.command(name="addrole", aliases=["addr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(2, 20, BucketType.user)
    async def _addrole(self, ctx, member: nextcord.Member, role: nextcord.Role):
        if role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, f"Du kannst {member.mention} diese Rolle nicht geben.")

        bot = ctx.guild.get_member(self.bot.user.id)

        if role.position >= bot.top_role.position or member.top_role.position >= bot.top_role.position or role.name == "@everyone":
            return await errorEmbed(self.bot, ctx, f"Ich kann {member.mention} diese Rolle nicht geben.")

        await member.add_roles(role)
        await successEmbed(self.bot, ctx, f"**<:icon_moderation:967038345395961896> {member} hat die Rolle {role} erhalten.**")
    
    @commands.command(name="removerole", aliases=["remr"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.cooldown(2, 20, BucketType.user)
    async def _removerole(self, ctx, member: nextcord.Member, role: nextcord.Role):
        if role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, f"Du kannst {member.mention} diese Rolle nicht entziehen.")

        bot = ctx.guild.get_member(self.bot.user.id)

        if role.position >= bot.top_role.position or member.top_role.position >= bot.top_role.position:
            return await errorEmbed(self.bot, ctx, f"Ich kann {member.mention} diese Rolle nicht entziehen.")

        await member.remove_roles(role)
        await successEmbed(self.bot, ctx, f"**<:icon_moderation:967038345395961896> {member} hat die Rolle {role} entzogen.**")

def setup(bot):
    bot.add_cog(moderation(bot))

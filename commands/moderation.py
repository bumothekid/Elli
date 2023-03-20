import re
from time import mktime
import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog, BucketType
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import messagePinned
from datetime import datetime, timedelta

class moderation(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="moderation", aliases=["mod"])
    @commands.cooldown(2, 10, BucketType.user)
    async def _moderation(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:Moderator:1087456158421352508> Moderations Befehle**\n\n> `-clear <anzahl>`\n> `> kick <@user> <grund>`\n> `-ban <@user> <grund>`\n> `-addrole <@user> <@rolle>`\n> `-removerole <@user> <@rolle>`")

    @commands.command(name="clear", aliases=["clr", "clean"])
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, BucketType.user)
    async def _clear(self, ctx, amount: int):
        if amount > 200:
            return await errorEmbed(self.bot, ctx, "Du kannst maximal 200 Nachrichten löschen.")

        await ctx.channel.purge(limit=amount + 1, check=messagePinned)
        await successEmbed(self.bot, ctx.channel, f"**<:Moderator:1087456158421352508> {amount} Nachrichten gelöscht.**", delete_after=10)
    
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
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, "Ich habe nicht genug Berechtigungen um diesen User zu kicken.")

        await member.kick(reason=reason)
        await successEmbed(self.bot, ctx, f"**<:Moderator:1087456158421352508> {member} wurde gekickt.**")

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
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, "Ich habe nicht genug Berechtigungen um diesen User zu bannen.")

        await member.ban(reason=reason)
        await successEmbed(self.bot, ctx, f"**<:Moderator:1087456158421352508> {member} wurde gebannt.**")

    @commands.command(name="mute", aliases=["timeout"])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _mute(self, ctx, member: nextcord.Member, *, time: str):
        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, "Du kannst dich nicht selbst muten.")
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, "Ich kann mich nicht selbst muten.")
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, "Du kannst diesen User nicht muten.")
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, "Ich habe nicht genug Berechtigungen um diesen User zu muten.")

        timeRegex = re.compile(r'(?:(\d{1,5})(d|h|m|s))+?')
        timeDict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

        matches = re.findall(timeRegex, time)
        seconds = 0

        if not matches:
            return await errorEmbed(self.bot, ctx, "Bitte gib eine gültige Zeitangabe an. `<s | m | h | d>`")

        for key, value in matches:    
            try:
                seconds += timeDict[value] * float(key)
            except KeyError:
                await errorEmbed(self.bot, ctx, f"`{value}` ist kein gültiger Wert. `<s | m | h | d>`")
                continue
            except ValueError:
                await errorEmbed(self.bot, ctx, f"`{key}` ist keine ganze Zahl.")
                continue
            except Exception as e:
                print(e)
                await errorEmbed(self.bot, ctx, "Ein unbekannter Fehler ist aufgetreten.")
                continue

        if seconds < 30:
            return await errorEmbed(self.bot, ctx, "Du musst mindestens `30` Sekunden muten.")

        if seconds > 28 * 86400:
            return await errorEmbed(self.bot, ctx, "Du kannst maximal `28` Tage muten.")

        now = datetime.utcnow()
        unixnow = datetime.now()
        await member.timeout(timeout=now + timedelta(seconds=seconds), reason=f"Mute von {ctx.author}")
        await successEmbed(self.bot, ctx, f"{member} wurde bis <t:{int(mktime((unixnow + timedelta(seconds=seconds)).timetuple()))}:R> (<t:{int(mktime((unixnow + timedelta(seconds=seconds)).timetuple()))}:f>) gemutet.")

    @commands.command(name="unmute", aliases=["untimeout"])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.cooldown(5, 10, BucketType.user)
    async def _unmute(self, ctx, member: nextcord.Member, *, reason: str = None):
        if member == ctx.author:
            return await errorEmbed(self.bot, ctx, "Du kannst dich nicht selbst entmuten.")
        
        if member == self.bot.user:
            return await errorEmbed(self.bot, ctx, "Ich kann mich nicht selbst entmuten.")
        
        if member.top_role.position >= ctx.author.top_role.position:
            return await errorEmbed(self.bot, ctx, "Du kannst diesen User nicht unmuten.")
        
        if member.top_role.position >= ctx.me.top_role.position:
            return await errorEmbed(self.bot, ctx, "Ich habe nicht genug Berechtigungen um diesen User zu entmuten.")

        await member.timeout(timeout=None, reason=f"Unmute von {ctx.author}")
        await successEmbed(self.bot, ctx, f"{member} wurde entmutet.")

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
        await successEmbed(self.bot, ctx, f"**<:Moderator:1087456158421352508> {member} hat die Rolle {role} erhalten.**")
    
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
        await successEmbed(self.bot, ctx, f"**<:Moderator:1087456158421352508> {member} hat die Rolle {role} entzogen.**")

def setup(bot):
    bot.add_cog(moderation(bot))

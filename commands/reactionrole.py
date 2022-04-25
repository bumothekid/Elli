import contextlib
import nextcord
import re
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import errorEmbed, infoEmbed, successEmbed
from .utils.database import readOne, insert, delete

class reactionrole(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="rr", aliases=["reactionrole"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _rr(self, ctx):
        await infoEmbed(self, ctx, "**🎭 Reactionrole einrichtung**\n\n> `-rr create <#channel> <messageid> <emote> <@&rolle>`\n> `-rr delete <#channel> <messageid> <emote>`")

    @_rr.command(name="create", aliases=["add"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _create(self, ctx, channel: nextcord.TextChannel, message, reaction: str, role: nextcord.Role):
        exists = readOne(columns="*", table="reactionroles", where="guild_id message_id reaction", values=[ctx.guild.id, message, reaction])

        if exists is not None:
            return await errorEmbed(self, ctx, "Du hast bereits eine Reactionrole mit diesem Emote bei dieser Nachricht.")

        if "<:" in reaction:
            reaction_id = re.findall(r"[0-9]+", reaction)[0]
            emote = self.bot.get_emoji(int(reaction_id))
            
            if emote is None:
                raise commands.EmojiNotFound(argument=reaction)

            try:
                message = await self.bot.get_channel(channel.id).fetch_message(message)
            except:
                raise commands.MessageNotFound(argument=message)

            await message.add_reaction(emote)
        else:
            try:
                message = await self.bot.get_channel(channel.id).fetch_message(message)
            except:
                raise commands.MessageNotFound(argument=message)

            try:
                await message.add_reaction(reaction)
            except:
                raise commands.EmojiNotFound(argument=reaction)

        insert(table="reactionroles", columns="guild_id, channel_id, message_id, reaction, role_id", values=[ctx.guild.id, channel.id, message.id, reaction, role.id])
        await successEmbed(self, ctx, f"**🎭 Die Reactionrole wurde eingerichtet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id})\n> **Emote:** {reaction}\n> **Rolle:** {role.mention}")

    @_rr.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _delete(self, ctx, channel: nextcord.TextChannel, message, reaction: str):
        exists = readOne(columns="*", table="reactionroles", where="guild_id message_id reaction", values=[ctx.guild.id, message, reaction])

        if exists is None:
            return await errorEmbed(self, ctx, "Du hast keine Reactionrole mit diesem Emote bei dieser Nachricht.")
        
        try:
            message = await self.bot.get_channel(channel.id).fetch_message(message)
        except:
            raise commands.MessageNotFound(argument=message)
            
        role = ctx.guild.get_role(int(exists[4]))

        if "<:" in reaction:
            reaction_id = re.findall(r"[0-9]+", reaction)[0]
            reaction = self.bot.get_emoji(int(reaction_id))
        
        try:
            await message.remove_reaction(reaction, self.bot.user)
        except:
            raise commands.EmojiNotFound(argument=reaction)

        delete(table="reactionroles", where="guild_id message_id reaction", values=[ctx.guild.id, message.id, reaction])
        await successEmbed(self, ctx, f"**🎭 Die Reactionrole wurde entfernt**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id})\n> **Emote:** {reaction}\n> **Rolle:** {role.mention}")


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        reactionrole = readOne(columns="role_id", table="reactionroles", where="guild_id message_id reaction", values=[payload.guild_id, payload.message_id, str(payload.emoji)])

        if reactionrole is not None:
            role = guild.get_role(reactionrole[0])

            with contextlib.suppress(Exception):
                await payload.member.add_roles(role, reason="Reactionrole")

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:
            return

        reactionrole = readOne(columns="role_id", table="reactionroles", where="guild_id message_id reaction", values=[payload.guild_id, payload.message_id, str(payload.emoji)])

        if reactionrole is not None:
            role = guild.get_role(reactionrole[0])

            with contextlib.suppress(Exception):
                await member.remove_roles(role, reason="Reactionrole")


        



    
    
def setup(bot):
    bot.add_cog(reactionrole(bot))
import contextlib
import nextcord
import sqlite3
import re
from nextcord.ext import commands
from nextcord.ext.commands import Cog

class reactionrole(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="rr", aliases=["reactionrole"], invoke_without_command=True)
    async def _rr(self, ctx):
        embed = nextcord.Embed(
            description="**🎭 Reactionrole einrichtung**\n\n> `!rr create <#channel> <messageid> <emote> <@&rolle>`\n> `!rr delete <#channel> <messageid> <emote>`",
            color=nextcord.Color.blurple()
        )

        return await ctx.reply(embed=embed)



    @_rr.command(name="create", aliases=["add"])
    @commands.has_permissions(manage_guild=True)
    async def _create(self, ctx, channel: nextcord.TextChannel, message, reaction: str, role: nextcord.Role):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM reactionroles WHERE guild_id = '{ctx.guild.id}' AND message_id = '{ctx.message.id}' AND reaction = '{reaction}'")
        exists = c.fetchone()

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

        if exists is not None: 
            embed = nextcord.Embed(
                description="Du hast bereits eine Reactionrole mit diesem Emote bei dieser Nachricht",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        c.execute("INSERT INTO reactionroles(guild_id, channel_id, message_id, reaction, role_id) VALUES(?, ?, ?, ?, ?)", [ctx.guild.id, channel.id, message.id, reaction, role.id])

        embed = nextcord.Embed(
            description=f"**🎭 Die Reactionrole wurde eingerichtet**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id})\n> **Emote:** {reaction}\n> **Rolle:** {role.mention}",
            color=nextcord.Color.dark_green()
        )
        
        await ctx.reply(embed=embed)

        db.commit()

    @_rr.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    async def _delete(self, ctx, channel: nextcord.TextChannel, message, reaction: str):
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT * FROM reactionroles WHERE guild_id = '{ctx.guild.id}' AND message_id = '{message}' AND reaction = '{reaction}'")
        exists = c.fetchone()

        if exists is None:
            embed = nextcord.Embed(
                description="Du hast keine Reactionrole mit diesem Emote bei dieser Nachricht",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)
        
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

        c.execute(f"DELETE FROM reactionroles WHERE guild_id = '{ctx.guild.id}' AND message_id = '{message.id}' AND reaction = '{reaction}'")

        embed = nextcord.Embed(
            description=f"**🎭 Die Reactionrole wurde entfernt**\n\n> **Channel:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id})\n> **Emote:** {reaction}\n> **Rolle:** {role.mention}",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

        db.commit()


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT role_id FROM reactionroles WHERE guild_id = '{payload.guild_id}' AND message_id = '{payload.message_id}' AND reaction = '{str(payload.emoji)}'")
        reactionrole = c.fetchone()

        guild = self.bot.get_guild(payload.guild_id)

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

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT role_id FROM reactionroles WHERE guild_id = '{payload.guild_id}' AND message_id = '{payload.message_id}' AND reaction = '{str(payload.emoji)}'")
        reactionrole = c.fetchone()

        if reactionrole is not None:
            role = guild.get_role(reactionrole[0])

            with contextlib.suppress(Exception):
                await member.remove_roles(role, reason="Reactionrole")


        



    
    
def setup(bot):
    bot.add_cog(reactionrole(bot))
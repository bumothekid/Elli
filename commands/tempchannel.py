import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.other import safeDict
from .utils.database import readOne, readAll, insert, update, delete
from .utils.embeds import infoEmbed, successEmbed, errorEmbed
from .utils.language import getLanguageStrings, getGuildLanguage, getLocale

languageStrings = {}
class Tempchannel(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="tempchannel", invoke_without_command=True, aliases=['temp'])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _tempchannel(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])[0]
        
        await infoEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "tempchannelDescription", prefix))

    @_tempchannel.command(name="add", aliases=['create', 'set'])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _add(self, ctx, channel: nextcord.VoiceChannel):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if channel not in ctx.guild.voice_channels:
            raise commands.ChannelNotFound(channel)

        tempchannel = readOne(columns="*", table="tempchannels", where="guild_id", values=[ctx.guild.id])

        if tempchannel is not None:
            update(table="tempchannels", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])
            
            return await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "tempchannelSet", channel.name, tempchannel[2]))

        insert(table="tempchannels", columns="guild_id, channel_id, name", values=[ctx.guild.id, channel.id, "⏳ {name}"])
        
        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "tempchannelSet", channel.name, "⏳ {name}"))

    @_tempchannel.command(name="remove", aliases=['delete', 'del'])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        tempchannel = readOne(columns="*", table="tempchannels", where="guild_id", values=[ctx.guild.id])

        if tempchannel is None or tempchannel[1] is None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "tempchannelNotSet"))

        update(table="tempchannels", columns="channel_id", where="guild_id", values=["NULL", ctx.guild.id])
        
        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "tempchannelRemoved", tempchannel[1], tempchannel[2]))

    @_tempchannel.command(name="name", aliases=['setname'])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _name(self, ctx, *, name):
        guildLocale = getGuildLanguage(ctx.guild.id)
        tempchannel = readOne(columns="*", table="tempchannels", where="guild_id", values=[ctx.guild.id])

        if tempchannel is None or tempchannel[1] is None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "tempchannelNotSet"))

        update(table="tempchannels", columns="name", where="guild_id", values=[name, ctx.guild.id])
        
        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "tempchannelNameSet", tempchannel[1], name))

    @Cog.listener()
    async def on_ready(self):
        open_tempchannels = readAll(columns="channel_id", table="open_tempchannels")

        for tempchannel in open_tempchannels:
            channel = self.bot.get_channel(tempchannel[0])

            if not channel:
                delete(table="open_tempchannels", where="channel_id", values=[tempchannel[0]])
                continue

            if len(channel.members) == 0:
                await channel.delete()

                delete(table="open_tempchannels", where="channel_id", values=[tempchannel[0]])
                continue

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # sourcery skip: merge-nested-ifs, remove-redundant-fstring
        tempchannels = readAll(columns="*", table="open_tempchannels", where="guild_id", values=[member.guild.id])
        tempchannel = readOne(columns="*", table="tempchannels", where="guild_id", values=[member.guild.id])

        if tempchannels:
            if before.channel:
                if before.channel.id in [tempchannel[1] for tempchannel in tempchannels]:
                    if len(before.channel.members) == 0:
                        delete(table="open_tempchannels", where="guild_id channel_id", values=[member.guild.id, before.channel.id])

                        await before.channel.delete(reason="Tempchannel empty")

        if tempchannel is not None:
            if after.channel:
                if after.channel.id == tempchannel[1]:
                    memberPermissions = nextcord.PermissionOverwrite(manage_permissions=True, move_members=True, manage_channels=True)

                    name = tempchannel[2].format_map(safeDict(user=member.name, amount=len(tempchannels) + 1))

                    tempchannel = await after.channel.clone(name=name, reason="Tempchannel erstellen")

                    await tempchannel.set_permissions(member, overwrite=memberPermissions)
                    await tempchannel.set_permissions(member.guild.default_role, overwrite=nextcord.PermissionOverwrite(speak=True))

                    try:
                        await member.move_to(tempchannel)
                    except nextcord.errors.HTTPException:
                        await tempchannel.delete()

                    insert(table="open_tempchannels", columns="guild_id, channel_id, host_id, name", values=[member.guild.id, tempchannel.id, member.id, tempchannel.name])


def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("tempchannel")
    bot.add_cog(Tempchannel(bot))
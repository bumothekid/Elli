import math
import nextcord
import contextlib
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.database import readOne, readAll, insert, update, delete
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.other import getPrefixFromDatabase, safeDict
from .utils.models.LevelingUser import LevelingUser as User
from .utils.models.LevelingGuild import LevelingGuild as Guild
from .utils.models.EmbedField import EmbedField
from time import time

cache = []
languageStrings = {}

class LevelSystem(Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot: return
        if message.content.startswith(getPrefixFromDatabase(self.bot, message)[0]): return
        if message.guild is None: return
        if not checkIfLevelSystemIsEnabled(message.guild): return
        
        guild: Guild = readGuild(message.guild)
        
        if message.channel.id in guild.blacklist_channel: return
        if any(role.id in guild.blacklist_roles for role in message.author.roles): return
        
        user: User = readUser(message.guild, message.author.id)
        
        if addUserXP(guild, user):
            user: User = readUser(message.guild, message.author.id)
            
            messageToSend = guild.message
            mention = f"{message.author.mention}"
            channel = message.channel
            
            if customMessage := guild.custom_messages.get(user.level):
                messageToSend = customMessage
                
            role = None
                
            if role := guild.roles.get(user.level):
                for oldRoles in guild.roles.values():
                    with contextlib.suppress(Exception):
                        oldRole = message.guild.get_role(oldRoles)
                        
                        if oldRole is None: continue
                        
                        if oldRole in message.author.roles:
                            await message.author.remove_roles(oldRole)
                
                await message.author.add_roles(message.guild.get_role(role))
                role = message.guild.get_role(role)
                
            if not messageToSend and not guild.message:
                return
                
            if not guild.mention:
                mention = ""
            
            if guild.channel_id != 0 and guild.channel_id is not None:
                channel = self.bot.get_channel(guild.channel_id)
                
            messageToSend = messageToSend.replace("\\n", "\n").format_map(safeDict(user_name=message.author.name, user_mention=message.author.mention, user_discriminator=message.author.discriminator, level=user.level, xp_needed=user.xp_needed, level_next=user.level + 1, role=role.mention if role is not None else ""))
                
            await infoEmbed(self.bot, channel, messageToSend, mention, color=message.author.color, thumbnail=message.author.display_avatar.url)
        
    @commands.command(name="level", aliases=["lvl", "rank", "xp", "r"])
    async def level(self, ctx, member: nextcord.Member = None):
        if not checkIfLevelSystemIsEnabled(ctx.guild):
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, getGuildLanguage(ctx.guild.id), "levelsysNotEnabled"))
        
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if member is None: member = ctx.author
        
        
        user: User = readUser(ctx.guild, member.id)
        allUsers = readAll("user_id", "level_users", "guild_id", ctx.guild.id, "xp DESC")
        
        top10 = False
        placing = 1
        
        for i, databaseUser in enumerate(allUsers):
            if databaseUser[0] == user.user_id:
                if i <= 10: top10 = True
                placing = i + 1
                break
        
        await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysUserLevel", member, user.level, user.xp, user.xp_needed, placing, len(allUsers), getLocale(languageStrings, guildLocale, "yes" if top10 else "no")), thumbnail=member.display_avatar.url, color=member.color)
    
    @commands.command(name="leaderboard", aliases=["lb", "top", "levels"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def leaderboard(self, ctx):
        if not checkIfLevelSystemIsEnabled(ctx.guild):
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, getGuildLanguage(ctx.guild.id), "levelsysNotEnabled"))
        
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        allUsers = readAll("user_id, level, xp", "level_users", "guild_id", ctx.guild.id, "xp DESC")
        
        if len(allUsers) == 0:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysNoUsers"))
        
        leaderboard = ""
        
        for i, databaseUser in enumerate(allUsers):
            if i >= 10: break
            
            user = self.bot.get_user(databaseUser[0])
            if user is None: user = await self.bot.fetch_user(databaseUser[0])
            
            leaderboard += f"> {i + 1}. {user.mention} - Level {databaseUser[1]} - {databaseUser[2]} XP\n"
        
        await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysLeaderboard", leaderboard))

    @commands.group(name="levelsystem", aliases=["levelsys", "leveling"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem(self, ctx, option: str = None, value: str = None):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if option is None or option.lower() in {"help", "h", "info", "i", "settings", "s"} or not ctx.author.guild_permissions.manage_guild:
            view = LevelSystemHelpView(self.bot, language=guildLocale)
            message = await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysHelp", getPrefixFromDatabase(self.bot, ctx.message)[0]), view=view)
            view.message = message
            cache.append(f"{message.id}|{ctx.author.id}")
            return
        
        guild: Guild = readGuild(ctx.guild)
        
        if not ctx.author.guild_permissions.manage_guild:
            raise commands.MissingPermissions(["manage_guild"])
        
        if option.lower() in {"enable", "e", "on"}:
            if guild.enabled:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysAlreadyEnabled"))
            
            guild.enabled = True
            update("level_system", "enabled", "guild_id", [1, ctx.guild.id])
            return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysEnabled"))
        
        if option.lower() in {"disable", "d", "off"}:
            if not guild.enabled:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysAlreadyDisabled"))
            
            guild.enabled = False
            update("level_system", "enabled", "guild_id", [0, ctx.guild.id])
            return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysDisabled"))
            
        if option.lower() in {"xp", "exp", "experience"}:
            if value is None or not value.isdigit():
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysXpValue"))
                
            if int(value) < 1:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysXpValue"))
            
            if int(value) > 12:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysXpValue"))
            
            if int(value) == guild.xp:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysXpAlready", value))
            
            guild.xp = int(value)
            update("level_system", "xp", "guild_id", [int(value), ctx.guild.id])
            return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysXpCustom", value))
        
        if option.lower() in {"cooldown", "cd"}:
            if value is None or not value.isdigit():
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCooldownValue"))
            
            if int(value) < 3:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCooldownValue"))
            
            if int(value) > 60:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCooldownValue"))
            
            if int(value) == guild.cooldown:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCooldownAlready", value))
            
            guild.cooldown = int(value)
            update("level_system", "cooldown", "guild_id", [int(value), ctx.guild.id])
            return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCooldownCustom", value))
        
        if option.lower() in {"mention", "ping"}:
            if value is None:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMentionValue"))
            
            if value.lower() in {"enable", "e", "on"}:
                if guild.mention:
                    return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMentionAlreadyEnabled"))
                
                guild.mention = True
                update("level_system", "mention", "guild_id", [1, ctx.guild.id])
                return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMentionEnabled"))
            
            if value.lower() in {"disable", "d", "off"}:
                if not guild.mention:
                    return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMentionAlreadyDisabled"))
                
                guild.mention = False
                update("level_system", "mention", "guild_id", [0, ctx.guild.id])
                return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMentionDisabled"))
            
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMentionValue"))
        
        if option.lower() in {"current", "show"}:
            yes = getLocale(languageStrings, guildLocale, "yes")
            no = getLocale(languageStrings, guildLocale, "no")
            none = getLocale(languageStrings, guildLocale, "none")
            enabled = yes if guild.enabled else no
            xp = str(guild.xp)
            cooldown = f"{str(guild.cooldown)} {getLocale(languageStrings, guildLocale, 'seconds')}"
            mention = yes if guild.mention else no
            channel = f"<#{guild.channel_id}>" if guild.channel_id is not None else none
            keysFromCustom_messages = ", ".join([f"Level `{key}`" for key in guild.custom_messages.keys()]) if guild.custom_messages else none
            roles = ", ".join([f"<@&{role}>" for role in guild.roles.values()]) if guild.roles else none
            blacklist_channel = ", ".join([f"<#{channel}>" for channel in guild.blacklist_channel]) if guild.blacklist_channel else none
            blacklist_roles = ", ".join([f"<@&{role}>" for role in guild.blacklist_roles]) if guild.blacklist_roles else none
            iconURL = ctx.guild.icon.url if ctx.guild.icon is not None else ""
            return await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCurrent", enabled, xp, cooldown, getPrefixFromDatabase(self.bot, ctx.message)[0], mention, channel, keysFromCustom_messages, roles, blacklist_channel, blacklist_roles), thumbnail=iconURL)
            
        view = LevelSystemHelpView(self.bot, language=guildLocale)
        message = await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysHelp", getPrefixFromDatabase(self.bot, ctx.message)[0]), view=view)
        view.message = message
        cache.append(f"{message.id}|{ctx.author.id}")
        return
        
    @levelsystem.command(name="message", aliases=["m"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_message(self, ctx, *, message: str = None):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if message is None:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageValue"))
        
        if message.lower() in {"current", "show"}:
            if guild.message == "none":
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageNone"))
            
            user: User = readUser(ctx.guild, ctx.author.id)
            
            return await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageCurrent", guild.message.replace("\\n", "\n").format_map(safeDict(user_name=ctx.message.author.name, user_mention=ctx.message.author.mention, user_discriminator=ctx.message.author.discriminator, level=user.level, xp_needed=user.xp_needed, level_next=user.level + 1, role="{role}"))))
        
        if message.lower() in {"none", "off"}:
            guild.message = "none"
            update("level_system", "message", "guild_id", ["none", ctx.guild.id])
            return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageNone"))
        
        if message.lower() in {"default", "standard"}:
            guild.message = "default"
            update("level_system", "message", "guild_id", ["default", ctx.guild.id])
            return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageDefault", getLocale(languageStrings, guildLocale, "levelsysDefaultMessage")))
        
        if len(message) > 1000:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageTooLong"))
        
        guild.message = message
        update("level_system", "message", "guild_id", [message, ctx.guild.id])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageCustom"))
    
    @levelsystem.command(name="channel", aliases=["c"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_channel(self, ctx, channel: nextcord.TextChannel = None):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if channel is None:
            guild.channel_id = None
            update("level_system", "channel_id", "guild_id", ["null", ctx.guild.id])
            return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysChannelNone"))
        
        guild.channel_id = channel.id
        update("level_system", "channel_id", "guild_id", [channel.id, ctx.guild.id])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysChannel", channel.mention))
    
    @levelsystem.group(name="custom", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_custom(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_custom.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_custom_add(self, ctx, level: int, *, message: str):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if level < 2:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomAddLevel"))
        
        if len(message) > 1000:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysMessageTooLong"))
        
        if guild.custom_messages is None:
            guild.custom_messages = {}
        
        if level in guild.custom_messages:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomAddAlready", level))
        
        guild.custom_messages[level] = message
        insert("level_custommessages", "guild_id, level, message", [ctx.guild.id, level, message])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomAdded", level, message))
    
    @levelsystem_custom.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_custom_remove(self, ctx, level: int):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if guild.custom_messages is None:
            guild.custom_messages = {}
        
        if level not in guild.custom_messages:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomRemoveLevel", level))
        
        del guild.custom_messages[level]
        delete("level_custommessages", "guild_id level", [ctx.guild.id, level])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomRemoved", level))
    
    @levelsystem_custom.command(name="show", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_custom_show(self, ctx, level):
        if level.lower() in {"all", "a"}:
            guildLocale = getGuildLanguage(ctx.guild.id)
            
            guild: Guild = readGuild(ctx.guild)
            
            if guild.custom_messages is None:
                guild.custom_messages = {}
            
            if len(guild.custom_messages) == 0:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomShowNone"))
            
            custom_messages = ""
            
            for level in guild.custom_messages.keys():
                custom_messages += f"> **{level}**\n"
            
            return await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomShowAll", custom_messages))
        
        custom_message = readOne("message", "level_custommessages", "guild_id level", [ctx.guild.id, level])
        
        if custom_message is None:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomShowLevel", level))
        
        return await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysCustomShow", level, custom_message[0]))
        
    @levelsystem.group(name="roles", aliases=["r", "role"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_roles(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_roles.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_roles_add(self, ctx, level: int, *, role: nextcord.Role):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if level < 2:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesAddLevel"))
        
        if guild.roles is None:
            guild.roles = {}
        
        if level in guild.roles:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesAddAlready", level))
        
        guild.roles[level] = role.id
        insert("level_roles", "guild_id, level, role_id", [ctx.guild.id, level, role.id])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesAdd", level, role.mention))
    
    @levelsystem_roles.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_roles_remove(self, ctx, level: int):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if guild.roles is None:
            guild.roles = {}
        
        if level not in guild.roles:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesRemoveLevel", level))
        
        del guild.roles[level]
        delete("level_roles", "guild_id level", [ctx.guild.id, level])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesRemoved", level))
    
    @levelsystem_roles.command(name="show", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_roles_show(self, ctx, level):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if guild.roles is None:
            guild.roles = {}
        
        if level.lower() in {"all", "a"}:
            if len(guild.roles) == 0:
                return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesShowNone"))
            
            roles = ""
            
            for level in guild.roles.keys():
                roles += f"> **{level}**\n"
            
            return await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesShowAll", roles))
        
        if level not in guild.roles:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesShowLevel", level))
        
        return await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysRolesShow", level, ctx.guild.get_role(guild.roles[level]).mention))
    
    @levelsystem.group(name="blacklist", aliases=["b"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_blacklist.group(name="channel", aliases=["c"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist_channel(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_blacklist_channel.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist_channel_add(self, ctx, channel: nextcord.TextChannel):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if guild.blacklist_channel is None:
            guild.blacklist_channel = []
        
        if channel.id in guild.blacklist_channel:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistAddChannelAlready", channel.mention))
        
        guild.blacklist_channel.append(channel.id)
        insert("level_blacklist_channel", "guild_id, channel_id", [ctx.guild.id, channel.id])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistAdd", channel.mention))
    
    @levelsystem_blacklist_channel.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist_channel_remove(self, ctx, channel: nextcord.TextChannel):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if guild.blacklist_channel is None:
            guild.blacklist_channel = []
        
        if channel.id not in guild.blacklist_channel:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistRemoveChannel"))
        
        guild.blacklist_channel.remove(channel.id)
        delete("level_blacklist_channel", "guild_id channel_id", [ctx.guild.id, channel.id])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistRemove", channel.mention))
    
    @levelsystem_blacklist.group(name="role", aliases=["r"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist_role(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_blacklist_role.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist_role_add(self, ctx, role: nextcord.Role):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if guild.blacklist_roles is None:
            guild.blacklist_roles = []
        
        if role.id in guild.blacklist_roles:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistAddRoleAlready"))
        
        guild.blacklist_roles.append(role.id)
        insert("level_blacklist_roles", "guild_id, role_id", [ctx.guild.id, role.id])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistAdd", role.mention))
    
    @levelsystem_blacklist_role.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist_role_remove(self, ctx, role: nextcord.Role):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        guild: Guild = readGuild(ctx.guild)
        
        if guild.blacklist_roles is None:
            guild.blacklist_roles = []
        
        if role.id not in guild.blacklist_roles:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistRemoveRole"))
        
        guild.blacklist_roles.remove(role.id)
        delete("level_blacklist_roles", "guild_id role_id", [ctx.guild.id, role.id])
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistRemove", role.mention))
    
    @levelsystem_blacklist.command(name="show", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_blacklist_show(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)

        guild: Guild = readGuild(ctx.guild)

        if guild.blacklist_channel is None:
            guild.blacklist_channel = []

        if guild.blacklist_roles is None:
            guild.blacklist_roles = []
            
        channelFieldDescription = ""
        
        for channel in guild.blacklist_channel:
            channel = ctx.guild.get_channel(channel)
            
            if channel is None: continue
            
            channelFieldDescription += f"{channel.mention},"
            
        roleFieldDescription = ""
        
        for role in guild.blacklist_roles:
            role = ctx.guild.get_role(role)
            
            if role is None: continue
            
            roleFieldDescription += f"{role.mention},"
        
        if not channelFieldDescription:
            channelFieldDescription = getLocale(languageStrings, guildLocale, "levelsysBlacklistShowChannelNone")

        if not roleFieldDescription:
            roleFieldDescription = getLocale(languageStrings, guildLocale, "levelsysBlacklistShowRoleNone")

        channelField = EmbedField(getLocale(languageStrings, guildLocale, "levelsysBlacklistShowChannel"), channelFieldDescription, True)
        roleField = EmbedField(getLocale(languageStrings, guildLocale, "levelsysBlacklistShowRoles"), roleFieldDescription, True)

        return await infoEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysBlacklistShowAll"), fields=[channelField, roleField])
    
    @levelsystem.group(name="modify", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_modify.group(name="xp", aliases=["x", "exp"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_xp(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_modify_xp.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_xp_add(self, ctx, user: nextcord.Member, amount: int):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if amount < 1:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyXpAddAmount"))
        
        user: User = readUser(ctx.guild, user.id)
        
        user.xp += amount
        
        if amount >= math.ceil(10 * ((1000) ** 1.5) + 20):
            user.xp = math.ceil(10 * ((1000) ** 1.5) + 20)
            
        while user.xp_needed < user.xp and user.level < 1000:
            user.level += 1
            user.xp_needed = math.ceil(10 * ((user.level) ** 1.5) + 20)
            
        
        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, user.user_id])
        
        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyXpAdd", user.user_id, amount))
    
    @levelsystem_modify_xp.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_xp_remove(self, ctx, user: nextcord.Member, amount: int):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if amount < 1:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyXpRemoveAmount"))

        user: User = readUser(ctx.guild, user.id)

        user.xp -= amount

        user.xp = max(user.xp, 0) # Prevents negative xp values (max function returns the highest value)
        user.level = 1
        user.xp_needed = 27

        while user.xp_needed < user.xp:
            user.level += 1
            user.xp_needed = math.ceil(10 * ((user.level) ** 1.5) + 20)

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, user.user_id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyXpRemove", user.user_id, amount))
    
    @levelsystem_modify_xp.command(name="set", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_xp_set(self, ctx, user: nextcord.Member, amount: int):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if amount < 1:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyXpSetAmount"))
        
        if amount > math.ceil(10 * ((1000) ** 1.5) + 20):
            amount = math.ceil(10 * ((1000) ** 1.5) + 20)

        user: User = readUser(ctx.guild, user.id)

        user.xp = amount
        user.level = 1
        user.xp_needed = 27

        while user.xp_needed < user.xp and user.level < 1000:
            user.level += 1
            user.xp_needed = math.ceil(10 * ((user.level) ** 1.5) + 20)

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, user.user_id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyXpSet", user.user_id, amount))
    
    @levelsystem_modify.group(name="level", aliases=["l"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_level(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_modify_level.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_level_add(self, ctx, user: nextcord.Member, amount: int):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if amount < 1:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyLevelAddAmount"))

        user: User = readUser(ctx.guild, user.id)

        user.level += amount

        user.level = min(user.level, 1000)
        user.xp_needed = math.ceil(10 * ((user.level - 1) ** 1.5) + 20)

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp_needed, ctx.guild.id, user.user_id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyLevelAdd", user.user_id, amount))
    
    @levelsystem_modify_level.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_level_remove(self, ctx, user: nextcord.Member, amount: int):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if amount < 1:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyLevelRemoveAmount"))

        user: User = readUser(ctx.guild, user.id)

        user.level -= amount

        user.level = max(user.level, 1)
        user.xp_needed = math.ceil(10 * ((user.level - 1) ** 1.5) + 20)

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp_needed, ctx.guild.id, user.user_id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyLevelRemove", user.user_id, amount))
    
    @levelsystem_modify_level.command(name="set", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_modify_level_set(self, ctx, user: nextcord.Member, amount: int):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if amount < 1:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyLevelSetAmount"))

        user: User = readUser(ctx.guild, user.id)

        user.level = amount
        user.xp_needed = math.ceil(10 * ((user.level - 1) ** 1.5) + 20)

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp_needed, ctx.guild.id, user.user_id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysModifyLevelSet", user.user_id, amount))
        
        
    @levelsystem.group(name="reset", aliases=["re"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_reset(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @levelsystem_reset.command(name="user", aliases=["u"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_reset_user(self, ctx, user: nextcord.Member):
        guildLocale = getGuildLanguage(ctx.guild.id)

        user: User = readUser(ctx.guild, user.id)

        user.xp = 0
        user.level = 1
        user.xp_needed = 27

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, user.user_id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysResetUser", user.user_id))
    
    @levelsystem_reset.command(name="all", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_reset_all(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)

        update("level_users", "level xp", "guild_id", [1, 0, ctx.guild.id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysResetAll"))
    
    @levelsystem_reset.command(name="settings", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def levelsystem_reset_settings(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)

        update("level_system", "xp cooldown mention message channel_id", "guild_id", [3, 6, 1, getLocale(languageStrings, guildLocale, "levelsysDefaultMessage"), "null", ctx.guild.id])

        return await successEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "levelsysResetSettings"))
        
def checkIfLevelSystemIsEnabled(guild: nextcord.Guild) -> bool:
    """Checks if the level system is enabled in the guild and returns True if it is enabled."""
    enabled = readOne("enabled", "level_system", "guild_id", [guild.id])

    return False if enabled is None else enabled[0] == 1

def readUser(guild: nextcord.Guild, userID: int) -> User:
    """Reads the user from the database and returns a User object."""
    databaseUser = readOne("messages, level, xp, cooldown", "level_users", "guild_id user_id", [guild.id, userID])
    
    if databaseUser is None:
        insert("level_users", "guild_id, user_id, messages, level, xp, cooldown", [guild.id, userID, 0, 1, 0, time()])
        return User(userID, 0, 1, 0, time(), 27)
    
    xpNeeded = 27 if databaseUser[1] == 1 else math.ceil(10 * (databaseUser[1] ** 1.5) + 20)
    
    return User(userID, databaseUser[0], databaseUser[1], databaseUser[2], databaseUser[3], xpNeeded)

def readGuild(guild: nextcord.Guild) -> Guild:
    """Reads the guild from the database and returns a Guild object."""
    databaseGuild = readOne("enabled, xp, cooldown, mention, message, channel_id", "level_system", "guild_id", [guild.id])
    databaseCustomMessages = readAll("level, message", "level_custommessages", "guild_id", [guild.id])
    databaseLevelRoles = readAll("level, role_id", "level_roles", "guild_id", [guild.id])
    databaseBlacklistedChannels = readAll("channel_id", "level_blacklist_channel", "guild_id", [guild.id])
    databaseBlacklistedRoles = readAll("role_id", "level_blacklist_roles", "guild_id", [guild.id])
    
    databaseBlacklistedChannels = [channel[0] for channel in databaseBlacklistedChannels]
    databaseBlacklistedRoles = [role[0] for role in databaseBlacklistedRoles]
    
    customMessages = {}
    levelRoles = {}
    
    if databaseCustomMessages is not None:
        for message in databaseCustomMessages:
            customMessages[message[0]] = message[1]
            
    if databaseLevelRoles is not None:
        for role in databaseLevelRoles:
            levelRoles[role[0]] = role[1]
    
    if databaseGuild is None:
        insert("level_system", "guild_id, enabled, xp, cooldown, mention, message, channel_id", [guild.id, 0, 3, 6, 1, getLocale(languageStrings, getGuildLanguage(guild.id), "levelsysDefaultMessage"), "null"])
        return Guild(guild.id, False, 3, 6, True, getLocale(languageStrings, getGuildLanguage(guild), "levelsysDefaultMessage"), None, {}, {}, [], [])
    
    if databaseBlacklistedChannels is None:
        databaseBlacklistedChannels = []
    
    if databaseBlacklistedRoles is None:
        databaseBlacklistedRoles = []
    
    return Guild(guild.id, databaseGuild[0] == 1, databaseGuild[1], databaseGuild[2], databaseGuild[3] == 1, databaseGuild[4], databaseGuild[5], customMessages, levelRoles, databaseBlacklistedChannels, databaseBlacklistedRoles)

def addUserXP(guild: Guild, user: User) -> bool:
    """Adds the xp to the user and returns True if the user leveled up."""
    if time() - user.cooldown < guild.cooldown: return
    if user.level == 1000: return
    
    user.xp += guild.xp
    user.messages += 1
    user.cooldown = time()
    
    if user.xp >= user.xp_needed:
        user.level += 1
        user.xp_needed = 27 if user.level == 1 else math.ceil(10 * (user.level ** 1.5) + 20)
        
        update("level_users", "messages level xp cooldown", "guild_id user_id", [user.messages, user.level, user.xp, user.cooldown, guild.guild_id, user.user_id])
        return True
    
    update("level_users", "messages xp cooldown", "guild_id user_id", [user.messages, user.xp, user.cooldown, guild.guild_id, user.user_id])
    return False

class LevelSystemHelpView(nextcord.ui.View):
    def __init__(self, bot, language: str, disabled: bool = False, category: str = "general"):
        super().__init__(timeout=300)
        self.add_item(SelectorButton(bot, disabled, category, language=language))
        self.bot = bot
        self.disabled = disabled
        
    async def on_timeout(self) -> None:
        if self.disabled:
            return
            
        await self.calltimeout(self.bot, self.message)
        
    async def calltimeout(self, bot, message):
        guildLocale = getGuildLanguage(message.guild.id)

        view = LevelSystemHelpView(bot, guildLocale, True)
        embed = nextcord.Embed(
                description=getLocale(languageStrings, guildLocale, "levelsysHelp", getPrefixFromDatabase(self.bot, message)[0]),
                color=nextcord.Color.blurple()
        )
        message = await message.edit(embed=embed, view=view)
        view.message = message
        
class SelectorButton(nextcord.ui.Select):
    def __init__(self, bot, disabled: bool, category: str = "general", language: str = "en"):
        general = getLocale(languageStrings, language, "general")
        message = getLocale(languageStrings, language, "message")
        roles = getLocale(languageStrings, language, "roles")
        blacklist = getLocale(languageStrings, language, "blacklist")
        reset = getLocale(languageStrings, language, "reset")

        options = [
            nextcord.SelectOption(label=general, emoji="<:Commands:1087442278118871140>", default=category == "general"),
            nextcord.SelectOption(label=message, emoji="<a:Typing:1097514996562395278>", default=category == "message"),
            nextcord.SelectOption(label=roles, emoji="<:autoroles:1090725070323859506>", default=category == "roles"),
            nextcord.SelectOption(label=blacklist, emoji="<:Cross:1097515321365110835>", default=category == "blacklist"),
            nextcord.SelectOption(label=reset, emoji="<:Error:1087445963280486430>", default=category == "reset")
        ]

        super().__init__(placeholder=getLocale(languageStrings, language, "categoriesPlaceholder"), options=options, disabled=disabled)
        self.bot = bot

    async def callback(self, interaction):
        global languageStrings
        if f"{interaction.message.id}|{interaction.user.id}" not in cache:
            return
        

        guildLocale = getGuildLanguage(interaction.guild.id)

        category = self.values[0].lower()
        if category == getLocale(languageStrings, guildLocale, "general").lower():
            category = "general"
        elif category == getLocale(languageStrings, guildLocale, "message").lower():
            category = "message"
        elif category == getLocale(languageStrings, guildLocale, "roles").lower():
            category = "roles"
        elif category == getLocale(languageStrings, guildLocale, "blacklist").lower():
            category = "blacklist"
        elif category == getLocale(languageStrings, guildLocale, "reset").lower():
            category = "reset"

        view = LevelSystemHelpView(self.bot, guildLocale, False, category)
        prefix = getPrefixFromDatabase(self.bot, interaction.message)[0]

        with contextlib.suppress(Exception):
            match category:
                case "general":
                    embed = nextcord.Embed(
                        description=getLocale(languageStrings, guildLocale, "levelsysHelp", prefix),
                        color=nextcord.Color.blurple()
                        )

                case "message":
                    embed = nextcord.Embed(
                        description=getLocale(languageStrings, guildLocale, "messageDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "roles":
                    embed = nextcord.Embed(
                        description=getLocale(languageStrings, guildLocale, "rolesDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "blacklist":
                    embed = nextcord.Embed(
                        description=getLocale(languageStrings, guildLocale, "blacklistDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "reset":
                    embed = nextcord.Embed(
                        description=getLocale(languageStrings, guildLocale, "resetDescription", prefix),
                        color=nextcord.Color.blurple()
                    )
            
            message = await interaction.message.edit(embed=embed, view=view)
            view.message = message

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("levelsys")
    bot.add_cog(LevelSystem(bot))
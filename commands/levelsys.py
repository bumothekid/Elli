import math
from time import time
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.database import readOne, readAll, update, insert, delete
from .utils.other import getPrefixFromDatabase, safeDict
from .utils.models.LevelingUser import LevelingUser as User
from .utils.models.EmbedField import EmbedField

class levelsys(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name="level", aliases=["levelsystem", "levelsys", "r", "rank"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _level(self, ctx, member: nextcord.Member = None):
        if ctx.invoked_subcommand is not None:
            return
            
        if member is None:
            member = ctx.author

        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if member is None:
            member = ctx.author

        user: User = readUser(ctx.guild.id, member.id)

        level = user.level
        xp = user.xp
        xpNeeded = user.xp_needed

        allUsers = readAll("user_id", "level_users", "guild_id", [ctx.guild.id], "xp DESC")

        top10 = False
        placing = 1
        if allUsers:
            for user in allUsers:
                if user[0] == member.id:
                    top10 = True
                    break
                placing += 1

        await infoEmbed(self.bot, ctx, f"**Level - {member}**\n\n> **Level:** {level}\n> **XP:** {xp}/{xpNeeded}\n> **Platz:** {placing}/10\n> **Top 10:** {'Ja' if top10 else 'Nein'}", thumbnail=member.display_avatar.url, color=member.color)
    
    @commands.command(name="leaderboard", aliases=["lb", "top", "top10"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _leaderboard(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist deaktiviert.")

        if allUsers := readAll("user_id", "level_users", "guild_id", [ctx.guild.id], "xp DESC"):
            fields = []

            for user in allUsers:
                member = ctx.guild.get_member(user[0])
                user = readUser(ctx.guild.id, user[0])

                if member is None or user is None:
                    continue

                fields.append(EmbedField(member.mention, f"Level: {user.level}\nXP: {user.xp}", False))
            
            await successEmbed(self.bot, ctx, "**Level Leaderboard**\n\n", fields=fields)
        else:
            await errorEmbed(self.bot, ctx, "Es sind keine noch User in der Datenbank gespeichert.")
    
    @_level.command(name="settings", aliases=["options"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _settings(self, ctx):
        await infoEmbed(self.bot, ctx, "** Level System**\n\n"
                                        "> `-level <@user>`\n"
                                        "> `-leaderboard`\n\n"
                                        "> `-level settings`\n"
                                        "> `-level <on | off>`\n"
                                        "> `-level xp <anzahl>`\n"
                                        "> `-level cooldown <sekunden>`\n\n"
                                        "> `-level message <text>`\n"
                                        "> `-level message`\n"
                                        "> `-level ping <on | off>`\n\n"
                                        "> `-level custom add <level> <text>`\n"
                                        "> `-level custom remove <level>`\n"
                                        "> `-level custom show <level>`\n"
                                        "> `-level custom show`\n\n"
                                        "> `-level roles add <level> <@rolle>`\n"
                                        "> `-level roles remove <level>`\n"
                                        "> `-level roles joinrole add <@rolle>`\n"
                                        "> `-level roles joinrole remove`\n"
                                        "> `-level roles`\n\n"
                                        "> `-level blacklist add <@rolle | #channel>`\n"
                                        "> `-level blacklist remove <@rolle | #channel>`\n"
                                        "> `-level blacklist`\n\n"
                                        "> `-level modifylevel add <level> <@user>`\n"
                                        "> `-level modifylevel remove <level> <@user>`\n"
                                        "> `-level modifyxp add <xp> <@user>`\n"
                                        "> `-level modifyxp remove <xp> <@user>`\n\n"
                                        "> `-level reset <@user>`\n"
                                        "> `-level reset level`\n"
                                        "> `-level reset settings`\n"
                                        "> `-level reset all`\n\n"
                                        "> Variablen für die Level Up Nachricht:\n"
                                        "> `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{level}`, `{xp_needed}`, `{level_next}` und `{role}` für custom Nachrichten\n\n"
                                        "> Du kannst eine Level Up Nachricht mit mehreren erstellen mit `\\n`\n"
                                        "> Um die Level Up Nachricht zu entfernen füge `off` als Nachricht ein."
        )
    
    @_level.command(name="on", aliases=["enable", "e"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _on(self, ctx):
        if checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist bereits aktiviert.")

        update("level_system", "enabled", "guild_id", [1, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Das Level System wurde aktiviert.")
    
    @_level.command(name="off", aliases=["disable", "d"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _off(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist bereits deaktiviert.")

        update("level_system", "enabled", "guild_id", [0, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Das Level System wurde deaktiviert.")

    @_level.command(name="xp", aliases=["exp", "expirience"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _xp(self, ctx, amount: int):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if not isinstance(amount, int):
            return await errorEmbed(self.bot, ctx, "Die anzahl an XP pro Nachricht muss eine ganze Zahl sein.")

        if amount < 1:
            return await errorEmbed(self.bot, ctx, "Die Anzahl der XP pro Nachricht muss größer als `0` sein.")
        
        if amount > 15:
            return await errorEmbed(self.bot, ctx, "Die Anzahl der XP pro Nachricht darf nicht größer als `15` sein.")

        update("level_system", "xp", "guild_id", [amount, ctx.guild.id])
        await successEmbed(self.bot, ctx, f"Die Anzahl der XP pro Nachricht wurde auf `{amount}` gesetzt.")

    @_level.command(name="cooldown", aliases=["cd", "c"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _cooldown(self, ctx, seconds: int):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if not isinstance(seconds, int):
            return await errorEmbed(self.bot, ctx, "Die Cooldown Zeit muss eine ganze Zahl sein.")

        if seconds <= 3:
            return await errorEmbed(self.bot, ctx, "Die Cooldown Zeit muss länger als `3` Sekunden sein.")

        if seconds > 500:
            return await errorEmbed(self.bot, ctx, "Die Cooldown Zeit darf nicht länger als `500` Sekunden sein.")

        update("level_system", "cooldown", "guild_id", [seconds, ctx.guild.id])
        await successEmbed(self.bot, ctx, f"Die Cooldown Zeit wurde auf `{seconds}` Sekunden gesetzt.")

    @_level.command(name="message", aliases=["msg", "m"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _message(self, ctx, *, text: str = None):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")
        
        if text is None:
            message = readOne("level_system", "message", "guild_id", [ctx.guild.id])

            if message is None:
                return await errorEmbed(self.bot, ctx, "Es wurde keine Level Up Nachricht gesetzt.")

            return await successEmbed(self.bot, ctx, f"Die aktuelle Nachricht ist:\n\n{message[0]}")

        if text == "off":
            update("level_system", "message", "guild_id", ["null", ctx.guild.id])
            return await successEmbed(self.bot, ctx, "Die Level Up Nachricht wurde entfernt.")

        text = text.replace("\n", "\\n")
        update("level_system", "message", "guild_id", [text, ctx.guild.id])
        await successEmbed(self.bot, ctx, f"Die Level Up Nachricht wurde auf `{text}` gesetzt.")

    @_level.group(name="ping", aliases=["p"], invoke_without_command=True)
    async def _ping(self, ctx):
        await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")

    @_ping.command(name="on", aliases=["enable", "e"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _on2(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        update("level_system", "ping", "guild_id", [1, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Die Ping Nachricht wurde aktiviert.")
    
    @_ping.command(name="off", aliases=["disable", "d"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _off2(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        update("level_system", "ping", "guild_id", [0, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Die Ping Nachricht wurde deaktiviert.")

    @_level.group(name="custom", invoke_without_command=True)
    async def _custom(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if ctx.invoked_subcommand is None:
            await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")
        
    @_custom.command(name="add", aliases=["a", "set"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set2(self, ctx, level: int, *, text: str):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if not isinstance(level, int):
            return await errorEmbed(self.bot, ctx, "Du musst ein Level angeben wofür die Nachricht sein soll.")

        if level <= 1:
            return await errorEmbed(self.bot, ctx, "Das Level muss größer als `1` sein.")

        message = readOne("message", "level_custommessages", "guild_id level", [ctx.guild.id, level])

        if message is not None:
            return await errorEmbed(self.bot, ctx, f"Level `{level}` hat bereits eine eigene Nachricht.")

        text = text.replace("\n", "\\n")
        insert("level_custommessages", "guild_id level text", [ctx.guild.id, level, text])
        await successEmbed(self.bot, ctx, f"Die Rank Up Nachricht wurde auf `{text}` gesetzt.")
    
    @_custom.command(name="remove", aliases=["r", "del", "delete"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove2(self, ctx, level: int):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if not isinstance(level, int):
            return await errorEmbed(self.bot, ctx, "Du musst ein Level angeben welche gelöscht werden soll.")

        if level <= 1:
            return await errorEmbed(self.bot, ctx, "Das Level muss größer als `1` sein.")

        message = readOne("message", "level_custommessages", "guild_id level", [ctx.guild.id, level])

        if message is None:
            return await errorEmbed(self.bot, ctx, f"Level `{level}` hat keine eigene Nachricht.")

        delete("level_custommessages", "guild_id level", [ctx.guild.id, level])
        await successEmbed(self.bot, ctx, f"Die eigene Nachricht für Level `{level}` wurde entfernt.")

    @_custom.command(name="show", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _show2(self, ctx, level: int = None):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if level is not None:
            if not isinstance(level, int):
                return await errorEmbed(self.bot, ctx, "Du musst ein Level angeben welche gelöscht werden soll.")

            if level <= 1:
                return await errorEmbed(self.bot, ctx, "Das Level muss größer als `1` sein.")

            message = readOne("message", "level_custommessages", "guild_id level", [ctx.guild.id, level])

            if message is None:
                return await errorEmbed(self.bot, ctx, f"Level `{level}` hat keine eigene Nachricht.")

            mention = readOne("mention", "level_system", "guild_id", [ctx.guild.id])
            user: User = readUser(ctx.guild.id, ctx.author.id)
            role_id = readOne("role_id", "level_roles", "guild_id level", [ctx.guild.id, level])

            role = ctx.guild.get_role(role_id) if role_id is not None else None
            return await infoEmbed(self.bot, ctx, message[0].replace("\\n", "\n").format_map(safeDict(user_name=ctx.author.name, user_mention=ctx.author.mention, user_discriminator=ctx.author.discriminator, level=user.level, xp_needed=user.xp_needed, level_next=user.level + 1, role=role)), content=f"{ctx.author.mention}" if mention[0] else None)

        messages = readAll("message", "level_custommessages", "guild_id", [ctx.guild.id])

        if not messages:
            return await errorEmbed(self.bot, ctx, "Es wurden keine eigenen Nachrichten gesetzt.")

        message = "".join(f"`{level[0]}`\n" for level in messages)

        await successEmbed(self.bot, ctx, f"**Eigenen Nachrichten:**\n\n{message}")
    
    @_level.group(name="roles", aliases=["r"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _roles(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        roles = readAll("role_id, level", "level_roles", "guild_id", [ctx.guild.id])

        if not roles:
            return await errorEmbed(self.bot, ctx, "Es gibt noch keine Ränge.")

        lb = ""

        for role in roles:
            if role[1] == 1:
                continue

            role_mention = f"{ctx.guild.get_role(role[0]).mention}"
            lb += f"Level `{role[1]}` | {role_mention}\n"

        await infoEmbed(self.bot, ctx, f"**Alle Ränge**\n\n{lb}")

    @_roles.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _add(self, ctx, level: int, role: nextcord.Role):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if not isinstance(level, int):
            return await errorEmbed(self.bot, ctx, "Du musst ein Level für diesen Rang angeben.")

        if level <= 1:
            return await errorEmbed(self.bot, ctx, "Du kannst eine joinrole mit `-level roles joinrole` festlegen.") # Das Level muss größer als `1` sein.

        if not isinstance(role, nextcord.Role):
            return await errorEmbed(self.bot, ctx, "Du musst einen Rang angeben.")

        if readOne("role_id", "level_roles", "guild_id level", [ctx.guild.id, level]) is not None:
            return await errorEmbed(self.bot, ctx, "Es gibt bereits einen Rang für dieses Level.")

        if readOne("role_id", "level_roles", "guild_id role_id", [ctx.guild.id, role.id]) is not None:
            return await errorEmbed(self.bot, ctx, f"Dieser Rang ist bereits für das Level `{(readOne('level', 'level_roles', 'guild_id role_id', [ctx.guild.id, role.id]))[0]}` gesetzt.")

        insert("level_roles", "guild_id, role_id, level", [ctx.guild.id, role.id, level])
        await successEmbed(self.bot, ctx, f"Der Rang {role.mention} wurde für Level `{level}` eingetragen.")

    @_roles.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove(self, ctx, level: int):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if not isinstance(level, int):
            return await errorEmbed(self.bot, ctx, "Du musst eine ganze Zahl als Level angeben.")
        
        if level <= 1:
            return await errorEmbed(self.bot, ctx, "# Das Level muss größer als `1` sein.")

        if readOne("role_id", "level_roles", "guild_id level", [ctx.guild.id, level]) is None:
            return await errorEmbed(self.bot, ctx, "Es gibt noch keinen Rang für diese Level.")

        delete("level_roles", "guild_id level", [ctx.guild.id, level])
        await successEmbed(self.bot, ctx, f"Der Rang für das Level `{level}` wurde entfernt.")

    @_roles.group(name="joinrole", aliases=["jr"], invoke_without_command=True)
    async def _joinrole(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if ctx.invoked_subcommand is None:
            await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")

    @_joinrole.command(name="set", aliases=["s", "add"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set9(self, ctx, role: nextcord.Role):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        role_id = readOne("role_id", "level_roles", "guild_id level", [ctx.guild.id, 1])

        if role_id is not None:
            return await errorEmbed(self.bot, ctx, "Es wurde bereits eine joinrole festgelegt.")

        insert("level_roles", "guild_id, role_id, level", [ctx.guild.id, role.id, 1])
        await successEmbed(self.bot, ctx, f"Die joinrole wurde auf {role.mention} gesetzt.")

    @_joinrole.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove9(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        role_id = readOne("role_id", "level_roles", "guild_id level", [ctx.guild.id, 1])

        if role_id is None:
            return await errorEmbed(self.bot, ctx, "Es gibt noch keine joinrole.")

        delete("level_roles", "guild_id level", [ctx.guild.id, 1])
        await successEmbed(self.bot, ctx, "Die joinrole wurde entfernt.")

    @_level.group(name="blacklist", aliases=["b"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _blacklist(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        blacklistChannel = readAll("channel_id", "level_blacklist_channel", "guild_id", [ctx.guild.id])
        blacklistRoles = readAll("role_id", "level_blacklist_roles", "guild_id", [ctx.guild.id])


        if not blacklistChannel and not blacklistRoles:
            return await errorEmbed(self.bot, ctx, "Es gibt noch keine Blacklist.")


        channel = ""
        if blacklistChannel:
            for channel_id in blacklistChannel:
                channel += f"{ctx.guild.get_channel(channel_id[0]).mention}\n"

        role = ""
        if blacklistRoles:
            for role_id in blacklistRoles:
                role += f"{ctx.guild.get_role(role_id[0]).mention}\n"
    

        channelField = EmbedField("Kanäle", channel if channel != "" else "Keine Kanäle auf der Blacklist", inline=True)
        roleField = EmbedField("Rollen", role if role != "" else "Keine Rollen auf der Blacklist", inline=True)

        await infoEmbed(self.bot, ctx, "**Blacklist**", fields=[channelField, roleField])

    @_blacklist.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _add2(self, ctx, id: nextcord.TextChannel | nextcord.Role):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if isinstance(id, nextcord.TextChannel):
            if readOne("channel_id", "level_blacklist_channel", "guild_id channel_id", [ctx.guild.id, id.id]) is not None:
                return await errorEmbed(self.bot, ctx, "Dieser Kanal ist bereits in der Blacklist.")

            insert("level_blacklist_channel", "guild_id, channel_id", [ctx.guild.id, id.id])
            await successEmbed(self.bot, ctx, f"Der Kanal {id.mention} wurde zur Blacklist hinzugefügt.")
        
        elif isinstance(id, nextcord.Role):
            if readOne("role_id", "level_blacklist_roles", "guild_id role_id", [ctx.guild.id, id.id]) is not None:
                return await errorEmbed(self.bot, ctx, "Diese Rolle ist bereits in der Blacklist.")

            insert("level_blacklist_roles", "guild_id, role_id", [ctx.guild.id, id.id])
            await successEmbed(self.bot, ctx, f"Die Rolle {id.mention} wurde zur Blacklist hinzugefügt.")

    @_blacklist.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove2(self, ctx, id: nextcord.TextChannel | nextcord.Role):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        if isinstance(id, nextcord.TextChannel):
            if readOne("channel_id", "level_blacklist_channel", "guild_id channel_id", [ctx.guild.id, id.id]) is None:
                return await errorEmbed(self.bot, ctx, "Dieser Kanal ist nicht in der Blacklist.")

            delete("level_blacklist_channel", "guild_id channel_id", [ctx.guild.id, id.id])
            await successEmbed(self.bot, ctx, f"Der Kanal {id.mention} wurde aus der Blacklist entfernt.")

        elif isinstance(id, nextcord.Role):
            if readOne("role_id", "level_blacklist_roles", "guild_id role_id", [ctx.guild.id, id.id]) is None:
                return await errorEmbed(self.bot, ctx, "Diese Rolle ist nicht in der Blacklist.")

            delete("level_blacklist_roles", "guild_id role_id", [ctx.guild.id, id.id])
            await successEmbed(self.bot, ctx, f"Die Rolle {id.mention} wurde aus der Blacklist entfernt.")

    @_level.group(name="modifylevel", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _level2(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")
    
    @_level2.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _add3(self, ctx, level: int, member: nextcord.Member):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        user = readUser(ctx.guild.id, member.id)

        user.level += level
        user.xp = (math.floor(5 * (math.pow((user.level - 1), 2)) + 50 * (user.level - 1) + 100))

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, member.id])

        await successEmbed(self.bot, ctx, f"{member.mention} ist nun Level {user.level} und hat {user.xp} XP.")
    
    @_level2.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove3(self, ctx, level: int, member: nextcord.Member):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        user = readUser(ctx.guild.id, member.id)

        user.level -= level
        user.xp = (math.floor(5 * (math.pow((user.level - 1), 2)) + 50 * (user.level - 1) + 100))

        update("level_users", "level xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, member.id])

        await successEmbed(self.bot, ctx, f"{member.mention} ist nun Level {user.level} und hat {user.xp} XP.")

    @_level.group(name="modifyxp", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _xp2(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")

    @_xp2.command(name="add", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _add4(self, ctx, xp: int, member: nextcord.Member):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        user = readUser(ctx.guild.id, member.id)

        user.xp += xp
        while user.xp_needed < user.xp:
            user.level += 1
            user.xp_needed = (math.floor(5 * (math.pow((user.level - 1), 2)) + 50 * (user.level - 1) + 100))

        update("level_users", "level, xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, member.id])

        await successEmbed(self.bot, ctx, f"{member.mention} ist nun Level {user.level} und hat {user.xp} XP.")
    
    @_xp2.command(name="remove", aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove4(self, ctx, xp: int, member: nextcord.Member):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        user = readUser(ctx.guild.id, member.id)

        user.xp -= xp

        if user.xp <= 0:
            user.xp = 0
            user.level = 1
            user.xp_needed = (math.floor(5 * (math.pow((user.level - 1), 2)) + 50 * (user.level - 1) + 100))

        while user.xp_needed < user.xp:
            user.level -= 1
            user.xp_needed = (math.floor(5 * (math.pow((user.level - 1), 2)) + 50 * (user.level - 1) + 100))

        update("level_users", "level, xp", "guild_id user_id", [user.level, user.xp, ctx.guild.id, member.id])

        await successEmbed(self.bot, ctx, f"{member.mention} ist nun Level {user.level} und hat {user.xp} XP.")

    @_level.group(name="reset", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _reset(self, ctx, user: nextcord.Member = None):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")
        
        if user is None and ctx.invoked_subcommand is None:
            return await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")
        
        if user is not None:
            delete("level_users", "guild_id user_id", [ctx.guild.id, user.id])
            await successEmbed(self.bot, ctx, f"{user} wurde auf Level 1 zurückgesetzt.")

    @_reset.command(name="all", aliases=["a"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _reset2(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        message = "Glückwunsch **{user_name}#{user_discriminator}**!\\n\\nDu bist ein Level aufgestiegen!\\nDu bist nun Level `{level}`"
        
        delete("level_users", "guild_id", [ctx.guild.id])
        delete("level_blacklist_channel", "guild_id", [ctx.guild.id])
        delete("level_blacklist_roles", "guild_id", [ctx.guild.id])
        delete("level_custommessages", "guild_id", [ctx.guild.id])
        delete("level_roles", "guild_id", [ctx.guild.id])
        update("level_system", "xp cooldown mention message", "guild_id", [3, 6, 1, message, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Alle Level und alle Einstellungen wurden zurückgesetzt.")

    @_reset.command(name="level", aliases=["l"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _reset3(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        delete("level_users", "guild_id", [ctx.guild.id])
        await successEmbed(self.bot, ctx, "Alle Level wurden zurückgesetzt.")

    @_reset.command(name="settings", aliases=["s"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _reset4(self, ctx):
        if not checkLevelOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Das Level System ist nicht aktiviert.")

        delete("level_blacklist_channel", "guild_id", [ctx.guild.id])
        delete("level_blacklist_roles", "guild_id", [ctx.guild.id])
        delete("level_custommessages", "guild_id", [ctx.guild.id])
        delete("level_roles", "guild_id", [ctx.guild.id])
        update("level_system", "xp cooldown mention message", "guild_id", [3, 6, 1, 1, "", ctx.guild.id])
        await successEmbed(self.bot, ctx, "Alle Einstellungen wurden zurückgesetzt.")

    @Cog.listener()
    async def on_member_join(self, member):
        if role_id := readOne("role_id", "level_roles", "guild_id level", [member.guild.id, 1]):
            if role := member.guild.get_role(role_id[0]):
                await member.add_roles(role)

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not checkLevelOn(message.guild.id) or message.content.startswith(getPrefixFromDatabase(self.bot, message)):
            return

        if readOne("channel_id", "level_blacklist_channel", "guild_id channel_id", [message.guild.id, message.channel.id]) is not None:
            return
        
        for role in readAll("role_id", "level_blacklist_roles", "guild_id", [message.guild.id]):
            if role in message.author.roles:
                return

        xp, cooldown, mention, lvlmessage = readOne("xp, cooldown, mention, message", "level_system", "guild_id", [message.guild.id])

        levelup = addUserXP(message.guild.id, message.author.id, xp, cooldown)

        if levelup:
            user = readUser(message.guild.id, message.author.id)
            customMessage = readOne("message", "level_custommessages", "guild_id level", [message.guild.id, user.level])

            if lvlmessage is None and customMessage is None:
                return

            allLevelRoles = readAll("role_id", "level_roles", "guild_id", [message.guild.id])
            levelRole = readOne("role_id", "level_roles", "guild_id level", [message.guild.id, user.level])

            role = message.guild.get_role(levelRole) if levelRole is not None else None
            
            if levelRole is not None:
                for role_id in allLevelRoles:
                    role = message.guild.get_role(role_id[0])

                    if role is None:
                        continue

                    if role in message.author.roles:
                        await message.author.remove_roles(role)

                await message.author.add_roles(message.guild.get_role(levelRole))

            match mention:
                case 1:
                    mention = message.author.mention
                case 0:
                    mention = ""
                
            if customMessage is not None:
                lvlmessage = customMessage

            await infoEmbed(self.bot, message.channel, lvlmessage.replace("\\n", "\n").format_map(safeDict(user_name=message.author.name, user_mention=message.author.mention, user_discriminator=message.author.discriminator, level=user.level, xp_needed=user.xp_needed, level_next=user.level + 1, role=role)), content=mention, thumbnail=message.author.display_avatar.url, color=message.author.color)


def checkLevelOn(guildid: int) -> bool:
    enabled = readOne("enabled", "level_system", "guild_id", guildid)

    if enabled is None:
        levelupmessage = "Glückwunsch **{user_name}#{user_discriminator}**!\\n\\nDu bist ein Level aufgestiegen!\\nDu bist nun Level `{level}`"
        insert("level_system", "guild_id, enabled, xp, cooldown, mention, message", [guildid, 0, 3, 6, 1, levelupmessage])
        return False
    
    return enabled[0] == 1

def readUser(guildid: int, userid: int) -> User:
    level = readOne("messages, level, xp, cooldown", "level_users", "guild_id user_id", [guildid, userid])

    if level is None:
        xp_needed = (math.floor(5 * (math.pow(1, 2)) + 50 * 1 + 100))

        insert("level_users", "guild_id, user_id, messages, level, xp, cooldown", [guildid, userid, 0, 1, 0, time()])
        return User(userid, 0, 1, 0, time(), xp_needed)
    
    xp_needed = (math.floor(5 * (math.pow(level[1], 2)) + 50 * level[1] + 100))
    return User(userid, level[0], level[1], level[2], level[3], xp_needed)

def addUserXP(guildid: int, userid: int, xp: int, cooldown: int) -> bool:
    user: User = readUser(guildid, userid)

    if time() - user.cooldown < cooldown:
        return False

    user.xp += xp
    user.messages += 1
    
    if user.xp >= user.xp_needed:
        user.level += 1
        user.xp_needed = (math.floor(5 * (math.pow(user.level, 2)) + 50 * user.level + 100))
        update("level_users", "level xp messages", "guild_id user_id", [user.level, user.xp, user.messages, guildid, userid])
        return True
    
    update("level_users", "xp messages cooldown", "guild_id user_id", [user.xp, user.messages, time(), guildid, userid])
    return False

    
def setup(bot):
    bot.add_cog(levelsys(bot))
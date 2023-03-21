import contextlib
from nextcord.ext import commands
from nextcord.ext.commands import Cog

from .utils.other import checkLink, getPrefixFromDatabase
from .utils.embeds import infoEmbed, errorEmbed, successEmbed
from .utils.database import delete, insert, readOne, readAll, update

class Automod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="badword", aliases=["bad-word", "bad_word", "wordblacklist", "word_blacklist", "word-blacklist"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _badword(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:BadWord:814817356001968141> Bad Words**\n\n> `-badword add <word>`\n> `-badword remove <word>`\n> `-badword show`")

    @_badword.command(name="add", aliases=["a"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _add(self, ctx, word):
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word.lower()])

        if exists is not None:
            return await errorEmbed(self.bot, ctx, "Dieses Wort ist bereits in den Badwords vorhanden.")
        
        insert("badwords", "guild_id, word", [ctx.guild.id, word.lower()])
        await successEmbed(self.bot, ctx, f"**{word} wurde erfolgreich hinzugefügt.**")

    @_badword.command(name="remove", aliases=["del", "delete"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _remove(self, ctx, word):
        exists = readOne("word", "badwords", "guild_id word", [ctx.guild.id, word.lower()])

        if exists is None:
            return await errorEmbed(self.bot, ctx, f"{word} ist nicht auf der Badword Liste.")
        
        delete("badwords", "guild_id word", [ctx.guild.id, word.lower()])
        await successEmbed(self.bot, ctx, f"**{word} wurde erfolgreich entfernt.**")

    @_badword.command(name="list", aliases=["show"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _list(self, ctx):
        words = readAll("word", "badwords", "guild_id", [ctx.guild.id])

        if not words:
            return await errorEmbed(self.bot, ctx, "Es gibt noch keine Badwords.")

        string = "".join(f"{word[0]}\n" for word in words)

        await infoEmbed(self.bot, ctx, f"**<:BadWord:814817356001968141> Bad Words**\n\n{string}")

    @commands.group(name="ghostping", aliases=["ghost-ping", "ghost_ping"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _ghostping(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:Ghostping:1087448502323384330> Anti-Ghostpings**\n\n> `-ghostping on`\n> `-ghostping off`")
    
    @_ghostping.command(name="on", aliases=["activate", "activ"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _on(self, ctx):
        if checkGhostOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Anti-Ghostping ist bereits aktiviert.")

        update("ghostping", "enabled", "guild_id", [1, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Das Anti-Ghostping System wurde aktiviert.")

    @_ghostping.command(name="off", aliases=["deactivate"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _off(self, ctx):
        if not checkGhostOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Anti-Ghostping ist bereits deaktiviert.")

        update("ghostping", "enabled", "guild_id", [0, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Das Anti-Ghostping System wurde deaktiviert.")

    @commands.group(name="linkblocker", aliases=["antilink", "anti-link", "link"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _linkblocker(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:Automod:1087440612430717068> Link Blocker**\n\n> `-linkblocker on`\n> `-linkblocker off`")

    @_linkblocker.command(name="on", aliases=["activate", "activ"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _on2(self, ctx):
        if checkLinkOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Der Linkblocker ist bereits aktiviert.")

        update("linkblocker", "enabled", "guild_id", [1, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Der Linkblocker wurde aktiviert.")

    @_linkblocker.command(name="off", aliases=["deactivate"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def _off2(self, ctx):
        if not checkLinkOn(ctx.guild.id):
            return await errorEmbed(self.bot, ctx, "Der Linkblocker ist bereits deaktiviert.")

        update("linkblocker", "enabled", "guild_id", [0, ctx.guild.id])
        await successEmbed(self.bot, ctx, "Der Linkblocker wurde deaktiviert.")

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.guild_permissions.administrator:
            return

        if checkLink(message.content.lower()):
            if not checkLinkOn(message.guild.id):
                return

            await infoEmbed(self.bot, message.channel, "**<:Automod:1087440612430717068> Du darfst hier keine Links reinschicken.**")

            with contextlib.suppress(Exception):
                return await message.delete()
        
        if message.content.startswith(getPrefixFromDatabase(self.bot, message)):
            return

        words = readAll("word", "badwords", "guild_id", [message.guild.id])

        if all(word[0].lower() not in message.content.lower() for word in words):
            return
        
        await infoEmbed(self.bot, message.channel, "**<:Badword:1087441597622399056> Du darfst dieses Wort nicht sagen.**", delete_after=10)
        with contextlib.suppress(Exception):
            await message.delete()

    @Cog.listener()
    async def on_raw_message_edit(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author.bot:
            return

        if message.author.guild_permissions.administrator:
            return

        if checkLink(message.content.lower()):
            if not checkLinkOn(message.guild.id):
                return

            await infoEmbed(self.bot, message.channel, "**<:Automod:1087440612430717068> Du darfst hier keine Links reinschicken.**")

            with contextlib.suppress(Exception):
                return await message.delete()

        words = readAll("word", "badwords", "guild_id", [message.guild.id])
        
        if any(word[0].lower() in message.content.lower() for word in words):
            await infoEmbed(self.bot, message.channel, "**<:BadWord:814817356001968141> Du darfst dieses Wort nicht sagen.**")
            with contextlib.suppress(Exception):
                await message.delete()

    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.mentions:
            return

        if not checkGhostOn(message.guild.id):
            return
        
        users = ""
        for i, member in enumerate(message.mentions):
            if i == 0: users += f"{member}"; continue
            users += f", {member}"
        
        await infoEmbed(self.bot, message.channel, f"{message.author.mention} hat {users} gepingt.")

def checkGhostOn(guildid: int) -> bool:
    enabled = readOne("enabled", "ghostping", "guild_id", [guildid])

    if enabled is None:
        insert("ghostping", "guild_id, enabled", [guildid, 0])
        return False
    
    return enabled[0] == 1

def checkLinkOn(guildid: int) -> bool:
    enabled = readOne("enabled", "linkblocker", "guild_id", [guildid])

    if enabled is None:
        insert("linkblocker", "guild_id, enabled", [guildid, 0])
        return False

    return enabled[0] == 1

def setup(bot):
    bot.add_cog(Automod(bot))
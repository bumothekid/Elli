from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import errorEmbed, errorLogging
from .utils.language import getLanguageStrings, getLocale, getGuildLanguage

class ErrorHandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        languageStrings = getLanguageStrings("error")
        
        if ctx.guild is None:
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, "en", "noPrivateMessage"))
            
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        if isinstance(error, (commands.CommandNotFound, commands.DisabledCommand)):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "commandNotFound"))

        elif isinstance(error, commands.MissingRequiredArgument):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "missingRequiredArgument"))

        elif isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace("_", " ").title() for perm in error.missing_permissions]
            await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "botMissingPermissions" if len(missing) > 1 else "botMissingPermission", ', '.join(missing)))

        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace("_", " ").replace('guild', 'server').title() for perm in error.missing_permissions]
            await errorEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "missingPermissions" if len(missing) > 1 else "missingPermission", ', '.join(missing)))

        elif isinstance(error, commands.NotOwner):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "notOwner"))

        elif isinstance(error, commands.UserNotFound):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "userNotFound"))

        elif isinstance(error, commands.ChannelNotFound):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "channelNotFound"))

        elif isinstance(error, commands.EmojiNotFound):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "emojiNotFound"))

        elif isinstance(error, commands.RoleNotFound):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "roleNotFound"))

        elif isinstance(error, commands.MessageNotFound):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "messageNotFound"))

        elif isinstance(error, commands.CommandOnCooldown):
            await errorEmbed(self, ctx,  getLocale(self.bot, languageStrings, guildLocale, "commandOnCooldown", f"{error.retry_after:,.2f}"))

        elif isinstance(error, commands.UserInputError):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "userInputError"))

        elif isinstance(error, commands.MaxConcurrencyReached):
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "maxConcurrencyReached"))

        else:
            # await interaction.reply("**Es ⚠️ ein kritischer Fehler aufgetreten\naber keine sorge daran bist nicht du schuld.**")
            await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "criticalError"))
            errorLogging(self.bot, ctx, str(error).split("exception: ")[1])



def setup(bot):
    bot.add_cog(ErrorHandler(bot))
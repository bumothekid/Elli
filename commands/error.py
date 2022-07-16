from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import errorEmbed, errorLogging

class errorhandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await errorEmbed(self, ctx, "Dieser Befehl existiert nicht oder ist gerade deaktiviert.")

        elif isinstance(error, commands.MissingRequiredArgument):
            await errorEmbed(self, ctx, "Es fehlt ein benötigtes Argument.")

        elif isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace("_", " ").title() for perm in error.missing_permissions]
            premessage = "Mir fehlen folgende Berechtigungen" if len(missing) > 1 else "Mir fehlt die folgende Berechtigung"
            await errorEmbed(self.bot, ctx, f"{premessage} um diesen Befehl auszuführen:**\n> `{', '.join(missing)}`** ")

        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace("_", " ").replace('guild', 'server').title() for perm in error.missing_permissions]
            premessage = "Dir fehlen folgende Berechtigungen" if len(missing) > 1 else "Dir fehlt die folgende Berechnigung"
            await errorEmbed(self.bot, ctx, f"{premessage} um diesen Befehl zu nutzen:**\n> `{', '.join(missing)}`** ")

        elif isinstance(error, commands.NotOwner):
            await errorEmbed(self, ctx, "Nur die Developer können diesen Befehl ausführen.")

        elif isinstance(error, commands.UserNotFound):
            await errorEmbed(self, ctx, "Ich konnte diesen User nicht finden.")

        elif isinstance(error, commands.ChannelNotFound):
            await errorEmbed(self, ctx, "Ich konnte diesen Channel nicht finden.")

        elif isinstance(error, commands.EmojiNotFound):
            await errorEmbed(self, ctx, "Ich konnte dieses Emote nicht finden.")

        elif isinstance(error, commands.RoleNotFound):
            await errorEmbed(self, ctx, "Ich konnte diese Rolle nicht finden.")

        elif isinstance(error, commands.MessageNotFound):
            await errorEmbed(self, ctx, "Ich konnte diese Nachricht nicht finden.")

        elif isinstance(error, commands.CommandOnCooldown):
            await errorEmbed(self, ctx, f"Der Befehl ist noch auf Cooldown, versuche es in `{error.retry_after:,.2f}` Sekunden erneut.")

        elif isinstance(error, commands.NoPrivateMessage):
            await errorEmbed(self, ctx, "Dieser Befehl ist nicht für Private Nachrichten verfügbar.")

        elif isinstance(error, commands.UserInputError):
            await errorEmbed(self, ctx, "Du hast eine Falsche eingabe getätigt.")

        else:
            # await interaction.reply("**Es ⚠️ ein kritischer Fehler aufgetreten\naber keine sorge daran bist nicht du schuld.**")
            await errorEmbed(self, ctx, "<:icon_error_red:962068826311254177> Es ist ein kritischer Fehler aufgetreten.")
            await errorLogging(self, ctx, error)



def setup(bot):
    bot.add_cog(errorhandler(bot))
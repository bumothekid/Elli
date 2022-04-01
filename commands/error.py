import nextcord
from .loggingHelper import errorLogging, criticalErrorLogging
from nextcord.ext import commands
from nextcord.ext.commands import Cog

class errorhandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, interaction, error):
        """
        This function is called whenever an error occurs while executing a command
        
        :param interaction: The interaction object that caused the error
        :param error: The error that was raised. In this case, it'll be a CommandInvokeError, which is
        raised whenever a command encounters an error while running
        :return: The return value of a command is being passed to the reply method of the interaction.
        """

        loggingChannel = self.bot.get_channel(957444324080115762)

        if isinstance(error, commands.CommandNotFound):
            embed = await errorLogging(text="**Dieser Command existiert nicht oder ist gerade deaktiviert**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.BotMissingPermissions):
            embed = await errorLogging(text="**Dieser Bot hat nicht genug Berechtigungen.**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = await errorLogging("**Es fehlt ein benötigtes Argument.**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            embed = await errorLogging(f"**Du brauchst die {missing} Berechtigung(en), um diesen Command zu nutzen!**")
            await interaction.reply(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = await errorLogging("**Nur die Developer können diesen Befehl ausführen.**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.UserNotFound):
            embed = await errorLogging("**Ich konnte diesen User nicht finden.**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.ChannelNotFound):
            embed = await errorLogging("**Ich konnte diesen Channel nicht finden.**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.EmojiNotFound):
            embed = await errorLogging("**Ich konnte dieses Emote nicht finden.**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.RoleNotFound):
            embed = await errorLogging("**Ich konnte diese Rolle nicht finden.**")
            await interaction.reply(embed=embed)
            return
        elif isinstance(error, commands.MessageNotFound):
            embed = await errorLogging("**Ich konnte diese Nachricht nicht finden.**")
            try:
                await interaction.reply(embed=embed)
            except:
                return
            return
        else:
            await interaction.reply("**Es ist ein kritischer Fehler aufgetreten\naber keine sorge daran bist nicht du schuld.**")
            embed = await criticalErrorLogging(interaction=interaction, text=error)
            await loggingChannel.send(embed=embed)
            return

            


def setup(bot):
    bot.add_cog(errorhandler(bot))
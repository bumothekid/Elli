import contextlib
import nextcord

from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.utils import errorLogging

class errorhandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, interaction, error):
        loggingChannel = self.bot.get_channel(957444324080115762)

        if isinstance(error, commands.CommandNotFound):
            await errorLogging(interaction, "Dieser Command existiert nicht oder ist gerade deaktiviert.")

        elif isinstance(error, commands.BotMissingPermissions):
            await errorLogging(interaction, "Dieser Bot hat nicht genug Berechtigungen.")

        elif isinstance(error, commands.MissingRequiredArgument):
            await errorLogging(interaction, "Es fehlt ein benötigtes Argument.")
        
        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            await errorLogging(f"Dir fehlen folgende Berechtigung(en) um diesen Command zu nutzen {missing}.")
            
        elif isinstance(error, commands.NotOwner):
            await errorLogging(interaction, "Nur die Developer können diesen Befehl ausführen.")

        elif isinstance(error, commands.UserNotFound):
            await errorLogging(interaction, "Ich konnte diesen User nicht finden.")

        elif isinstance(error, commands.ChannelNotFound):
            await errorLogging(interaction, "Ich konnte diesen Channel nicht finden.")

        elif isinstance(error, commands.EmojiNotFound):
            await errorLogging(interaction, "Ich konnte dieses Emote nicht finden.")

        elif isinstance(error, commands.RoleNotFound):
            await errorLogging(interaction, "Ich konnte diese Rolle nicht finden.")

        elif isinstance(error, commands.MessageNotFound):
            await errorLogging(interaction, "Ich konnte diese Nachricht nicht finden.")

        else:
            # await interaction.reply("**Es ⚠️ ein kritischer Fehler aufgetreten\naber keine sorge daran bist nicht du schuld.**")
            await errorLogging(interaction, "<:icon_error_red:962068826311254177> Es ist ein kritischer Fehler aufgetreten.")
            await criticalErrorLogging(interaction, error, loggingChannel)

async def criticalErrorLogging(ctx, error, channel):
    errorEmbed = nextcord.Embed(
        color=nextcord.Color.red()
    )

    errorEmbed.add_field(name="<:icon_globe:960643612872417280> Guild", value=f"```ini\n{ctx.guild}```", inline=False)
    errorEmbed.add_field(name="<:icon_clide:960643699279265843> Command", value=f"```ini\n{ctx.message.content}```", inline=False)
    errorEmbed.add_field(name="<:icon_error_red:962068826311254177> Error", value=f"```python\n{error}```", inline=False)

    await channel.send(embed=errorEmbed)



def setup(bot):
    bot.add_cog(errorhandler(bot))
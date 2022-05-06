from re import A
from discord import Color
import nextcord
from nextcord.ext import commands
from numpy import info

from .utils.models.EmbedField import EmbedField
from .utils.embeds import infoEmbed

cache = []

class ClassHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def help(self, ctx):
        view = HelpButtonView(self.bot)
        message = await infoEmbed(self.bot, ctx, f"**<:icon_commands:966028792890003547> {self.bot.user.name}'s Command Kategorien**\n\n> **<:icon_discord:968229925528145980> Generell**\n> **💡 Nützlich**\n> **<:icon_moderation:967038345395961896> Moderation**\n> **<:icon_fun:968221028985761812> Fun**\n> **<:icon_member_joined:965033605707481128> Welcome**\n> **<:icon_member_left:965034270622122044> Leave**\n> **<a:giveaway:958492679749140510> Giveaway**\n> **<:icon_ticket:959885507557470239> Ticket System**\n> **⏳ Tempchannel**\n> **<:icon_roles:968233835710017566> Reaction Roles**\n> **🌟 Level System**\n> **📨 Invite-Logger**\n> **<:icon_badword:970238990743658518> Bad Words**\n> **<:icon_ghostping:970292783027986463> Anti Ghostping**\n> **<:icon_automod:967038254367006791> Link Blocker**", view=view)
        view.message = message
        cache.append(f"{message.id}|{ctx.author.id}")


async def calltimeout(bot, message):
    view = HelpButtonView(bot, True)
    embed = nextcord.Embed(
                description=f"**<:icon_commands:966028792890003547> {bot.user.name}'s Command Kategorien**\n\n> **<:icon_discord:968229925528145980> Generell**\n> **💡 Nützlich**\n> **<:icon_moderation:967038345395961896> Moderation**\n> **<:icon_fun:968221028985761812> Fun**\n> **<:icon_member_joined:965033605707481128> Welcome**\n> **<:icon_member_left:965034270622122044> Leave**\n> **<a:giveaway:958492679749140510> Giveaway**\n> **<:icon_ticket:959885507557470239> Ticket System**\n> **⏳ Tempchannel**\n> **<:icon_roles:968233835710017566> Reaction Roles**\n> **🌟 Level System**\n> **📨 Invite-Logger**\n> **<:icon_badword:970238990743658518> Bad Words**\n> **<:icon_ghostping:970292783027986463> Anti Ghostping**\n> **<:icon_automod:967038254367006791> Link Blocker**",
                color=nextcord.Color.blurple()
    )
    message = await message.edit(embed=embed, view=view)
    view.message = message

class HelpButtonView(nextcord.ui.View):
    def __init__(self, bot, disabled: bool = False):
        super().__init__(timeout=300)
        self.add_item(HelpButton(bot, disabled))
        self.bot = bot
        self.disabled = disabled

    async def on_timeout(self) -> None:
        if self.disabled:
            return
            
        await calltimeout(self.bot, self.message)

class HelpButton(nextcord.ui.Select):
    def __init__(self, bot, disabled: bool):
        options = [
            nextcord.SelectOption(label="Kategorien", emoji="<:icon_commands:966028792890003547>", default=False),
            nextcord.SelectOption(label="Generell", emoji="<:icon_discord:968229925528145980>"),
            nextcord.SelectOption(label="Nützlich", emoji="💡"),
            nextcord.SelectOption(label="Moderation", emoji="<:icon_moderation:967038345395961896>"),
            nextcord.SelectOption(label="Fun", emoji="<:icon_fun:968221028985761812>"),
            nextcord.SelectOption(label="Welcome", emoji="<:icon_member_joined:965033605707481128>"),
            nextcord.SelectOption(label="Leave", emoji="<:icon_member_left:965034270622122044>"),
            nextcord.SelectOption(label="Giveaway", emoji="<a:giveaway:958492679749140510>"),
            nextcord.SelectOption(label="Ticket System", emoji="<:icon_ticket:959885507557470239>"),
            nextcord.SelectOption(label="Tempchannel", emoji="⏳"),
            nextcord.SelectOption(label="Reaction Roles", emoji="<:icon_roles:968233835710017566>"),
            nextcord.SelectOption(label="Level System", emoji="🌟"),
            nextcord.SelectOption(label="Invite Logger", emoji="📨"),
            nextcord.SelectOption(label="Bad Words", emoji="<:icon_badword:970238990743658518>"),
            nextcord.SelectOption(label="Anti Ghostping", emoji="<:icon_ghostping:970292783027986463>"),
            nextcord.SelectOption(label="Link Blocker", emoji="<:icon_automod:967038254367006791>")
        ]
        super().__init__(placeholder="Wähle eine Kategorie", options=options, disabled=disabled)
        self.bot = bot

    async def callback(self, interaction):
        if f"{interaction.message.id}|{interaction.user.id}" not in cache:
            return
    
        match self.values[0]:
            case "Kategorien":
                embed = nextcord.Embed(
                    description=f"**<:icon_commands:966028792890003547> {self.bot.user.name}'s Command Kategorien**\n\n> **<:icon_discord:968229925528145980> Generell**\n> **💡 Nützlich**\n> **<:icon_moderation:967038345395961896> Moderation**\n> **<:icon_fun:968221028985761812> Fun**\n> **<:icon_member_joined:965033605707481128> Welcome**\n> **<:icon_member_left:965034270622122044> Leave**\n> **<a:giveaway:958492679749140510> Giveaway**\n> **<:icon_ticket:959885507557470239> Ticket System**\n> **⏳ Tempchannel**\n> **<:icon_roles:968233835710017566> Reaction Roles**\n> **🌟 Level System**\n> **📨 Invite-Logger**",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Generell":
                embed = nextcord.Embed(
                    description=f"**<:icon_discord:968229925528145980> Generelle Commands**\n\n> `-help`\n> <:icon_reply:969871237062983740> Zeigt diese Hilfe an\n> `-botinfo`\n> <:icon_reply:969871237062983740> Zeigt Infos zu diesem Bot an\n> `-invite`\n> <:icon_reply:969871237062983740> Zeigt einen Invite zu diesem Bot an\n> `-support`\n> <:icon_reply:969871237062983740> Zeigt einen Support-Server an\n> `-vote`\n> <:icon_reply:969871237062983740> Zeigt einen Vote-Link an",
                    color=nextcord.Color.blurple()
                    )

                await interaction.message.edit(embed=embed)

            case "Nützlich":
                embed = nextcord.Embed(
                    description=f"**💡 Nützlich**\n\n> `-ping`\n> <:icon_reply:969871237062983740> Zeigt den Ping an\n> `-userinfo <@user>`\n> <:icon_reply:969871237062983740> Zeigt Infos zu einem User an\n> `-serverinfo`\n> <:icon_reply:969871237062983740> Zeigt Infos zu diesem Server an\n> `-avatar <@user>`\n> <:icon_reply:969871237062983740> Zeigt das Avatar eines Users an\n> `-bugreport <text>`\n> <:icon_reply:969871237062983740> Sendet einen Bug Report an die Developer",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Moderation":
                embed = nextcord.Embed(
                    description=f"**<:icon_moderation:967038345395961896> Moderation**\n\n> `-clear <anzahl>`\n> <:icon_reply:969871237062983740> Löscht eine bestimmte Anzahl von Nachrichten\n> `-ban <@user>`\n> <:icon_reply:969871237062983740> Bannt einen User\n> `-kick <@user>`\n> <:icon_reply:969871237062983740> Kickt einen User\n> `-mute <@user> <time>`\n> <:icon_reply:969871237062983740> Mute einen User\n> `-unmute <@user>`\n> <:icon_reply:969871237062983740> Unmute einen User\n> `-addrole <@user> <@rolle>`\n> <:icon_reply:969871237062983740> Fügt eine Rolle einem User hinzu\n> `-removerole <@user> <@rolle>`\n> <:icon_reply:969871237062983740> Entfernt eine Rolle eines Users",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Fun":
                embed = nextcord.Embed(
                    description=f"**<:icon_fun:968221028985761812> Fun**\n\n> `-8ball <frage>`\n> <:icon_reply:969871237062983740> Fragt eine Frage mit einem 8ball\n> `-cat`\n> <:icon_reply:969871237062983740> Zeigt ein Bild von einer Katze\n> `-dog`\n> <:icon_reply:969871237062983740> Zeigt ein Bild von einem Hund\n> `-reverse <text>`\n> <:icon_reply:969871237062983740> Dreht den Text um den du angibst",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Welcome":
                embed = nextcord.Embed(
                    description=f"**<:icon_member_joined:965033605707481128> Willkommensnachrichten**\n\n> `-welcome channel set <#channel>`\n> <:icon_reply:969871237062983740> Setzt einen Willkommenskanal\n> `-welcome channel remove`\n> <:icon_reply:969871237062983740> Entfernt den davor gesetzten Willkommenskanal\n> `-welcome message <message>`\n> <:icon_reply:969871237062983740> Setzt eine neue Willkommensnachricht\n> `-welcome picture set <picture>`\n> <:icon_reply:969871237062983740> Setzt ein Willkommensbild\n> `-welcome picture remove`\n> <:icon_reply:969871237062983740> Entfernt das aktuelle Willkommensbild\n> `-welcome picture show`\n> <:icon_reply:969871237062983740> Zeigt dir alle aktuell Verfügbaren Willkommensbilder\n\n> Variablen für die Willkommensnachricht `{{user_mention}}`, `{{user_name}}`, `{{user_discriminator}}`, `{{guild_name}}`, `{{guild_membercount}}`\n> Du kannst eine Willkommensnachricht mit mehreren Zeilen erstellen mit `\\n`\n> Um die Willkommensnachricht ganz zu entfernen füge `_ _` als Nachricht ein",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)
            
            case "Leave":
                embed = nextcord.Embed(
                    description=f"**<:icon_member_left:965034270622122044> Verlassnachrichten**\n\n> `-leave channel set <#channel>`\n> <:icon_reply:969871237062983740> Setzt einen Verlasskanal\n> `-leave channel remove`\n> <:icon_reply:969871237062983740> Entfernt den davor gesetzten Verlasskanal\n> `-leave message <message>`\n> <:icon_reply:969871237062983740> Setzt eine neue Verlassnachricht\n> `-leave picture set <picture>`\n> <:icon_reply:969871237062983740> Setzt ein Verlassbild\n> `-leave picture remove`\n> <:icon_reply:969871237062983740> Entfernt das aktuelle Verlassbild\n> `-leave picture show`\n> <:icon_reply:969871237062983740> Zeigt dir alle aktuell Verfügbaren Verlassbilder\n\n> Variablen für die Verlassnachricht `{{user_mention}}`, `{{user_name}}`, `{{user_discriminator}}`, `{{guild_name}}`, `{{guild_membercount}}`\n> Du kannst eine Verlassnachricht mit mehreren Zeilen erstellen mit `\\n`\n> Um die Verlassnachricht ganz zu entfernen füge `_ _` als Nachricht ein",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)
            
            case "Giveaway":
                embed = nextcord.Embed(
                    description="**<a:giveaway:958492679749140510> Giveaway Commands**\n\n> `-giveaway create`\n> <:icon_reply:969871237062983740> Starten den start prozess für ein Giveaway\n> `-giveaway quick <#channel> <zeit> <winner> <preis>`\n> <:icon_reply:969871237062983740> Erstellt ein Giveaway mit einem Befehl\n> `-giveaway drop <#channel> <preis>`\n> <:icon_reply:969871237062983740> Erstellt einen Drop den die erste person erhält die Reagiert\n> `-giveaway end <#channel> <messageid>`\n> <:icon_reply:969871237062983740> Beendet ein noch laufendes Giveaway\n> `-giveaway reroll <#channel> <messageid> <winner>`\n> <:icon_reply:969871237062983740> Wählt ein neue Gewinner für das Giveaway\n> `-giveaway list`\n> <:icon_reply:969871237062983740> Zeigt dir alle momentan laufenden Giveaways an",
                    color=nextcord.Color.blurple()
                )
                
                await interaction.message.edit(embed=embed)

            case "Ticket System":
                embed = nextcord.Embed(
                    description="**<:Ticket:959885507557470239> Ticket System**\n\n> `-ticket create <#channel> <@rolle> <text>`\n> <:icon_reply:969871237062983740> Erstellt ein neues Ticket wo User Reagieren können\n> `-ticket update <#channel> <messageid> <@rolle> <text>`\n> <:icon_reply:969871237062983740> Setzt ein neuen Text für ein bereits erstelltes Ticket\n> `-ticket delete <#channel> <messageid>`\n> <:icon_reply:969871237062983740> Löscht ein altes Ticket das nicht mehr gebraucht wird\n> `-ticket message <text>`\n> <:icon_reply:969871237062983740> Setzt einen neuen Ticket öffnungs Text\n> `-ticket list`\n> <:icon_reply:969871237062983740> Zeigt alle aktuellen Tickets an\n> `-ticket log set <#channel>`\n> <:icon_reply:969871237062983740> Setzt einen Kanal für Ticket Protokollierung\n> `-ticket log remove`\n> <:icon_reply:969871237062983740> Entfernt den Kanal für die Ticket Protokollierung\n\n> Variablen für die Ticket öffnungs Nachricht: `{user_name}` `{user_discriminator}` `{user_mention}` `{ticket_link}` `{guild_name}` `{moderation_role}`\n> Du kannst ein Ticket mit mehreren Zeilen erstellen mit `\\n`",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Tempchannel":
                embed = nextcord.Embed(
                    description="** `⏳`Tempchannel Commands**\n\n> `-tempchannel set <channel>`\n> <:icon_reply:969871237062983740> Setzt ein Tempchannel Sprachkanal\n> `-tempchannel remove`\n> <:icon_reply:969871237062983740> Entfernt den Sprachkanal als Tempchannel\n> `-tempchannel name <name>`\n> <:icon_reply:969871237062983740> Setzt einen neuen standard Namen\n\n> Variablen für den Namen: `{user}`, `{anzahl}`",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Reaction Roles":
                embed = nextcord.Embed(
                    description="**<:icon_roles:968233835710017566> Reactionrole einrichtung**\n\n> `-rr create <#channel> <messageid> <emote> <@&rolle>`\n> <:icon_reply:969871237062983740> Erstellt eine neue Reaction Role\n> `-rr delete <#channel> <messageid> <emote>`\n> <:icon_reply:969871237062983740> Löscht eine bereits vorhandene Reaction Role",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Level System":
                embed = nextcord.Embed(
                    description="** Level System**\n\n"
                                        "> `-level <@user>`\n> <:icon_reply:969871237062983740> Zeigt dir dein/das Level eines Users an\n"
                                        "> `-leaderboard`\n> <:icon_reply:969871237062983740> Zeigt dir die Top 10 User\n\n"
                                        "> `-level settings`\n> <:icon_reply:969871237062983740> Zeigt dir alle möglichen Einstellungen\n"
                                        "> `-level <on | off>`\n> <:icon_reply:969871237062983740> Schaltet das Level Sytem an und aus\n"
                                        "> `-level xp <anzahl>`\n> <:icon_reply:969871237062983740> Setzt eine XP anzahl per Nachricht\n"
                                        "> `-level cooldown <sekunden>`\n> <:icon_reply:969871237062983740> Setzt den cooldown auf eine bestimmte Zeit\n\n"
                                        "> `-level message <text>`\n> <:icon_reply:969871237062983740> Setzt die Nachricht für ein Level Up\n"
                                        "> `-level message`\n> <:icon_reply:969871237062983740> Zeigt dir die aktuelle Level Up Nachricht\n"
                                        "> `-level ping <on | off>`\n> <:icon_reply:969871237062983740> Schaltet den Ping @ ein und aus bei einem Level Up\n\n"
                                        "> `-level custom add <level> <text>`\n> <:icon_reply:969871237062983740> Setzt eine custom Nachricht für ein bestimmtes Level\n"
                                        "> `-level custom remove <level>\n> <:icon_reply:969871237062983740>` Entfernt eine custom Nachricht für ein bestimmtes Level\n"
                                        "> `-level custom show <level>`\n> <:icon_reply:969871237062983740> Zeigt dir die custom Nachricht von einem bestimmten Level\n"
                                        "> `-level custom show`\n> <:icon_reply:969871237062983740> Zeigt dir alle custom Nachrichten\n\n"
                                        "> `-level roles add <level> <@rolle>`\n> <:icon_reply:969871237062983740> Fügt eine Level Up Rolle zu einem bestimmten Level hinzu\n"
                                        "> `-level roles remove <level>`\n> <:icon_reply:969871237062983740> Entfernt eine Level Up Rolle von einem bestimmten Level\n"
                                        "> `-level roles joinrole add <@rolle>`\n> <:icon_reply:969871237062983740> Setzt eine Start Rolle für das Level System die bei dem ersten Level Up wieder weggenommen wird\n"
                                        "> `-level roles joinrole remove`\n> <:icon_reply:969871237062983740> Entfernt diese Start Rolle wieder\n"
                                        "> `-level roles`\n> <:icon_reply:969871237062983740> Zeigt alle Level an mit einer Level Up Rolle\n\n"
                                        "> `-level blacklist add <@rolle | #channel>`\n> <:icon_reply:969871237062983740> Fügt einen Kanal oder eine Rolle der Blacklist hinzu\n"
                                        "> `-level blacklist remove <@rolle | #channel>`\n> <:icon_reply:969871237062983740> Entfernt eine Rolle oder einen Kanal von der Blacklist\n"
                                        "> `-level blacklist`\n> <:icon_reply:969871237062983740> Zeigt alle Rollen und Kanäle die auf einer Blacklist stehen\n\n"
                                        "> `-level modifylevel add <level> <@user>`\n> <:icon_reply:969871237062983740> Füge eine bestimmte anzahl an Leveln einem User hinzu\n"
                                        "> `-level modifylevel remove <level> <@user>`\n> <:icon_reply:969871237062983740> Entfernte eine bestimmte anzahl an Leveln von einem User\n"
                                        "> `-level modifyxp add <xp> <@user>`\n> <:icon_reply:969871237062983740> Füge eine bestimmte anzahl an XP einem User hinzu\n"
                                        "> `-level modifyxp remove <xp> <@user>`\n> <:icon_reply:969871237062983740> Entferne eine bestimmte anzahl an XP von einem User\n\n"
                                        "> `-level reset <@user>`\n> <:icon_reply:969871237062983740> Setzte einen User komplett zurück\n"
                                        "> `-level reset level`\n> <:icon_reply:969871237062983740> Setze alle Level zurück\n"
                                        "> `-level reset settings`\n> <:icon_reply:969871237062983740> Setzte alle Einstellungen zurück\n"
                                        "> `-level reset all`\n> <:icon_reply:969871237062983740> Setze alles zurück\n\n"
                                        "> Variablen für die Level Up Nachricht:\n"
                                        "> `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{level}`, `{xp_needed}`, `{level_next}` und `{role}` für custom Nachrichten\n\n"
                                        "> Du kannst eine Level Up Nachricht mit mehreren erstellen mit `\\n`\n"
                                        "> Um die Level Up Nachricht zu entfernen füge `off` als Nachricht ein.",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Invite Logger":
                embed = nextcord.Embed(
                    description="Soon!",
                    color=nextcord.Color.blurple()
                )
                
                await interaction.message.edit(embed=embed)
            
            case "Bad Words":
                embed = nextcord.Embed(
                    description="**<:icon_badword:970238990743658518> Bad Words**\n\n> `-badword add <word>`\n> <:icon_reply:969871237062983740> Fügt ein Wort der Blacklist hinzu\n> `-badword remove <word>`\n> <:icon_reply:969871237062983740> Entfernt ein Wort von der Blacklist\n> `-badword show`\n> <:icon_reply:969871237062983740> Zeigt dir alle Wörter auf der Blacklist",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Anti Ghostping":
                embed = nextcord.Embed(
                    description="**<:icon_ghostping:970292783027986463> Anti-Ghostpings**\n\n> `-ghostping on`\n> <:icon_reply:969871237062983740> Schaltet die Anti Ghostping Erkenn Funktion ein\n> `-ghostping off`\n> <:icon_reply:969871237062983740> Schaltet die Anti Ghostping Erkenn Funktion aus",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

            case "Link Blocker":
                embed = nextcord.Embed(
                    description="**<:icon_automod:967038254367006791> Link Blocker**\n\n> `-linkblocker on`\n> <:icon_reply:969871237062983740> Schaltet den Linkblocker ein\n `-linkblocker off`\n> <:icon_reply:969871237062983740> Schaltet den Link Blocker aus",
                    color=nextcord.Color.blurple()
                )

                await interaction.message.edit(embed=embed)

def setup(bot):
    bot.add_cog(ClassHelp(bot))

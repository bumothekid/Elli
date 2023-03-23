import contextlib
import nextcord
from nextcord.ext import commands

from .utils.embeds import infoEmbed
from .utils.database import readOne

cache = []
prefix = None

class ClassHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def help(self, ctx):
        view = HelpButtonView(self.bot)
        message = await infoEmbed(self.bot, ctx, f"**<:Commands:1087442278118871140> {self.bot.user.name}'s Command Kategorien**\n\n> **<:Discord:1087443793810301051> Generell**\n> **💡 Nützlich**\n> **<:Moderator:1087456158421352508> Moderation**\n> **<:Fun:1087447621582454926> Fun**\n> **<:MemberJoin:1087453129198546964> Welcome**\n> **<:MemberLeave:1087453384858157149> Leave**\n> **<a:Giveaway:1087437215648456794> Giveaway**\n> **<:Ticket:1087437978873376798> Ticket System**\n> **⏳ Tempchannel**\n> **<:Roles:1087457575257255998> Reaction Roles**\n> **🌟 Level System**\n> **📨 Invite-Logger**\n> **<:Badword:1087441597622399056> Bad Words**\n> **<:Ghostping:1087448502323384330> Anti Ghostping**\n> **<:Automod:1087440612430717068>  Link Blocker**", view=view)
        global prefix
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[message.guild.id])[0]
        view.message = message
        cache.append(f"{message.id}|{ctx.author.id}")

    @nextcord.slash_command(name="help", description="Zeigt dir alle Commands an")
    async def _help(self, interaction):
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[interaction.guild.id])[0]
        await infoEmbed(self, interaction, f"**<:Commands:1087442278118871140> {self.bot.user.name}'s Command Kategorien**\n\n> Der Bot läuft noch auf Message Commands\n> Wir bitten deshalb darum den normalen Help Command `{prefix}help` zu nutzen.", ephemeral=True)


async def calltimeout(bot, message):
    view = HelpButtonView(bot, True)
    embed = nextcord.Embed(
                description=f"**<:Commands:1087442278118871140> {bot.user.name}'s Command Kategorien**\n\n> **<:Discord:1087443793810301051> Generell**\n> **💡 Nützlich**\n> **<:Moderator:1087456158421352508> Moderation**\n> **<:Fun:1087447621582454926> Fun**\n> **<:MemberJoin:1087453129198546964> Welcome**\n> **<:MemberLeave:1087453384858157149> Leave**\n> **<a:Giveaway:1087437215648456794> Giveaway**\n> **<:Ticket:1087437978873376798> Ticket System**\n> **⏳ Tempchannel**\n> **<:Roles:1087457575257255998> Reaction Roles**\n> **🌟 Level System**\n> **📨 Invite-Logger**\n> **<:Badword:1087441597622399056> Bad Words**\n> **<:Ghostping:1087448502323384330> Anti Ghostping**\n> **<:Automod:1087440612430717068>  Link Blocker**",
                color=nextcord.Color.blurple()
    )
    message = await message.edit(embed=embed, view=view)
    view.message = message

class HelpButtonView(nextcord.ui.View):
    def __init__(self, bot, disabled: bool = False, category: str = None):
        super().__init__(timeout=300)
        self.add_item(HelpButton(bot, disabled, category))
        self.bot = bot
        self.disabled = disabled

    async def on_timeout(self) -> None:
        if self.disabled:
            return
            
        await calltimeout(self.bot, self.message)

class HelpButton(nextcord.ui.Select):
    def __init__(self, bot, disabled: bool, category: str = None):
        options = [
            nextcord.SelectOption(label="Kategorien", emoji="<:Commands:1087442278118871140>", default=category is None,),
            nextcord.SelectOption(label="Generell", emoji="<:Discord:1087443793810301051>", default=category == "generell"),
            nextcord.SelectOption(label="Nützlich", emoji="💡", default=category == "nützlich"),
            nextcord.SelectOption(label="Moderation", emoji="<:Moderator:1087456158421352508>", default=category == "moderation"),
            nextcord.SelectOption(label="Fun", emoji="<:Fun:1087447621582454926>", default=category == "fun"),
            nextcord.SelectOption(label="Welcome", emoji="<:MemberJoin:1087453129198546964>", default=category == "welcome"),
            nextcord.SelectOption(label="Leave", emoji="<:MemberLeave:1087453384858157149>", default=category == "leave"),
            nextcord.SelectOption(label="Giveaway", emoji="<a:Giveaway:1087437215648456794>", default=category == "giveaway"),
            nextcord.SelectOption(label="Ticket System", emoji="<:Ticket:1087437978873376798>", default=category == "ticket system"),
            nextcord.SelectOption(label="Tempchannel", emoji="⏳", default=category == "tempchannel"),
            nextcord.SelectOption(label="Reaction Roles", emoji="<:Roles:1087457575257255998>", default=category == "reaction roles"),
            nextcord.SelectOption(label="Level System", emoji="🌟", default=category == "level system"),
            nextcord.SelectOption(label="Invite-Logger", emoji="📨", default=category == "invite-logger"),
            nextcord.SelectOption(label="Bad Words", emoji="<:Badword:1087441597622399056>", default=category == "bad words"),
            nextcord.SelectOption(label="Anti Ghostping", emoji="<:Ghostping:1087448502323384330>", default=category == "anti ghostping"),
            nextcord.SelectOption(label="Link Blocker", emoji="<:Automod:1087440612430717068>", default=category == "link blocker"),
        ]

        super().__init__(placeholder="Wähle eine Kategorie", options=options, disabled=disabled)
        self.bot = bot

    async def callback(self, interaction):
        if f"{interaction.message.id}|{interaction.user.id}" not in cache:
            return
        
        view = HelpButtonView(self.bot, False, self.values[0].lower() if self.values[0] != "Kategorien" else None)

        with contextlib.suppress(Exception):
            match self.values[0]:
                case "Kategorien":
                    embed = nextcord.Embed(
                        description=f"**<:Commands:1087442278118871140> {self.bot.user.name}'s Command Kategorien**\n\n> **<:Discord:1087443793810301051> Generell**\n> **💡 Nützlich**\n> **<:Moderator:1087456158421352508> Moderation**\n> **<:Fun:1087447621582454926> Fun**\n> **<:MemberJoin:1087453129198546964> Welcome**\n> **<:MemberLeave:1087453384858157149> Leave**\n> **<a:Giveaway:1087437215648456794> Giveaway**\n> **<:Ticket:1087437978873376798> Ticket System**\n> **⏳ Tempchannel**\n> **<:Roles:1087457575257255998> Reaction Roles**\n> **🌟 Level System**\n> **📨 Invite-Logger**\n> **<:Badword:1087441597622399056> Bad Words**\n> **<:Ghostping:1087448502323384330> Anti Ghostping**\n> **<:Automod:1087440612430717068>  Link Blocker**",
                        color=nextcord.Color.blurple()
                    )

                case "Generell":
                    embed = nextcord.Embed(
                        description=f"**<:Discord:1087443793810301051> Generelle Commands**\n\n> `{prefix}help`\n> <:Reply:1087438925632643082> Zeigt diese Hilfe an\n> `{prefix}prefix <prefix>`\n> <:Reply:1087438925632643082>  Ändert die Prefix von dem Bot\n> `{prefix}botinfo`\n> <:Reply:1087438925632643082> Zeigt Infos zu diesem Bot an\n> `{prefix}invite`\n> <:Reply:1087438925632643082> Zeigt einen Invite zu diesem Bot an\n> `{prefix}support`\n> <:Reply:1087438925632643082> Zeigt einen Support-Server an\n> `{prefix}vote`\n> <:Reply:1087438925632643082> Zeigt einen Vote-Link an",
                        color=nextcord.Color.blurple()
                        )

                case "Nützlich":
                    embed = nextcord.Embed(
                        description=f"**💡 Nützlich**\n\n> `{prefix}ping`\n> <:Reply:1087438925632643082> Zeigt den Ping an\n> `{prefix}userinfo <@user>`\n> <:Reply:1087438925632643082> Zeigt Infos zu einem User an\n> `{prefix}serverinfo`\n> <:Reply:1087438925632643082> Zeigt Infos zu diesem Server an\n> `{prefix}avatar <@user>`\n> <:Reply:1087438925632643082> Zeigt das Avatar eines Users an\n> `{prefix}bugreport <text>`\n> <:Reply:1087438925632643082> Sendet einen Bug Report an die Developer",
                        color=nextcord.Color.blurple()
                    )

                case "Moderation":
                    embed = nextcord.Embed(
                        description=f"**<:Moderator:1087456158421352508> Moderation**\n\n> `{prefix}clear <anzahl>`\n> <:Reply:1087438925632643082> Löscht eine bestimmte Anzahl von Nachrichten\n> `{prefix}ban <@user>`\n> <:Reply:1087438925632643082> Bannt einen User\n> `{prefix}kick <@user>`\n> <:Reply:1087438925632643082> Kickt einen User\n> `{prefix}mute <@user> <time>`\n> <:Reply:1087438925632643082> Mute einen User\n> `{prefix}unmute <@user>`\n> <:Reply:1087438925632643082> Unmute einen User\n> `{prefix}addrole <@user> <@rolle>`\n> <:Reply:1087438925632643082> Fügt eine Rolle einem User hinzu\n> `{prefix}removerole <@user> <@rolle>`\n> <:Reply:1087438925632643082> Entfernt eine Rolle eines Users",
                        color=nextcord.Color.blurple()
                    )

                case "Fun":
                    embed = nextcord.Embed(
                        description=f"**<:Fun:1087447621582454926> Fun**\n\n> `{prefix}8ball <frage>`\n> <:Reply:1087438925632643082> Fragt eine Frage mit einem 8ball\n> `{prefix}cat`\n> <:Reply:1087438925632643082> Zeigt ein Bild von einer Katze\n> `{prefix}dog`\n> <:Reply:1087438925632643082> Zeigt ein Bild von einem Hund\n> `{prefix}reverse <text>`\n> <:Reply:1087438925632643082> Dreht den Text um den du angibst",
                        color=nextcord.Color.blurple()
                    )

                case "Welcome":
                    embed = nextcord.Embed(
                        description=f"**<:MemberJoin:1087453129198546964> Willkommensnachrichten**\n\n> `{prefix}welcome channel set <#channel>`\n> <:Reply:1087438925632643082> Setzt einen Willkommenskanal\n> `{prefix}welcome channel remove`\n> <:Reply:1087438925632643082> Entfernt den davor gesetzten Willkommenskanal\n> `{prefix}welcome message <message>`\n> <:Reply:1087438925632643082> Setzt eine neue Willkommensnachricht\n> `{prefix}welcome picture set <picture>`\n> <:Reply:1087438925632643082> Setzt ein Willkommensbild\n> `{prefix}welcome picture remove`\n> <:Reply:1087438925632643082> Entfernt das aktuelle Willkommensbild\n> `{prefix}welcome picture show`\n> <:Reply:1087438925632643082> Zeigt dir alle aktuell Verfügbaren Willkommensbilder\n\n> Variablen für die Willkommensnachricht `{{user_mention}}`, `{{user_name}}`, `{{user_discriminator}}`, `{{guild_name}}`, `{{guild_membercount}}`\n> Du kannst eine Willkommensnachricht mit mehreren Zeilen erstellen mit `\\n`\n> Um die Willkommensnachricht ganz zu entfernen füge `_ _` als Nachricht ein",
                        color=nextcord.Color.blurple()
                    )

                case "Leave":
                    embed = nextcord.Embed(
                        description=f"**<:MemberLeave:1087453384858157149> Verlassnachrichten**\n\n> `{prefix}leave channel set <#channel>`\n> <:Reply:1087438925632643082> Setzt einen Verlasskanal\n> `{prefix}leave channel remove`\n> <:Reply:1087438925632643082> Entfernt den davor gesetzten Verlasskanal\n> `{prefix}leave message <message>`\n> <:Reply:1087438925632643082> Setzt eine neue Verlassnachricht\n> `{prefix}leave picture set <picture>`\n> <:Reply:1087438925632643082> Setzt ein Verlassbild\n> `{prefix}leave picture remove`\n> <:Reply:1087438925632643082> Entfernt das aktuelle Verlassbild\n> `{prefix}leave picture show`\n> <:Reply:1087438925632643082> Zeigt dir alle aktuell Verfügbaren Verlassbilder\n\n> Variablen für die Verlassnachricht `{{user_mention}}`, `{{user_name}}`, `{{user_discriminator}}`, `{{guild_name}}`, `{{guild_membercount}}`\n> Du kannst eine Verlassnachricht mit mehreren Zeilen erstellen mit `\\n`\n> Um die Verlassnachricht ganz zu entfernen füge `_ _` als Nachricht ein",
                        color=nextcord.Color.blurple()
                    )

                case "Giveaway":
                    embed = nextcord.Embed(
                        description=f"**<a:Giveaway:1087437215648456794> Giveaway Commands**\n\n> `{prefix}giveaway create`\n> <:Reply:1087438925632643082> Starten den start prozess für ein Giveaway\n> `{prefix}giveaway quick <#channel> <zeit> <winner> <preis>`\n> <:Reply:1087438925632643082> Erstellt ein Giveaway mit einem Befehl\n> `{prefix}giveaway drop <#channel> <preis>`\n> <:Reply:1087438925632643082> Erstellt einen Drop den die erste person erhält die Reagiert\n> `{prefix}giveaway end <#channel> <messageid>`\n> <:Reply:1087438925632643082> Beendet ein noch laufendes Giveaway\n> `{prefix}giveaway reroll <#channel> <messageid> <winner>`\n> <:Reply:1087438925632643082> Wählt ein neue Gewinner für das Giveaway\n> `{prefix}giveaway list`\n> <:Reply:1087438925632643082> Zeigt dir alle momentan laufenden Giveaways an",
                        color=nextcord.Color.blurple()
                    )

                case "Ticket System":
                    embed = nextcord.Embed(
                        description=f"**<:Ticket:1087437978873376798> Ticket System**\n\n> `{prefix}ticket create <#channel> <@rolle> <text>`\n> <:Reply:1087438925632643082> Erstellt ein neues Ticket wo User Reagieren können\n> `{prefix}ticket update <#channel> <messageid> <@rolle> <text>`\n> <:Reply:1087438925632643082> Setzt ein neuen Text für ein bereits erstelltes Ticket\n> `{prefix}ticket delete <#channel> <messageid>`\n> <:Reply:1087438925632643082> Löscht ein altes Ticket das nicht mehr gebraucht wird\n> `{prefix}ticket message <text>`\n> <:Reply:1087438925632643082> Setzt einen neuen Ticket öffnungs Text\n> `{prefix}ticket list`\n> <:Reply:1087438925632643082> Zeigt alle aktuellen Tickets an\n> `{prefix}ticket log set <#channel>`\n> <:Reply:1087438925632643082> Setzt einen Kanal für Ticket Protokollierung\n> `{prefix}ticket log remove`\n> <:Reply:1087438925632643082> Entfernt den Kanal für die Ticket Protokollierung\n\n> Variablen für die Ticket öffnungs Nachricht: `{{user_name}}` `{{user_discriminator}}` `{{user_mention}}` `{{ticket_link}}` `{{guild_name}}` `{{moderation_role}}`\n> Du kannst ein Ticket mit mehreren Zeilen erstellen mit `\\n`",
                        color=nextcord.Color.blurple()
                    )

                case "Tempchannel":
                    embed = nextcord.Embed(
                        description=f"** `⏳`Tempchannel Commands**\n\n> `{prefix}tempchannel set <channel>`\n> <:Reply:1087438925632643082> Setzt ein Tempchannel Sprachkanal\n> `{prefix}tempchannel remove`\n> <:Reply:1087438925632643082> Entfernt den Sprachkanal als Tempchannel\n> `{prefix}tempchannel name <name>`\n> <:Reply:1087438925632643082> Setzt einen neuen standard Namen\n\n> Variablen für den Namen: `{{user}}`, `{{anzahl}}`",
                        color=nextcord.Color.blurple()
                    )

                case "Reaction Roles":
                    embed = nextcord.Embed(
                        description=f"**<:Roles:1087457575257255998> Reactionrole einrichtung**\n\n> `{prefix}rr create <#channel> <messageid> <emote> <@&rolle>`\n> <:Reply:1087438925632643082> Erstellt eine neue Reaction Role\n> `{prefix}rr delete <#channel> <messageid> <emote>`\n> <:Reply:1087438925632643082> Löscht eine bereits vorhandene Reaction Role",
                        color=nextcord.Color.blurple()
                    )

                case "Level System":
                    embed = nextcord.Embed(
                        description="** Level System**\n\n"
                                            f"> `{prefix}level <@user>`\n> <:Reply:1087438925632643082> Zeigt dir dein/das Level eines Users an\n"
                                            f"> `{prefix}leaderboard`\n> <:Reply:1087438925632643082> Zeigt dir die Top 10 User\n\n"
                                            f"> `{prefix}level settings`\n> <:Reply:1087438925632643082> Zeigt dir alle möglichen Einstellungen\n"
                                            f"> `{prefix}level <on | off>`\n> <:Reply:1087438925632643082> Schaltet das Level Sytem an und aus\n"
                                            f"> `{prefix}level xp <anzahl>`\n> <:Reply:1087438925632643082> Setzt eine XP anzahl per Nachricht\n"
                                            f"> `{prefix}level cooldown <sekunden>`\n> <:Reply:1087438925632643082> Setzt den cooldown auf eine bestimmte Zeit\n\n"
                                            f"> `{prefix}level message <text>`\n> <:Reply:1087438925632643082> Setzt die Nachricht für ein Level Up\n"
                                            f"> `{prefix}level message`\n> <:Reply:1087438925632643082> Zeigt dir die aktuelle Level Up Nachricht\n"
                                            f"> `{prefix}level ping <on | off>`\n> <:Reply:1087438925632643082> Schaltet den Ping @ ein und aus bei einem Level Up\n\n"
                                            f"> `{prefix}level custom add <level> <text>`\n> <:Reply:1087438925632643082> Setzt eine custom Nachricht für ein bestimmtes Level\n"
                                            f"> `{prefix}level custom remove <level>`\n> <:Reply:1087438925632643082>` Entfernt eine custom Nachricht für ein bestimmtes Level\n"
                                            f"> `{prefix}level custom show <level>`\n> <:Reply:1087438925632643082> Zeigt dir die custom Nachricht von einem bestimmten Level\n"
                                            f"> `{prefix}level custom show`\n> <:Reply:1087438925632643082> Zeigt dir alle custom Nachrichten\n\n"
                                            f"> `{prefix}level roles add <level> <@rolle>`\n> <:Reply:1087438925632643082> Fügt eine Level Up Rolle zu einem bestimmten Level hinzu\n"
                                            f"> `{prefix}level roles remove <level>`\n> <:Reply:1087438925632643082> Entfernt eine Level Up Rolle von einem bestimmten Level\n"
                                            f"> `{prefix}level roles joinrole add <@rolle>`\n> <:Reply:1087438925632643082> Setzt eine Start Rolle für das Level System die bei dem ersten Level Up wieder weggenommen wird\n"
                                            f"> `{prefix}level roles joinrole remove`\n> <:Reply:1087438925632643082> Entfernt diese Start Rolle wieder\n"
                                            f"> `{prefix}level roles`\n> <:Reply:1087438925632643082> Zeigt alle Level an mit einer Level Up Rolle\n\n"
                                            f"> `{prefix}level blacklist add <@rolle | #channel>`\n> <:Reply:1087438925632643082> Fügt einen Kanal oder eine Rolle der Blacklist hinzu\n"
                                            f"> `{prefix}level blacklist remove <@rolle | #channel>`\n> <:Reply:1087438925632643082> Entfernt eine Rolle oder einen Kanal von der Blacklist\n"
                                            f"> `{prefix}level blacklist`\n> <:Reply:1087438925632643082> Zeigt alle Rollen und Kanäle die auf einer Blacklist stehen\n\n"
                                            f"> `{prefix}level modifylevel add <level> <@user>`\n> <:Reply:1087438925632643082> Füge eine bestimmte anzahl an Leveln einem User hinzu\n"
                                            f"> `{prefix}level modifylevel remove <level> <@user>`\n> <:Reply:1087438925632643082> Entfernte eine bestimmte anzahl an Leveln von einem User\n"
                                            f"> `{prefix}level modifyxp add <xp> <@user>`\n> <:Reply:1087438925632643082> Füge eine bestimmte anzahl an XP einem User hinzu\n"
                                            f"> `{prefix}level modifyxp remove <xp> <@user>`\n> <:Reply:1087438925632643082> Entferne eine bestimmte anzahl an XP von einem User\n\n"
                                            f"> `{prefix}level reset <@user>`\n> <:Reply:1087438925632643082> Setzte einen User komplett zurück\n"
                                            f"> `{prefix}level reset level`\n> <:Reply:1087438925632643082> Setze alle Level zurück\n"
                                            f"> `{prefix}level reset settings`\n> <:Reply:1087438925632643082> Setzte alle Einstellungen zurück\n"
                                            f"> `{prefix}level reset all`\n> <:Reply:1087438925632643082> Setze alles zurück\n\n"
                                            "> Variablen für die Level Up Nachricht:\n"
                                            "> `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{level}`, `{xp_needed}`, `{level_next}` und `{role}` für custom Nachrichten\n\n"
                                            "> Du kannst eine Level Up Nachricht mit mehreren erstellen mit `\\n`\n"
                                            "> Um die Level Up Nachricht zu entfernen füge `off` als Nachricht ein.",
                        color=nextcord.Color.blurple()
                    )

                case "Invite-Logger":
                    embed = nextcord.Embed(
                        description="**📨 Invite-Logger**\n\n> *Soon!*",
                        color=nextcord.Color.blurple()
                    )

                case "Bad Words":
                    embed = nextcord.Embed(
                        description=f"**<:Badword:1087441597622399056> Bad Words**\n\n> `{prefix}badword add <word>`\n> <:Reply:1087438925632643082> Fügt ein Wort der Blacklist hinzu\n> `{prefix}badword remove <word>`\n> <:Reply:1087438925632643082> Entfernt ein Wort von der Blacklist\n> `{prefix}badword show`\n> <:Reply:1087438925632643082> Zeigt dir alle Wörter auf der Blacklist",
                        color=nextcord.Color.blurple()
                    )

                case "Anti Ghostping":
                    embed = nextcord.Embed(
                        description=f"**<:Ghostping:1087448502323384330> Anti-Ghostpings**\n\n> `{prefix}ghostping on`\n> <:Reply:1087438925632643082> Schaltet die Anti Ghostping Erkenn Funktion ein\n> `{prefix}ghostping off`\n> <:Reply:1087438925632643082> Schaltet die Anti Ghostping Erkenn Funktion aus",
                        color=nextcord.Color.blurple()
                    )

                case "Link Blocker":
                    embed = nextcord.Embed(
                        description=f"**<:Automod:1087440612430717068> Link Blocker**\n\n> `{prefix}linkblocker on`\n> <:Reply:1087438925632643082> Schaltet den Linkblocker ein\n> `{prefix}linkblocker off`\n> <:Reply:1087438925632643082> Schaltet den Link Blocker aus",
                        color=nextcord.Color.blurple()
                    )
            
            message = await interaction.message.edit(embed=embed, view=view)
            view.message = message

def setup(bot):
    bot.add_cog(ClassHelp(bot))

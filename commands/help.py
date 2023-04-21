import contextlib
import nextcord
from nextcord.ext import commands

from .utils.embeds import infoEmbed
from .utils.database import readOne
from .utils.language import getLocale, getLanguageStrings, getGuildLanguage

cache = []
prefix = None
languageStrings = {}

class ClassHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def help(self, ctx):
        guildID = ctx.guild.id
        guildLocale = getGuildLanguage(guildID)
        view = HelpButtonView(self.bot, language=guildLocale)
        message = await infoEmbed(self.bot, ctx, getLocale(self.bot, languageStrings, guildLocale, "defaultMenu", self.bot.user.name), view=view)
        global prefix
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[guildID])[0]
        view.message = message
        cache.append(f"{message.id}|{ctx.author.id}")

    @nextcord.slash_command(name="help", description="Shows the help menu", description_localizations={nextcord.Locale.de: "Zeigt das Hilfemenü"})
    async def _help(self, interaction):
        guildLocale = getGuildLanguage(interaction.guild.id)
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[interaction.guild.id])[0]
        await infoEmbed(self, interaction, getLocale(self.bot, languageStrings, guildLocale, "slashHelp", self.bot.user.name, prefix), ephemeral=True)


async def calltimeout(bot, message):
    guildLocale = getGuildLanguage(message.guild.id)

    view = HelpButtonView(bot, guildLocale, True)
    embed = nextcord.Embed(
                description=getLocale(self.bot, languageStrings, guildLocale, "defaultMenu", bot.user.name),
                color=nextcord.Color.blurple()
    )
    message = await message.edit(embed=embed, view=view)
    view.message = message

class HelpButtonView(nextcord.ui.View):
    def __init__(self, bot, language: str, disabled: bool = False, category: str = "categories"):
        super().__init__(timeout=300)
        self.add_item(HelpButton(bot, disabled, category, language=language))
        self.bot = bot
        self.disabled = disabled

    async def on_timeout(self) -> None:
        if self.disabled:
            return
            
        await calltimeout(self.bot, self.message)

class HelpButton(nextcord.ui.Select):
    def __init__(self, bot, disabled: bool, category: str = "categories", language: str = "en"):
        self.bot = bot
        
        categories = getLocale(self.bot, languageStrings, language, "categories")
        general = getLocale(self.bot, languageStrings, language, "general")
        useful = getLocale(self.bot, languageStrings, language, "useful")
        moderation = getLocale(self.bot, languageStrings, language, "moderation")
        fun = getLocale(self.bot, languageStrings, language, "fun")
        welcome = getLocale(self.bot, languageStrings, language, "welcome")
        leave = getLocale(self.bot, languageStrings, language, "leave")
        giveaway = getLocale(self.bot, languageStrings, language, "giveaway")
        ticketsystem = getLocale(self.bot, languageStrings, language, "ticketsystem")
        tempchannel = getLocale(self.bot, languageStrings, language, "tempchannel")
        reactionroles = getLocale(self.bot, languageStrings, language, "reactionroles")
        levelsystem = getLocale(self.bot, languageStrings, language, "levelsystem")
        autoroles = getLocale(self.bot, languageStrings, language, "autoroles")
        invitelogger = getLocale(self.bot, languageStrings, language, "invitelogger")
        badwords = getLocale(self.bot, languageStrings, language, "badwords")
        antighostping = getLocale(self.bot, languageStrings, language, "antighostping")
        linkblocker = getLocale(self.bot, languageStrings, language, "linkblocker")

        options = [
            nextcord.SelectOption(label=categories, emoji="<:Commands:1087442278118871140>", default=category == "categories"),
            nextcord.SelectOption(label=general, emoji="<:Discord:1087443793810301051>", default=category == "general"),
            nextcord.SelectOption(label=useful, emoji="💡", default=category == "useful"),
            nextcord.SelectOption(label=moderation, emoji="<:Moderator:1087456158421352508>", default=category == "moderation"),
            nextcord.SelectOption(label=fun, emoji="<:Fun:1087447621582454926>", default=category == "fun"),
            nextcord.SelectOption(label=welcome, emoji="<:MemberJoin:1087453129198546964>", default=category == "welcome"),
            nextcord.SelectOption(label=leave, emoji="<:MemberLeave:1087453384858157149>", default=category == "leave"),
            nextcord.SelectOption(label=giveaway, emoji="<a:Giveaway:1087437215648456794>", default=category == "giveaway"),
            nextcord.SelectOption(label=ticketsystem, emoji="<:Ticket:1087437978873376798>", default=category == "ticketsystem"),
            nextcord.SelectOption(label=tempchannel, emoji="⏳", default=category == "tempchannel"),
            nextcord.SelectOption(label=reactionroles, emoji="<:Roles:1087457575257255998>", default=category == "reactionroles"),
            nextcord.SelectOption(label=levelsystem, emoji="🌟", default=category == "levelsystem"),
            nextcord.SelectOption(label=autoroles, emoji="<:autoroles:1090725070323859506>", default=category == "autoroles"),
            nextcord.SelectOption(label=invitelogger, emoji="📨", default=category == "invitelogger"),
            nextcord.SelectOption(label=badwords, emoji="<:Badword:1087441597622399056>", default=category == "badwords"),
            nextcord.SelectOption(label=antighostping, emoji="<:Ghostping:1087448502323384330>", default=category == "antighostping"),
            nextcord.SelectOption(label=linkblocker, emoji="<:Automod:1087440612430717068>", default=category == "linkblocker")
        ]

        super().__init__(placeholder=getLocale(self.bot, languageStrings, language, "categoriesPlaceholder"), options=options, disabled=disabled)

    async def callback(self, interaction):
        global languageStrings
        if f"{interaction.message.id}|{interaction.user.id}" not in cache:
            return
        

        guildLocale = getGuildLanguage(interaction.guild.id)

        category = self.values[0].lower()
        if category == getLocale(self.bot, languageStrings, guildLocale, "categories").lower():
            category = "categories"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "general").lower():
            category = "general"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "useful").lower():
            category = "useful"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "moderation").lower():
            category = "moderation"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "fun").lower():
            category = "fun"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "welcome").lower():
            category = "welcome"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "leave").lower():
            category = "leave"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "giveaway").lower():
            category = "giveaway"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "ticketsystem").lower():
            category = "ticketsystem"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "tempchannel").lower():
            category = "tempchannel"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "reactionroles").lower():
            category = "reactionroles"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "levelsystem").lower():
            category = "levelsystem"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "autoroles").lower():
            category = "autoroles"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "invitelogger").lower():
            category = "invitelogger"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "badwords").lower():
            category = "badwords"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "antighostping").lower():
            category = "antighostping"
        elif category == getLocale(self.bot, languageStrings, guildLocale, "linkblocker").lower():
            category = "linkblocker"

        view = HelpButtonView(self.bot, guildLocale, False, category)

        with contextlib.suppress(Exception):
            match category:
                case "categories":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "defaultMenu", self.bot.user.name),
                        color=nextcord.Color.blurple()
                    )

                case "general":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "generalDescription", prefix),
                        color=nextcord.Color.blurple()
                        )

                case "useful":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "usefulDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "moderation":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "moderationDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "fun":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "funDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "welcome":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "welcomeDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "leave":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "leaveDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "giveaway":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "giveawayDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "ticketsystem":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "ticketsystemDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "tempchannel":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "tempchannelDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "reactionroles":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "reactionrolesDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "levelsystem":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "levelsystemDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "autoroles":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "autorolesDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "invitelogger":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "inviteloggerDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "badwords":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "badwordsDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "antighostping":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "antighostpingDescription", prefix),
                        color=nextcord.Color.blurple()
                    )

                case "linkblocker":
                    embed = nextcord.Embed(
                        description=getLocale(self.bot, languageStrings, guildLocale, "linkblockerDescription", prefix),
                        color=nextcord.Color.blurple()
                    )
            
            message = await interaction.message.edit(embed=embed, view=view)
            view.message = message

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("help")
    bot.add_cog(ClassHelp(bot))

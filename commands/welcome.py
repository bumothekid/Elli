import nextcord
import contextlib
import os
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from nextcord import ui, ButtonStyle
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.image import memberCardImageProcessing
from .utils.other import safeDict
from .utils.embeds import infoEmbed, successEmbed, errorEmbed
from .utils.database import readOne, insert, update
from PIL import Image

languageStrings = {}
class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="welcome", aliases=["wel"], invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _welcome(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])[0]
        await infoEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeDescription", prefix))

    @_welcome.group(name="channel", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _channel(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)

    @_channel.command(name="set", aliases=["add", "update"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        guildLocale = getGuildLanguage(ctx.guild.id)
        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is not None:
            message = welcome[2] if welcome[2] is not None else getLocale(self.bot, languageStrings, guildLocale, "welcomeDefaultMessage", "{user_mention}", "{guild_name}", "{guild_membercount}")
            picture = welcome[3] if welcome[3] is not None else "None"
            update(table="welcome", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])


            return await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeChannelSet", ctx.guild.id, channel.id, message, picture))

        insert(table="welcome", columns="guild_id, channel_id, message, picture", values=[ctx.guild.id, channel.id, getLocale(self.bot, languageStrings, guildLocale, "welcomeDefaultMessage", "{user_mention}", "{guild_name}", "{guild_membercount}"), "null"])

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeChannelSet", ctx.guild.id, channel.id, getLocale(self.bot, languageStrings, guildLocale, "welcomeDefaultMessage", "{user_mention}", "{guild_name}", "{guild_membercount}"), "None"))

    @_channel.command(name="remove", aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        channel = readOne(columns="channel_id", table="welcome", where="guild_id", values=[ctx.guild.id])

        if channel is None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeChannelNotSet"))

        update(table="welcome", columns="channel_id", where="guild_id", values=["NULL", ctx.guild.id])

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeChannelRemoved"))
    
    @_welcome.command(name="message", aliases=["text", "msg"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _message(self, ctx, *, message):
        guildLocale = getGuildLanguage(ctx.guild.id)
        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is None or welcome[1] is None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeChannelNotSet"))

        picture = welcome[3] if welcome[3] is not None else "None"
        update(table="welcome", columns="message", where="guild_id", values=[message, ctx.guild.id])

        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeDefaultMessageSet", ctx.guild.id, self.bot.get_channel(welcome[1]).id, message, picture))

    @_welcome.group(name="picture", aliases=["pic", "img"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _picture(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)

    @_picture.command(name="set", aliases=["add", "update", "select"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set2(self, ctx, picture):
        guildLocale = getGuildLanguage(ctx.guild.id)

        if picture not in ["1", "2", "3", "4", "5", "6"]:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomePictureNotValid"))

        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is None or welcome[1] is None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeChannelNotSet"))

        message = welcome[2] if welcome[2] is not None else getLocale(self.bot, languageStrings, guildLocale, "welcomeDefaultMessage", "{user_mention}", "{guild_name}", "{guild_membercount}")
        update(table="welcome", columns="picture", where="guild_id", values=[picture, ctx.guild.id])
        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomePictureSet", ctx.guild.id, self.bot.get_channel(welcome[1]).id, message, picture))
    
    @_picture.command(name="remove", aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove2(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is None or welcome[1] is None:
            return await errorEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomeChannelNotSet"))

        update(table="welcome", columns="picture", where="guild_id", values=["null", ctx.guild.id])
        await successEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomePictureRemoved"))

    @_picture.command(name="show", aliases=["list"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _show(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        
        await infoEmbed(self, ctx, getLocale(self.bot, languageStrings, guildLocale, "welcomePictureShow"), view=ButtonView(self.bot))
    
    @Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[member.guild.id])

        if welcome is None or welcome[1] is None:
            return

        card = None

        if welcome[3] is not None:
            guildLocale = getGuildLanguage(member.guild.id)

            img = await memberCardImageProcessing(member, Image.open(f"assets/welcome/card{welcome[3]}.png"), getLocale(self.bot, languageStrings, guildLocale, "welcomeCardTitle"))
            img.save(f"assets/welcome/user_card{welcome[3]}.png")

            card = nextcord.File(f"assets/welcome/user_card{welcome[3]}.png")
    
        channel = self.bot.get_channel(welcome[1])
        message = welcome[2].replace("\\n", "\n").format_map(safeDict(user_mention=member.mention, user_name=member.name, user_discriminator=member.discriminator, guild_name=member.guild, guild_membercount=member.guild.member_count))

        await channel.send(message, file=card)

        if card is not None:
            with contextlib.suppress(Exception):
                os.remove(f"assets/welcome/user_card{welcome[3]}.png")

class ButtonView(ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=600)
        self.bot = bot

    @ui.button(style=ButtonStyle.primary, label="1", custom_id="welpic1")
    async def _picture1(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/welcome/card1.png"), getLocale(self.bot, languageStrings, guildLocale, "welcomeCardTitle"))
        card.save("assets/welcome/user_card1.png")
        pic = nextcord.File("assets/welcome/user_card1.png")

        embed = nextcord.Embed(
            description=getLocale(self.bot, languageStrings, guildLocale, "welcomePicture", "1"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card1.png")

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="2", custom_id="welpic2")
    async def _picture2(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/welcome/card2.png"), getLocale(self.bot, languageStrings, guildLocale, "welcomeCardTitle"))
        card.save("assets/welcome/user_card2.png")
        pic = nextcord.File("assets/welcome/user_card2.png")

        embed = nextcord.Embed(
            description=getLocale(self.bot, languageStrings, guildLocale, "welcomePicture", "2"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card2.png")

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="3", custom_id="welpic3")
    async def _picture3(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/welcome/card3.png"), getLocale(self.bot, languageStrings, guildLocale, "welcomeCardTitle"))
        card.save("assets/welcome/user_card3.png")
        pic = nextcord.File("assets/welcome/user_card3.png")

        embed = nextcord.Embed(
            description=getLocale(self.bot, languageStrings, guildLocale, "welcomePicture", "3"),
            color=nextcord.Color.blurple(),
        )

        embed.set_image(url="attachment://user_card3.png")

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="4", custom_id="welpic4")
    async def _picture4(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/welcome/card4.png"), getLocale(self.bot, languageStrings, guildLocale, "welcomeCardTitle"))
        card.save("assets/welcome/user_card4.png")
        pic = nextcord.File("assets/welcome/user_card4.png")

        embed = nextcord.Embed(
            description=getLocale(self.bot, languageStrings, guildLocale, "welcomePicture", "4"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card4.png")

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="5", custom_id="welpic5")
    async def _picture5(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/welcome/card5.png"), getLocale(self.bot, languageStrings, guildLocale, "welcomeCardTitle"))
        card.save("assets/welcome/user_card5.png")
        pic = nextcord.File("assets/welcome/user_card5.png")

        embed = nextcord.Embed(
            description=getLocale(self.bot, languageStrings, guildLocale, "welcomePicture", "5"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card5.png")

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="6", custom_id="welpic6")
    async def _picture6(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/welcome/card6.png"), getLocale(self.bot, languageStrings, guildLocale, "welcomeCardTitle"))
        card.save("assets/welcome/user_card6.png")
        pic = nextcord.File("assets/welcome/user_card6.png")

        embed = nextcord.Embed(
            description=getLocale(self.bot, languageStrings, guildLocale, "welcomePicture", "6"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card6.png")

        await ctx.send(embed=embed, file=pic)

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("welcome")
    bot.add_cog(Welcome(bot))

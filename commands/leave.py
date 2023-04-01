import nextcord
import contextlib
import os
from nextcord import ui, ButtonStyle
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.database import readOne, insert, update
from .utils.language import getGuildLanguage, getLanguageStrings, getLocale
from .utils.image import memberCardImageProcessing
from .utils.other import safeDict
from PIL import Image

languageStrings = {}
class Leave(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="leave", invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _leave(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        prefix = readOne(columns="prefix", table="guilds", where="guild_id", values=[ctx.guild.id])[0]

        await infoEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leaveDescription", prefix))

    @_leave.group(name="channel", invoke_without_command=True)
    async def _channel(self, ctx):
        await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")

    @_channel.command(name="set", aliases=["add", "update"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        guildLocale = getGuildLanguage(ctx.guild.id)
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is not None:
            message = leave[2] if leave[2] is not None else getLocale(languageStrings, guildLocale, "leaveDefaultMessage", "{user_name}", "{user_discriminator}"),
            picture = leave[3] if leave[3] is not None else "None"
            update(table="leave", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])

            return await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leaveChannelSet", ctx.guild.id, channel.id, message, picture))

        insert(table="leave", columns="guild_id, channel_id, message, picture", values=[ctx.guild.id, channel.id, getLocale(languageStrings, guildLocale, "leaveDefaultMessage", "{user_name}", "{user_discriminator}"), "null"])

        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leaveChannelSet", ctx.guild.id, channel.id, getLocale(languageStrings, guildLocale, "leaveDefaultMessage", "{user_name}", "{user_discriminator}"), "None"))
    
    @_channel.command(name="remove", aliases=["delete", "del"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "leaveChannelNotSet"))

        update(table="leave", columns="channel_id", where="guild_id", values=["null", ctx.guild.id])

        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leaveChannelRemoved"))

    @_leave.command(name="message", aliases=["msg"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _message(self, ctx, *, message: str):
        guildLocale = getGuildLanguage(ctx.guild.id)
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "leaveChannelNotSet"))

        picture = leave[3] if leave[3] is not None else "None"
        update(table="leave", columns="message", where="guild_id", values=[message, ctx.guild.id])
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leaveMessageSet", ctx.guild.id, leave[1], message, picture))

    @_leave.group(name="picture", aliases=["pic", "img"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _picture(self, ctx):
        raise commands.MissingRequiredArgument(ctx.command)
    
    @_picture.command(name="set", aliases=["add", "update", "select"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set2(self, ctx, picture):
        guildLocale = getGuildLanguage(ctx.guild.id)
        if picture not in ["1", "2", "3", "4", "5", "6"]:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "leavePictureNotValid"))

        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "leaveChannelNotSet"))

        message = leave[2] if leave[2] is not None else "Tschüss {user_name}#{user_discriminator} hoffentlich kommst du bald wieder!"
        update(table="leave", columns="picture", where="guild_id", values=[picture, ctx.guild.id])
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leavePictureSet", ctx.guild.id, leave[1], message, picture))

    @_picture.command(name="remove", aliases=["delete", "del"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove2(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, getLocale(languageStrings, guildLocale, "leaveChannelNotSet"))

        update(table="leave", columns="picture", where="guild_id", values=["null", ctx.guild.id])
        await successEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leavePictureRemoved"))

    @_picture.command(name="show", aliases=["list"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _show(self, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)

        await infoEmbed(self, ctx, getLocale(languageStrings, guildLocale, "leavePictureShow"), view=ButtonView())

    @Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        leave = readOne(columns="*", table="leave", where="guild_id", values=[member.guild.id])

        if leave is None or leave[1] is None:
            return

        card = None

        if leave[3] is not None:
            guildLocale = getGuildLanguage(member.guild.id)
            img = await memberCardImageProcessing(member, Image.open(f"assets/leave/card{leave[3]}.png"), getLocale(languageStrings, guildLocale, "leaveCardTitle"))
            img.save(f"assets/leave/user_card{leave[3]}.png")

            card = nextcord.File(f"assets/leave/user_card{leave[3]}.png")
    
        channel = self.bot.get_channel(leave[1])
        message = leave[2].replace("\\n", "\n").format_map(safeDict(user_mention=member.mention, user_name=member.name, user_discriminator=member.discriminator, guild_name=member.guild, guild_membercount=member.guild.member_count))

        await channel.send(message, file=card)

        if card is not None:
            with contextlib.suppress(Exception):
                os.remove(f"assets/leave/user_card{leave[3]}.png")

class ButtonView(ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    @ui.button(style=ButtonStyle.primary, label="1", custom_id="leavepic1")
    async def _picture1(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card1.png"), getLocale(languageStrings, guildLocale, "leaveCardTitle"))
        card.save("assets/leave/user_card1.png")
        pic = nextcord.File("assets/leave/user_card1.png")

        embed = nextcord.Embed(
            description=getLocale(languageStrings, guildLocale, "leavePictureShow", "1"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card1.png")

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="2", custom_id="leavepic2")
    async def _picture2(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card2.png"), getLocale(languageStrings, guildLocale, "leaveCardTitle"))
        card.save("assets/leave/user_card2.png")
        pic = nextcord.File("assets/leave/user_card2.png")

        embed = nextcord.Embed(
            description=getLocale(languageStrings, guildLocale, "leavePictureShow", "2"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card2.png")

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="3", custom_id="leavepic3")
    async def _picture3(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card3.png"), getLocale(languageStrings, guildLocale, "leaveCardTitle"))
        card.save("assets/leave/user_card3.png")
        pic = nextcord.File("assets/leave/user_card3.png")

        embed = nextcord.Embed(
            description=getLocale(languageStrings, guildLocale, "leavePictureShow", "3"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card3.png")

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="4", custom_id="leavepic4")
    async def _picture4(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card4.png"), getLocale(languageStrings, guildLocale, "leaveCardTitle"))
        card.save("assets/leave/user_card4.png")
        pic = nextcord.File("assets/leave/user_card4.png")

        embed = nextcord.Embed(
            description=getLocale(languageStrings, guildLocale, "leavePictureShow", "4"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card4.png")

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="5", custom_id="leavepic5")
    async def _picture5(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card5.png"), getLocale(languageStrings, guildLocale, "leaveCardTitle"))
        card.save("assets/leave/user_card5.png")
        pic = nextcord.File("assets/leave/user_card5.png")

        embed = nextcord.Embed(
            description=getLocale(languageStrings, guildLocale, "leavePictureShow", "5"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card5.png")

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="6", custom_id="leavepic6")
    async def _picture6(self, _, ctx):
        guildLocale = getGuildLanguage(ctx.guild.id)
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card6.png"), getLocale(languageStrings, guildLocale, "leaveCardTitle"))
        card.save("assets/leave/user_card6.png")
        pic = nextcord.File("assets/leave/user_card6.png")

        embed = nextcord.Embed(
            description=getLocale(languageStrings, guildLocale, "leavePictureShow", "6"),
            color=nextcord.Color.blurple()
        )

        embed.set_image(url="attachment://user_card6.png")

        await ctx.send(embed=embed, file=pic)

def setup(bot):
    global languageStrings
    languageStrings = getLanguageStrings("leave")
    bot.add_cog(Leave(bot))
import nextcord
import contextlib
import os
from nextcord import ui, ButtonStyle
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from .utils.embeds import successEmbed, errorEmbed, infoEmbed
from .utils.database import readOne, insert, update
from .utils.image import memberCardImageProcessing
from .utils.other import safeDict
from PIL import Image

class leave(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="leave", invoke_without_command=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _leave(self, ctx):
        await infoEmbed(self.bot, ctx, "**<:MemberLeave:1087453384858157149> Verlassnachrichten**\n\n> `-leave channel set <#channel>`\n> `-leave channel remove <#channel>`\n> `-leave message <message>`\n> `-leave picture set <picture>`\n> `-leave picture remove`\n> `-leave picture show`\n\n> Variablen für die Verlassnachricht `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{guild_name}`, `{guild_membercount}`\n> Du kannst eine Verlassnachricht mit mehreren Zeilen erstellen mit `\\n`\n> Um die Verlassnachricht ganz zu entfernen füge `_ _` als Nachricht ein")

    @_leave.group(name="channel", invoke_without_command=True)
    async def _channel(self, ctx):
        await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")

    @_channel.command(name="set", aliases=["add", "update"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is not None:
            message = leave[2] if leave[2] is not None else "Tschüss {user_name}#{user_discriminator} hoffentlich kommst du bald wieder!"
            picture = leave[3] if leave[3] is not None else "Keins"
            update(table="leave", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])

            return await successEmbed(self, ctx, f"**<:MemberLeave:1087453384858157149> Verlasskanal aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** {message}\n> **Bild:** `{picture}`")

        insert(table="leave", columns="guild_id, channel_id, message, picture", values=[ctx.guild.id, channel.id, "Tschüss {user_name}#{user_discriminator} hoffentlich kommst du bald wieder!", "null"])

        await successEmbed(self, ctx, f"**<:MemberLeave:1087453384858157149> Verlasskanal gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Tschüss {{user_name}}#{{user_discriminator}} hoffentlich kommst du bald wieder!\n> **Bild:** `Keins`")
    
    @_channel.command(name="remove", aliases=["delete", "del"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove(self, ctx):
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, "Es ist kein Verlasskanal gesetzt.")

        update(table="leave", columns="channel_id", where="guild_id", values=["null", ctx.guild.id])

        await successEmbed(self, ctx, "**<:MemberLeave:1087453384858157149> Verlasskanal zurückgesetzt**")

    @_leave.command(name="message", aliases=["msg"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _message(self, ctx, *, message: str):
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, "Es ist kein Verlasskanal gesetzt.")

        picture = leave[3] if leave[3] is not None else "Keins"
        update(table="leave", columns="message", where="guild_id", values=[message, ctx.guild.id])
        await successEmbed(self, ctx, f"**<:MemberLeave:1087453384858157149> Verlassnachricht aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(leave[1]).id}/)\n> **Nachricht:** {message}\n> **Bild:** `{picture}`")

    @_leave.group(name="picture", aliases=["pic", "img"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _picture(self, ctx):
        await errorEmbed(self.bot, ctx, "Es fehlt ein benötigtes Argument.")
    
    @_picture.command(name="set", aliases=["add", "update", "select"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _set2(self, ctx, picture):
        if picture not in ["1", "2", "3", "4", "5", "6"]:
            return await errorEmbed(self.bot, ctx, "Es ist kein Bild mit dieser Nummer vorhanden. <1-6>")

        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, "Es ist kein Verlasskanal gesetzt.")

        message = leave[2] if leave[2] is not None else "Tschüss {user_name}#{user_discriminator} hoffentlich kommst du bald wieder!"
        update(table="leave", columns="picture", where="guild_id", values=[picture, ctx.guild.id])
        await successEmbed(self, ctx, f"**<:MemberLeave:1087453384858157149> Verlassbild aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(leave[1]).id}/)\n> **Nachricht:** {message}\n> **Bild:** `{picture}`")

    @_picture.command(name="remove", aliases=["delete", "del"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _remove2(self, ctx):
        leave = readOne(columns="*", table="leave", where="guild_id", values=[ctx.guild.id])

        if leave is None or leave[1] is None:
            return await errorEmbed(self.bot, ctx, "Es ist kein Verlasskanal gesetzt.")

        update(table="leave", columns="picture", where="guild_id", values=["null", ctx.guild.id])
        await successEmbed(self, ctx, "**<:MemberLeave:1087453384858157149> Verlassbild zurückgesetzt**")

    @_picture.command(name="show", aliases=["list"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def _show(self, ctx):
        await infoEmbed(self, ctx, "**<:MemberLeave:1087453384858157149> Verlassbilder**\n\n> **Du kannst dir die Bilder anschauen mit den jeweiligen Knöpfen**", view=ButtonView())

    @Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        leave = readOne(columns="*", table="leave", where="guild_id", values=[member.guild.id])

        if leave is None or leave[1] is None:
            return

        card = None

        if leave[3] is not None:
            img = await memberCardImageProcessing(member, Image.open(f"assets/leave/card{leave[3]}.png"), "Tschüss!")
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

    @ui.button(style=ButtonStyle.primary, label="Bild 1", custom_id="leavepic1")
    async def _picture1(self, _, ctx):
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card1.png"), "Tschüss!")
        card.save("assets/leave/user_card1.png")
        pic = nextcord.File("assets/leave/user_card1.png")

        embed = nextcord.Embed(
            description="**Bild 1**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="Bild 2", custom_id="leavepic2")
    async def _picture2(self, _, ctx):
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card2.png"), "Tschüss!")
        card.save("assets/leave/user_card2.png")
        pic = nextcord.File("assets/leave/user_card2.png")

        embed = nextcord.Embed(
            description="**Bild 2**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="Bild 3", custom_id="leavepic3")
    async def _picture3(self, _, ctx):
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card3.png"), "Tschüss!")
        card.save("assets/leave/user_card3.png")
        pic = nextcord.File("assets/leave/user_card3.png")

        embed = nextcord.Embed(
            description="**Bild 3**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="Bild 4", custom_id="leavepic4")
    async def _picture4(self, _, ctx):
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card4.png"), "Tschüss!")
        card.save("assets/leave/user_card4.png")
        pic = nextcord.File("assets/leave/user_card4.png")

        embed = nextcord.Embed(
            description="**Bild 4**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="Bild 5", custom_id="leavepic5")
    async def _picture5(self, _, ctx):
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card5.png"), "Tschüss!")
        card.save("assets/leave/user_card5.png")
        pic = nextcord.File("assets/leave/user_card5.png")

        embed = nextcord.Embed(
            description="**Bild 5**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="Bild 6", custom_id="leavepic6")
    async def _picture6(self, _, ctx):
        card = await memberCardImageProcessing(ctx.user, Image.open("assets/leave/card6.png"), "Tschüss!")
        card.save("assets/leave/user_card6.png")
        pic = nextcord.File("assets/leave/user_card6.png")

        embed = nextcord.Embed(
            description="**Bild 6**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

def setup(bot):
    bot.add_cog(leave(bot))
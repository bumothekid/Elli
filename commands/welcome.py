import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from nextcord import ui, ButtonStyle
from .utils.image import welcomeImageProcessing
from .utils.other import safeDict
from .utils.embeds import infoEmbed, successEmbed, errorEmbed
from .utils.database import readOne, insert, update
from PIL import Image

class welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="welcome", aliases=["wel"], invoke_without_command=True)
    async def _welcome(self, ctx):
        await infoEmbed(self, ctx, "**<:icon_member_joined:965033605707481128> Willkommensnachrichten**\n\n`-welcome channel set <#channel>`\n`-welcome channel remove <#channel>`\n`-welcome message <message>`\n`-welcome picture set <picture>`\n`-welcome picture remove`\n`-welcome picture show`\n\n> Variablen für die Willkommensnachricht `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{guild_name}`, `{guild_membercount}`\n> Du kannst eine Willkommensnachricht mit mehreren Zeilen erstellen mit `\\n`\n> Um die Willkommensnachricht ganz zu entfernen füge `_ _` als Nachricht ein")

    @_welcome.group(name="channel", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _channel(self, ctx):
        await errorEmbed(self, ctx, "Es fehlt ein benötigtes Argument.")

    @_channel.command(name="set", aliases=["add", "update"])
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is not None:
            message = welcome[2] if welcome[2] is not None else "Willkommen auf {guild_name} {user_mention},\\n du bist unser `{guild_membercount}`tes Mitglied!"
            picture = welcome[3] if welcome[3] is not None else "Keins"
            update(table="welcome", columns="channel_id", where="guild_id", values=[channel.id, ctx.guild.id])

            return await successEmbed(self, ctx, f"**<:icon_member_joined:965033605707481128> Willkommenskanal aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** {message}\n> **Bild:** `{picture}`")

        insert(table="welcome", columns="guild_id, channel_id, message, picture", values=[ctx.guild.id, channel.id, "Willkommen auf {guild_name} {user_mention},\\n du bist unser `{guild_membercount}`tes Mitglied!", "null"])

        await successEmbed(self, ctx, f"**<:icon_member_joined:965033605707481128> Willkommenskanal gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Willkommen auf {{guild_name}} {{user_mention}},\\n du bist unser `{{guild_membercount}}`tes Mitglied!\n> **Bild:** `Keins`")

    @_channel.command(name="remove", aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    async def _remove(self, ctx):
        channel = readOne(columns="channel_id", table="welcome", where="guild_id", values=[ctx.guild.id])

        if channel is None:
            return await errorEmbed(self, ctx, "Es ist kein Willkommenskanal gesetzt.")

        update(table="welcome", columns="channel_id", where="guild_id", values=["NULL", ctx.guild.id])

        await successEmbed(self, ctx, "**<:icon_member_joined:965033605707481128> Willkommenskanal zurückgesetzt**")
    
    @_welcome.command(name="message", aliases=["text"])
    @commands.has_permissions(manage_guild=True)
    async def _message(self, ctx, *, message):
        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is None or welcome[1] is None:
            return await errorEmbed(self, ctx, "Es ist kein Willkommenskanal gesetzt.")

        picture = welcome[3] if welcome[3] is not None else "Keins"
        update(table="welcome", columns="message", where="guild_id", values=[message, ctx.guild.id])
        await successEmbed(self, ctx, f"**<:icon_member_joined:965033605707481128> Willkommensnachricht gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(welcome[1]).id}/)\n> **Nachricht:** {message}\n> **Bild:** `{picture}`")

    @_welcome.group(name="picture", aliases=["pic"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _picture(self, ctx):
        await errorEmbed(self, ctx, "Es fehlt ein benötigtes Argument.")

    @_picture.command(name="set", aliases=["add", "update", "select"])
    @commands.has_permissions(manage_guild=True)
    async def _set2(self, ctx, picture):
        if picture not in ["1", "2", "3", "4", "5", "6"]:
            await errorEmbed(self, ctx, "Ungültiges Bild**\n**Gültige Bilder `<1 | 2 | 3 | 4 | 5 | 6>`")

        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is None or welcome[1] is None:
            return await errorEmbed(self, ctx, "Es ist kein Willkommenskanal gesetzt.")

        update(table="welcome", columns="picture", where="guild_id", values=[picture, ctx.guild.id])
        await successEmbed(self, ctx, f"**<:icon_member_joined:965033605707481128> Willkommensnachricht gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(welcome[1]).id}/)\n> **Nachricht:** {welcome[2]}\n> **Bild:** `{picture}`")
    
    @_picture.command(name="remove", aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    async def _remove2(self, ctx):
        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[ctx.guild.id])

        if welcome is None or welcome[1] is None:
            return await errorEmbed(self, ctx, "Es ist kein Willkommenskanal gesetzt.")

        update(table="welcome", columns="picture", where="guild_id", values=["null", ctx.guild.id])
        await successEmbed(self, ctx, "**<:icon_member_joined:965033605707481128> Willkommensbild zurückgesetzt**")

    @_picture.command(name="show", aliases=["list"])
    @commands.has_permissions(manage_guild=True)
    async def _show(self, ctx):
        await infoEmbed(self, ctx, "**<:icon_member_joined:965033605707481128> Willkommensbilder**\n\n> Du kannst dir die Bilder anschauen mit den jeweiligen Buttons", view=ButtonView())
    
    @Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        welcome = readOne(columns="*", table="welcome", where="guild_id", values=[member.guild.id])

        if welcome is None or welcome[1] is None:
            return

        card = None

        if welcome[3] is not None:
            img = await welcomeImageProcessing(member, Image.open(f"assets/welcome/card{welcome[3]}.png"))
            img.save(f"assets/welcome/user_card{welcome[3]}.png")

            card = nextcord.File(f"assets/welcome/user_card{welcome[3]}.png")
    
        channel = self.bot.get_channel(welcome[1])
        message = welcome[2].replace("\\n", "\n").format_map(safeDict(user_mention=member.mention, user_name=member.name, user_discriminator=member.discriminator, guild_name=member.guild, guild_membercount=member.guild.member_count))

        await channel.send(message, file=card)

class ButtonView(ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    @ui.button(style=ButtonStyle.primary, label="Bild 1", custom_id="welpic1")
    async def _picture1(self, _, ctx):
        card = await welcomeImageProcessing(ctx, Image.open("assets/welcome/card1.png"))
        card.save("assets/welcome/user_card1.png")
        pic = nextcord.File("assets/welcome/user_card1.png")

        embed = nextcord.Embed(
            description="**Bild 1**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="Bild 2", custom_id="welpic2")
    async def _picture2(self, _, ctx):
        card = await welcomeImageProcessing(ctx, Image.open("assets/welcome/card2.png"))
        card.save("assets/welcome/user_card2.png")
        pic = nextcord.File("assets/welcome/user_card2.png")

        embed = nextcord.Embed(
            description="**Bild 2**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="Bild 3", custom_id="welpic3")
    async def _picture3(self, _, ctx):
        card = await welcomeImageProcessing(ctx, Image.open("assets/welcome/card3.png"))
        card.save("assets/welcome/user_card3.png")
        pic = nextcord.File("assets/welcome/user_card3.png")

        embed = nextcord.Embed(
            description="**Bild 3**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="Bild 4", custom_id="welpic4")
    async def _picture4(self, _, ctx):
        card = await welcomeImageProcessing(ctx, Image.open("assets/welcome/card4.png"))
        card.save("assets/welcome/user_card4.png")
        pic = nextcord.File("assets/welcome/user_card4.png")

        embed = nextcord.Embed(
            description="**Bild 4**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="Bild 5", custom_id="welpic5")
    async def _picture5(self, _, ctx):
        card = await welcomeImageProcessing(ctx, Image.open("assets/welcome/card5.png"))
        card.save("assets/welcome/user_card5.png")
        pic = nextcord.File("assets/welcome/user_card5.png")

        embed = nextcord.Embed(
            description="**Bild 5**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

    @ui.button(style=ButtonStyle.primary, label="Bild 6", custom_id="welpic6")
    async def _picture6(self, _, ctx):
        card = await welcomeImageProcessing(ctx, Image.open("assets/welcome/card6.png"))
        card.save("assets/welcome/user_card6.png")
        pic = nextcord.File("assets/welcome/user_card6.png")

        embed = nextcord.Embed(
            description="**Bild 6**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

def setup(bot):
    bot.add_cog(welcome(bot))

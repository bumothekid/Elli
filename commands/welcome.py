import sqlite3
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from nextcord import ui, ButtonStyle
from .utils.utils import safeDict, welcomeImageProcessing
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from io import BytesIO

class welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="welcome", aliases=["wel"], invoke_without_command=True)
    async def _welcome(self, ctx):
        embed = nextcord.Embed(
            description="**<:icon_member_joined:965033605707481128> Willkommensnachrichten**\n\n`-welcome channel set <#channel>`\n`-welcome channel remove <#channel>`\n`-welcome message <message>`\n`-welcome picture set <picture>`\n`-welcome picture remove`\n`-welcome picture show`\n\n> Variablen für die Willkommensnachricht `{user_mention}`, `{user_name}`, `{user_discriminator}`, `{guild_name}`, `{guild_membercount}`\n> Du kannst eine Willkommensnachricht mit mehreren Zeilen erstellen mit `\\n`",
            color=nextcord.Color.blurple()
        )

        await ctx.reply(embed=embed)

    @_welcome.group(name="channel", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _channel(self, ctx):
        embed = nextcord.Embed(
            description="**Es fehlt ein benötigtes Argument.**",
            color=nextcord.Color.dark_red()
        )

        await ctx.reply(embed=embed)

    @_channel.command(name="set", aliases=["add", "update"])
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx, channel: nextcord.TextChannel):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        welcome = c.fetchone()

        if welcome is not None:
            picture = welcome[3] if welcome[3] is not None else "Keins"
            c.execute("UPDATE welcome SET channel_id = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
            db.commit()

            embed = nextcord.Embed(
                description=f"**<:icon_member_joined:965033605707481128> Willkommenskanal aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Willkommen auf guild_name, user_mention!\n> **Bild:** `{picture}`",
                color=nextcord.Color.dark_green()
            )

            return await ctx.reply(embed=embed)

        c.execute("INSERT INTO welcome(guild_id, channel_id, message, picture) VALUES(?,?,?, NULL)", [ctx.guild.id, channel.id, "Willkommen auf guild_name, user_mention!"])
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:icon_member_joined:965033605707481128> Willkommenskanal gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Willkommen auf guild_name, user_mention!\n> **Bild:** `Keins`",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_channel.command(name="remove", aliases=["delete", "reset"])
    @commands.has_permissions(manage_guild=True)
    async def _remove(self, ctx):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT channel_id FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        channel = c.fetchone()

        if channel is None:
            embed = nextcord.Embed(
                description="**Es ist kein Willkommenskanal gesetzt**",
                color=nextcord.Color.dark_red()
            )

            return ctx.reply(embed=embed)

        c.execute("UPDATE welcome SET channel_id = NULL WHERE guild_id = ?", [ctx.guild.id])
        db.commit()

        embed = nextcord.Embed(
            description="**<:icon_member_joined:965033605707481128> Willkommenskanal zurückgesetzt**",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)
    
    @_welcome.command(name="message", aliases=["text"])
    @commands.has_permissions(manage_guild=True)
    async def _message(self, ctx, *, message):
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        welcome = c.fetchone()

        if welcome is None or welcome[1] is None:
            embed = nextcord.Embed(
                description="**Es ist kein Willkommenskanal gesetzt**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        picture = welcome[3] if welcome[3] is not None else "Keins"
        c.execute("UPDATE welcome SET message = ? WHERE guild_id = ?", [message, ctx.guild.id])
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:icon_member_joined:965033605707481128> Willkommensnachricht gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(welcome[1]).id}/)\n> **Nachricht:** {message}\n> **Bild:** {picture}",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_welcome.group(name="picture", aliases=["pic"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def _picture(self, ctx):
        embed = nextcord.Embed(
            description="**Es fehlt ein benötigtes Argument.**", 
            color=nextcord.Color.dark_red()
        )

        await ctx.reply(embed=embed)

    @_picture.command(name="set", aliases=["add", "update", "select"])
    @commands.has_permissions(manage_guild=True)
    async def _set2(self, ctx, picture):
        if picture not in ["1", "2", "3", "4", "5", "6"]:
            embed = nextcord.Embed(
                description="**Ungültiges Bild**\n**Gültige Bilder `<1 | 2 | 3 | 4 | 5 | 6>`**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)
        
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        welcome = c.fetchone()

        if welcome is None:
            embed = nextcord.Embed(
                description="**Es ist kein Willkommenskanal gesetzt**",
                color=nextcord.Color.dark_red()
            )

            return await ctx.reply(embed=embed)

        c.execute("UPDATE welcome SET picture = ? WHERE guild_id = ?", (picture, ctx.guild.id))
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:icon_member_joined:965033605707481128> Willkommensnachricht gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(welcome[1]).id}/)\n> **Nachricht:** {welcome[2]}\n> **Bild:** {picture}",
            color=nextcord.Color.dark_green()
        )

        await ctx.reply(embed=embed)

    @_picture.command(name="show", aliases=["list"])
    @commands.has_permissions(manage_guild=True)
    async def _show(self, ctx):
        embed = nextcord.Embed(
            description="**<:icon_member_joined:965033605707481128> Willkommensbilder**\n\n> Du kannst dir die Bilder anschauen mit den jeweiligen Buttons",
            color=nextcord.Color.blurple()
        )
        await ctx.reply(embed=embed, view=ButtonView())
    
    # @Cog.listener()
    # async def on_member_join(self, member):
    @commands.command(name="join")
    async def _join(self, ctx):
        member = ctx.author
        if member.bot:
            return
        
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM welcome WHERE guild_id = ?", [member.guild.id])
        welcome = c.fetchone()

        if welcome is None or welcome[1] is None:
            return

        card = None

        if welcome[3] is not None:
            img = await welcomeImageProcessing(member, Image.open(f"assets/welcome/card{welcome[3]}.png"))
            img.save(f"assets/welcome/user_card{welcome[3]}.png")

            card = nextcord.File(f"assets/welcome/user_card{welcome[3]}.png")
            print("a")
    
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

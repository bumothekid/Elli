import sqlite3
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from nextcord import ui, ButtonStyle
from .utils.utils import safeDict
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from io import BytesIO

class welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="welcome", aliases=["wel"], invoke_without_command=True)
    async def _welcome(self, ctx):
        # TODO: Add pictures commands to overview command
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

        c.execute("SELECT channel_id FROM welcome WHERE guild_id = ?", [ctx.guild.id])
        channel_id = c.fetchone()

        if channel_id is not None:
            c.execute("UPDATE welcome SET channel_id = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
            db.commit()

            embed = nextcord.Embed(
                description=f"**<:icon_member_joined:965033605707481128> Willkommenskanal aktualisiert**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Willkommen auf guild_name, user_mention!",
                color=nextcord.Color.dark_green()
            )

            return await ctx.reply(embed=embed)

        c.execute("INSERT INTO welcome(guild_id, channel_id, message, picture) VALUES(?,?,?, NULL)", [ctx.guild.id, channel.id, "Willkommen auf guild_name, user_mention!"])
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:icon_member_joined:965033605707481128> Willkommenskanal gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/)\n> **Nachricht:** Willkommen auf guild_name, user_mention!",
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

        c.execute("UPDATE welcome SET message = ? WHERE guild_id = ?", [message, ctx.guild.id])
        db.commit()

        embed = nextcord.Embed(
            description=f"**<:icon_member_joined:965033605707481128> Willkommensnachricht gesetzt**\n\n> **Kanal:** [`📎`Link](https://discord.com/channels/{ctx.guild.id}/{self.bot.get_channel(welcome[1]).id}/)\n> **Nachricht:** {message}",
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

    @_picture.command(name="show", aliases=["list"])
    async def _show(self, ctx):
        embed = nextcord.Embed(
            description="**<:icon_member_joined:965033605707481128> Willkommensbilder**\n\n> Du kannst dir die Bilder anschauen mit den jeweiligen Buttons",
            color=nextcord.Color.blurple()
        )
        await ctx.reply(embed=embed, view=ButtonView())
    
    @Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        
        db = sqlite3.connect("database.db")
        c = db.cursor()

        c.execute("SELECT * FROM welcome WHERE guild_id = ?", [member.guild.id])
        welcome = c.fetchone()

        if welcome is None or welcome[1] is None:
            return
    
        channel = self.bot.get_channel(welcome[1])
        message = welcome[2].replace("\\n", "\n").format_map(safeDict(user_mention=member.mention, user_name=member.name, user_discriminator=member.discriminator, guild_name=member.guild, guild_membercount=member.guild.member_count))

        await channel.send(message)

class ButtonView(ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    @ui.button(style=ButtonStyle.primary, label="Bild 1", custom_id="welpic1")
    async def _picture1(self, _, ctx):
        # card1 = Image.open("assets/welcome/card1.png")
        # corner = add_corners(card1, 5)
        # corner.save("assets/welcome/card1.png")

        card = Image.open("assets/welcome/card1.png")
        draw = ImageDraw.Draw(card)
        primaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Regular.otf", 64)
        secondaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Regular.otf", 46)

        buffer_avatar = BytesIO(await ctx.user.display_avatar.replace(format="png", size=128).read())
        avatar = Image.open(buffer_avatar).resize((225, 225))
        avatar = add_corners(avatar, 8)
        # avatar = dropShadow(avatar, shadow=(0x00, 0x00, 0x00, 0xff))
        _, bg_h = card.size
        offset = (20, (bg_h - 225) // 2)
        card.paste(avatar, offset, avatar)
        draw.text((360, 80), "Willkommen!", (255, 255, 255), font=primaryFont)
        draw.text((440, 160), f"{ctx.user.name}", (255, 255, 255), font=secondaryFont)
        card.save("assets/welcome/user_card1.png")

        pic = nextcord.File("assets/welcome/user_card1.png")

        embed = nextcord.Embed(
            description="**Bild 1**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)
    
    @ui.button(style=ButtonStyle.primary, label="Bild 2", custom_id="welpic2")
    async def _picture2(self, _, ctx):
        # card1 = Image.open("assets/welcome/card2.png")
        # corner = add_corners(card1, 5)
        # corner.save("assets/welcome/card2.png")

        card = Image.open("assets/welcome/card2.png")
        draw = ImageDraw.Draw(card)
        primaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Regular.otf", 64)
        secondaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Regular.otf", 46)

        buffer_avatar = BytesIO(await ctx.user.display_avatar.replace(format="png", size=128).read())
        avatar = Image.open(buffer_avatar).resize((225, 225))
        avatar = add_corners(avatar, 8)
        # avatar = dropShadow(avatar, shadow=(0x00, 0x00, 0x00, 0xff))
        _, bg_h = card.size
        offset = (20, (bg_h - 225) // 2)
        card.paste(avatar, offset, avatar)
        draw.text((360, 80), "Willkommen!", (255, 255, 255), font=primaryFont)
        draw.text((440, 160), f"{ctx.user.name}", (255, 255, 255), font=secondaryFont)
        card.save("assets/welcome/user_card2.png")

        pic = nextcord.File("assets/welcome/user_card2.png")

        embed = nextcord.Embed(
            description="**Bild 2**",
            color=nextcord.Color.blurple()
        )

        await ctx.send(embed=embed, file=pic)

def add_corners(image, radius):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', image.size, 255)
    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    image.putalpha(alpha)
    return image

# def dropShadow( image, offset=(5,5), background=0xffffff, shadow=0x444444, 
#                 border=8, iterations=3):
#   totalWidth = image.size[0] + abs(offset[0]) + 2*border
#   totalHeight = image.size[1] + abs(offset[1]) + 2*border
#   back = Image.new(image.mode, (totalWidth, totalHeight), background)
#   shadowLeft = border + max(offset[0], 0)
#   shadowTop = border + max(offset[1], 0)
#   back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], 
#     shadowTop + image.size[1]] )
#   n = 0
#   while n < iterations:
#     back = back.filter(ImageFilter.BLUR)
#     n += 1

#   imageLeft = border - min(offset[0], 0)
#   imageTop = border - min(offset[1], 0)
#   back.paste(image, (imageLeft, imageTop))

#   return back

def setup(bot):
    bot.add_cog(welcome(bot))

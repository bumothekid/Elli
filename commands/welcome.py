import nextcord
import sqlite3
from nextcord.ext import commands
from json import load, dump
from requests import get
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # with open("data/welcome.json", encoding="utf-8") as f:
        #     welcome_data = load(f)
        
        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT channel_id FROM welcome WHERE guild_id = '{member.guild.id}'")
        channel_id = c.fetchone()

        # if welcome_data.get(str(member.guild.id)):
        if channel_id is not None:
            welcome = Image.open("assets/welcome/default.jpg")
            avatar = Image.open(BytesIO(get(member.avatar.url).content)).resize((275, 275))

            mask = Image.new("L", avatar.size)
            ImageDraw.Draw(mask).ellipse((0, 0, 275, 275), fill=255)

            ImageDraw.Draw(welcome).text((40, 80), f"Willkommen\n{member.name}",
                                         font=ImageFont.truetype("arial.ttf", size=100),
                                         align="center", stroke_width=4, stroke_fill="black")

            welcome.paste(avatar, (660, 60), mask)
            welcome.save("assets/welcome/done.jpg")

            embed = nextcord.Embed(
                title=":dizzy: Ein neues Mitglied erscheint!",
                color=0x6850be)

            embed.set_footer(text=f"{member} | {member.id}")
            embed.set_image(url="attachment://done.jpg")

            # channel = self.client.get_channel(welcome_data[str(member.guild.id)]["channel_id"])
            channel = self.client.get_channel(channel_id[0])
            await channel.send(embed=embed, file=nextcord.File("assets/welcome/done.jpg"))

    @commands.command(aliases=["welcomeset"])
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def setwelcome(self, ctx, channel: nextcord.abc.GuildChannel):
        # with open("data/welcome.json", encoding="utf-8") as f:
        #     welcome_data = load(f)

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT channel_id FROM welcome WHERE guild_id = '{ctx.guild.id}'")
        exists = await c.fetchone()

        if exists is None:
        # if not welcome_data.get(str(ctx.guild.id)):
        #     welcome_data[str(ctx.guild.id)] = {}
        #     welcome_data[str(ctx.guild.id)]["channel_id"] = channel.id


            # with open("data/welcome.json", "w") as f:
            #     dump(welcome_data, f, indent=4)

            c.execute("INSERT INTO welcome(guild_id, channel_id) VALUES(?, ?)", [ctx.guild.id, channel.id])

            embed = nextcord.Embed(
                description=f"Der Willkommenskanal wurde erfolgreich in {channel.mention} gesetzt!",
                color=nextcord.Color.dark_green())

            await ctx.reply(embed=embed, mention_author=False)

            db.commit()
        else:
            embed = nextcord.Embed(
                description="Bitte entferne erst den aktuellen Willkommenskanal!",
                color=nextcord.Color.red())

            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["welcomeremove"])
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def removewelcome(self, ctx):
        # with open("data/welcome.json", encoding="utf-8") as f:
        #     welcome_data = load(f)

        db = sqlite3.connect("database.db")
        c = db.cursor()
        c.execute(f"SELECT channel_id FROM welcome WHERE guild_id = '{ctx.guild.id}'")
        exists = await c.fetchone()

        if exists is not None:
        # if welcome_data.get(str(ctx.guild.id)):
        #     del welcome_data[str(ctx.guild.id)]

            # with open("data/welcome.json", "w") as f:nm
            #     dump(welcome_data, f, indent=4)

            c.execute(f"DELETE FROM welcome WHERE guild_id = '{ctx.guild.id}'")

            embed = nextcord.Embed(
                description=f"Der Willkommenskanal wurde erfolgreich zurückgesetzt!",
                color=nextcord.Color.dark_green())

            await ctx.reply(embed=embed, mention_author=False)

            db.commit()
        else:
            embed = nextcord.Embed(
                description="Momentan ist kein Willkommenskanal gesetzt!",
                color=nextcord.Color.red())

            await ctx.reply(embed=embed, mention_author=False)

def setup(client):
    client.add_cog(Welcome(client))

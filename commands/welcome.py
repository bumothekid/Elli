import nextcord
from nextcord.ext import commands
from requests import get
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        embed = nextcord.Embed(
            description=f"{member} rara",
            colour=nextcord.Colour.dark_blue())

        await self.bot.get_channel(957421116262072370).send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("ddd"):

            # gettet das welcome-image und den user-avatar
            welcome = Image.open("assets/welcome/welcome.jpg")
            avatar = Image.open(BytesIO(get(message.author.avatar.url).content)).resize((75, 75))

            # bringt den user-avatar in die runde form
            mask = Image.new("L", avatar.size)
            ImageDraw.Draw(mask).ellipse((0, 0, 75, 75), fill=255)

            # packt text auf das welcome-image
            ImageDraw.Draw(welcome).text((20, 20), f"WASSER!\n{message.author.name}",
            font=ImageFont.truetype("Arial.ttf", size=25), align="center" , stroke_width=4, stroke_fill="black")

            # klatscht den avatar drauf und speichert das ganze
            welcome.paste(avatar, (160, 10), mask)
            welcome.save("assets/welcome/welcome_done.jpg")

            embed = nextcord.Embed(
                title=f"{message.author} IST WASSER!",
                colour=nextcord.Colour.dark_blue())

            embed.set_image(url="attachment://welcome_done.jpg")

            await self.bot.get_channel(957421116262072370).send(embed=embed, 
            file=nextcord.File("assets/welcome/welcome_done.jpg"))

def setup(bot):
    bot.add_cog(welcome(bot))